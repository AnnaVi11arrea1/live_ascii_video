"""
Session - Main coordinator that integrates all components
"""
import threading
import time
import re
import subprocess
import platform
from video_capture import VideoCapture
from ascii_converter import AsciiConverter
from network import NetworkConnection, NetworkServer
from terminal_ui import TerminalUI, InputHandler
from sound_manager import SoundManager


class ChatSession:
    """Coordinates video chat session with all components."""
    
    def __init__(self, mode='host', host='0.0.0.0', port=5000, 
                remote_host=None, ascii_width=None, device_id=0, color_mode="rainbow", 
                user_name="You", chat_color="white", theme_color="green"):
        """
        Initialize chat session.
        
        Args:
            mode: 'host' or 'connect'
            host: Host address (for server binding or client connection)
            port: Port number
            remote_host: Remote host IP (for connect mode)
            ascii_width: Width of ASCII art in characters (None = auto-detect from terminal)
            device_id: Camera device ID
            color_mode: Color mode - "rainbow", "bw", or "normal"
            user_name: Display name for this user
            chat_color: Color for chat messages
            theme_color: Theme color for video frame
        """
        self.mode = mode
        self.host = host
        self.port = port
        self.remote_host = remote_host
        self.device_id = device_id
        self.color_mode = color_mode
        self.user_name = user_name
        self.chat_color = chat_color
        self.theme_color = theme_color
        
        # Remote user info
        self.remote_name = "Remote"
        self.remote_chat_color = "white"
        self.remote_theme_color = "blue"
        
        # Components - resolution preserved, aspect calculated from image
        self.video_capture = None
        
        # Create UI first to get terminal dimensions
        self.ui = TerminalUI(user_name=user_name, theme_color=theme_color)
        
        # Auto-detect width from terminal if not specified
        if ascii_width is None:
            # Use the video_width from UI (which is half the terminal minus divider)
            ascii_width = max(50, (self.ui.term.width - 3) // 2)
        
        self.ascii_converter = AsciiConverter(width=ascii_width, char_set="simple", 
                                            color_mode=color_mode)
        self.network = None
        self.server = None
        self.input_handler = None
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Sound and camera state
        self.muted = False
        self.camera_enabled = True
        
        # State
        self.running = False
        self.connected = False
        
        # Threads
        self.capture_thread = None
        self.receive_thread = None
        
        # Stats
        self.local_frame_count = 0
        self.remote_frame_count = 0
        self.last_stats_time = time.time()
        self.local_fps = 0
        self.remote_fps = 0
    
    def start(self):
        """Start the chat session."""
        self.running = True
        
        try:
            # Initialize UI
            self.ui.set_status("Starting up...")
            self.ui.start()
            
            # Play startup sound
            self.sound_manager.play_startup_sound()
            
            # Now that UI is started, update converter width to match terminal
            optimal_width = self.ui.video_width
            self.ascii_converter.set_width(optimal_width)
            self.ui.add_message(f"System: ASCII width set to {optimal_width} chars")
            self.ui.add_message("System: Type :) :D <3 :fire: :rocket: and more for emojis!")
            
            # Set up input handler
            self.input_handler = InputHandler(self.ui.term, self._on_user_message)
            self.input_handler.start()
            
            # Initialize video capture
            self.ui.set_status("Opening camera...")
            self.ui.add_message("System: Opening camera...")
            try:
                self.video_capture = VideoCapture(device_id=self.device_id, fps_target=15)
                self.video_capture.open()
                self.ui.add_message("System: Camera opened successfully!")
            except Exception as e:
                self.ui.add_message(f"System: Camera error - {e}")
                raise
            
            # Set up network connection
            if self.mode == 'host':
                self._start_host_mode()
            else:
                self._start_connect_mode()
            
            if not self.connected:
                raise RuntimeError("Failed to establish connection")
            
            # Start capture and receive threads
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # Stats update thread
            stats_thread = threading.Thread(target=self._stats_loop, daemon=True)
            stats_thread.start()
            
            # Main loop - handle input
            self._main_loop()
            
        except KeyboardInterrupt:
            self.ui.add_message("System: Disconnecting...")
        except Exception as e:
            self.ui.add_message(f"System: Error - {e}")
        finally:
            self.stop()
    
    def _start_host_mode(self):
        """Start in host mode (listen for connection)."""
        self.ui.set_status(f"Waiting for connection on port {self.port}...")
        self.ui.add_message(f"System: Hosting on {self.host}:{self.port}")
        self.ui.add_message("System: Waiting for peer to connect...")
        
        self.server = NetworkServer(host=self.host, port=self.port)
        self.server.start()
        
        # Start camera preview thread while waiting for connection
        preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        preview_thread.start()
        
        # Wait for connection (with timeout checks)
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while self.running and time.time() - start_time < timeout:
            conn = self.server.accept(timeout=1.0)
            if conn:
                self.network = conn
                self.connected = True
                self.ui.set_status("Connected!")
                self.ui.add_message("System: Peer connected!")
                
                # Exchange user info
                self._exchange_user_info()
                return
        
        if not self.connected:
            raise RuntimeError("Connection timeout")
    
    def _start_connect_mode(self):
        """Start in connect mode (connect to host)."""
        target = self.remote_host if self.remote_host else self.host
        self.ui.set_status(f"Connecting to {target}:{self.port}...")
        self.ui.add_message(f"System: Connecting to {target}:{self.port}...")
        
        self.network = NetworkConnection()
        
        if self.network.connect(target, self.port, timeout=30):
            self.connected = True
            self.ui.set_status("Connected!")
            self.ui.add_message("System: Connected to peer!")
            
            # Exchange user info
            self._exchange_user_info()
        else:
            raise RuntimeError("Connection failed")
    
    def _exchange_user_info(self):
        """Exchange user information with peer."""
        from protocol import Protocol
        
        # Send our info
        user_info_msg = Protocol.create_user_info(
            self.user_name, 
            self.chat_color, 
            self.theme_color
        )
        self.network.send(user_info_msg)
        
        # Wait briefly for their info (it will be handled in _receive_loop)
        time.sleep(0.5)
    
    def _preview_loop(self):
        """Show camera preview while waiting for connection (host mode only)."""
        error_count = 0
        last_update = time.time()
        
        while self.running and not self.connected:
            try:
                # Limit preview update rate to 2 FPS for host mode
                if time.time() - last_update < 0.5:
                    time.sleep(0.1)
                    continue
                
                last_update = time.time()
                
                # Check if camera is enabled
                if not self.camera_enabled:
                    # Show placeholder when camera is off
                    ascii_frame = self.ascii_converter.generate_no_cam_placeholder()
                else:
                    # Capture frame
                    frame = self.video_capture.read_frame_throttled()
                    
                    if frame is None:
                        time.sleep(0.05)
                        continue
                    
                    # Reset error count on successful capture
                    error_count = 0
                    
                    # Convert to ASCII
                    ascii_frame = self.ascii_converter.image_to_ascii(frame)
                
                # Update local preview
                self.ui.update_local_frame(ascii_frame)
                
            except Exception as e:
                error_count += 1
                if self.running and error_count < 3 and not self.connected:
                    pass  # Silently skip errors during preview
                if error_count >= 10:
                    break
                time.sleep(0.1)
    
    def _capture_loop(self):
        """Capture and send video frames."""
        error_count = 0
        last_width_check = time.time()
        
        while self.running and self.connected:
            try:
                # Check if terminal was resized every 2 seconds
                if time.time() - last_width_check > 2.0:
                    new_width = self.ui.video_width
                    if new_width != self.ascii_converter.width:
                        self.ascii_converter.set_width(new_width)
                        self.ui.add_message(f"System: Resized to {new_width} chars")
                    last_width_check = time.time()
                
                # Check if camera is enabled
                if not self.camera_enabled:
                    # Show placeholder when camera is off
                    ascii_frame = self.ascii_converter.generate_no_cam_placeholder()
                else:
                    # Capture frame
                    frame = self.video_capture.read_frame_throttled()
                    
                    if frame is None:
                        time.sleep(0.01)
                        continue
                    
                    # Reset error count on successful capture
                    error_count = 0
                    
                    # Convert to ASCII
                    ascii_frame = self.ascii_converter.image_to_ascii(frame)
                
                # Update local preview
                self.ui.update_local_frame(ascii_frame)
                
                # Send to peer
                if self.network and self.network.is_connected():
                    self.network.send_video_frame(ascii_frame)
                    self.local_frame_count += 1
                
            except Exception as e:
                error_count += 1
                if self.running and error_count < 3:
                    self.ui.add_message(f"System: Capture error - {e}")
                if error_count >= 5:
                    self.ui.add_message("System: Too many capture errors, stopping")
                    break
                time.sleep(0.1)
    
    def _receive_loop(self):
        """Receive and display remote video frames."""
        error_count = 0
        
        while self.running and self.connected:
            try:
                # Check connection
                if not self.network.is_connected():
                    self.ui.add_message("System: Connection lost")
                    self.connected = False
                    break
                
                # Get video frame
                frame = self.network.get_video_frame(timeout=0.1)
                if frame:
                    self.ui.update_remote_frame(frame)
                    self.remote_frame_count += 1
                    error_count = 0
                
                # Get text messages
                text = self.network.get_text_message(timeout=0.01)
                if text:
                    # Check if this is a ping message
                    if text.startswith('[PING] '):
                        # Play loud alert sound for ping
                        self.sound_manager.play_ping_alert()
                        # Extract message and format with ATTENTION
                        ping_msg = text[7:]  # Remove '[PING] ' prefix
                        from blessed import Terminal
                        term = Terminal()
                        color_func = getattr(term, self.remote_chat_color, term.white)
                        self.ui.add_message(color_func(f"{self.remote_name}: ATTENTION: {ping_msg}"))
                    else:
                        # Regular message - play ding sound
                        self.sound_manager.play_chat_ding()
                        
                        # Format with remote user's color
                        from blessed import Terminal
                        term = Terminal()
                        color_func = getattr(term, self.remote_chat_color, term.white)
                        self.ui.add_message(color_func(f"{self.remote_name}: {text}"))
                
                # Check for user info
                user_info = self.network.get_user_info(timeout=0.01)
                if user_info:
                    from protocol import Protocol
                    name, chat_color, theme_color = Protocol.parse_user_info(user_info)
                    self.remote_name = name
                    self.remote_chat_color = chat_color
                    self.remote_theme_color = theme_color
                    self.ui.update_remote_name(name, theme_color)
                    self.ui.add_message(f"System: {name} has joined the chat!")
                
            except Exception as e:
                error_count += 1
                if self.running and error_count < 3:
                    self.ui.add_message(f"System: Receive error - {e}")
                if error_count >= 5:
                    self.ui.add_message("System: Too many receive errors, stopping")
                    break
                time.sleep(0.1)
    
    def _stats_loop(self):
        """Update FPS statistics."""
        while self.running:
            time.sleep(1.0)
            
            current_time = time.time()
            elapsed = current_time - self.last_stats_time
            
            if elapsed > 0:
                self.local_fps = self.local_frame_count / elapsed
                self.remote_fps = self.remote_frame_count / elapsed
                
                self.ui.update_fps(self.remote_fps, self.local_fps)
                
                # Reset counters
                self.local_frame_count = 0
                self.remote_frame_count = 0
                self.last_stats_time = current_time
    
    def _main_loop(self):
        """Main loop - update input display."""
        while self.running and self.connected:
            try:
                # Update input display
                if self.input_handler:
                    self.ui.set_input_text(self.input_handler.get_buffer())
                
                time.sleep(0.1)  # Slower to reduce CPU usage
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                if self.running:
                    self.ui.add_message(f"System: Main loop error - {e}")
                break
    
    def _on_user_message(self, message):
        """Handle user sending a message or command."""
        # Check if message is a command
        if message.startswith('/'):
            self._handle_command(message)
        else:
            # Regular message - check for emoji shortcode
            message = self._process_emojis(message)
            
            if self.network and self.network.is_connected():
                self.network.send_text(message)
                # Display with our chat color
                from blessed import Terminal
                term = Terminal()
                color_func = getattr(term, self.chat_color, term.white)
                self.ui.add_message(color_func(f"You: {message}"))
    
    def _process_emojis(self, text):
        """Replace emoji codes with emojis."""
        emoji_map = {
            ':)': '😊',
            ':D': '😄',
            ':(': '😢',
            ':P': '😛',
            ';)': '😉',
            '<3': '❤️',
            ':heart:': '❤️',
            ':fire:': '🔥',
            ':star:': '⭐',
            ':check:': '✓',
            ':x:': '✗',
            ':thumbsup:': '👍',
            ':thumbsdown:': '👎',
            ':wave:': '👋',
            ':clap:': '👏',
            ':rocket:': '🚀',
            ':eyes:': '👀',
            ':100:': '💯',
            ':thinking:': '🤔',
            ':laugh:': '😂',
            ':cry:': '😭',
            ':cool:': '😎',
            ':party:': '🎉',
        }
        
        for code, emoji in emoji_map.items():
            text = text.replace(code, emoji)
        
        return text
    
    def _handle_command(self, message):
        """Parse and execute chat commands."""
        parts = message.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command == '/copyframe':
            self._cmd_copyframe(args)
        elif command == '/color-mode':
            self._cmd_color_mode(args)
        elif command == '/color-chat':
            self._cmd_color_chat(args)
        elif command == '/ping':
            self._cmd_ping(args)
        elif command == '/mute':
            self._cmd_mute(args)
        elif command == '/togglecam':
            self._cmd_togglecam(args)
        elif command == '/help':
            self.ui.add_message("System: Available commands:")
            self.ui.add_message("System: /copyframe - Copy current ASCII frame to clipboard")
            self.ui.add_message("System: /color-mode {mode} - Change video color mode (normal, rainbow, grayscale)")
            self.ui.add_message("System: /color-chat {color} - Change your chat message color")
            self.ui.add_message("System: /ping {message} - Send an alert to the other user")
            self.ui.add_message("System: /mute - Toggle all sounds on/off")
            self.ui.add_message("System: /togglecam - Turn camera on/off")
            self.ui.add_message("System: Type [command] help for details on a command")
        else:
            self.ui.add_message(f"System: Unknown command '{command}'. Try /copyframe, /color-mode, /color-chat, /ping, /mute, or /togglecam")
    
    def _cmd_copyframe(self, args):
        """Copy current ASCII frame to clipboard."""
        if args.lower() == 'help':
            self.ui.add_message("System: /copyframe - Copies the current ASCII video frame to clipboard")
            return
        
        if not self.ui.local_frame:
            self.ui.add_message("System: No frame to copy yet")
            return
        
        # Remove ANSI color codes from frame before copying
        frame_text = self._strip_ansi_codes(self.ui.local_frame)
        
        try:
            self._copy_to_clipboard(frame_text)
            self.ui.add_message("System: Copied To Clipboard")
        except Exception as e:
            self.ui.add_message(f"System: Failed to copy frame - {e}")
    
    def _cmd_color_mode(self, args):
        """Change color mode."""
        if not args or args.lower() == 'help':
            self.ui.add_message("System: /color-mode {colormode} - Change video color mode")
            self.ui.add_message("System: Available modes: normal, rainbow, grayscale")
            return
        
        mode = args.lower().strip()
        valid_modes = ['normal', 'rainbow', 'grayscale', 'bw']
        
        if mode not in valid_modes:
            self.ui.add_message(f"System: Invalid color mode '{mode}'. Valid modes: normal, rainbow, grayscale")
            return
        
        # Map user-friendly names to internal names
        mode_mapping = {
            'normal': 'normal',
            'rainbow': 'rainbow',
            'grayscale': 'bw',
            'bw': 'bw'
        }
        
        internal_mode = mode_mapping[mode]
        self.color_mode = internal_mode
        self.ascii_converter.set_color_mode(internal_mode)
        
        self.ui.add_message(f"System: Color mode changed to {mode}")
    
    def _cmd_color_chat(self, args):
        """Change chat message color."""
        if not args or args.lower() == 'help':
            self.ui.add_message("System: /color-chat {color} - Change your chat message color")
            self.ui.add_message("System: Available colors: white, red, green, yellow, blue, magenta, cyan, black")
            return
        
        color = args.lower().strip()
        valid_colors = ['white', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'black']
        
        if color not in valid_colors:
            self.ui.add_message(f"System: Invalid color '{color}'. Valid colors: {', '.join(valid_colors)}")
            return
        
        self.chat_color = color
        self.ui.add_message(f"System: Chat color changed to {color}")
    
    def _cmd_ping(self, args):
        """Send a ping alert to the other user."""
        if not args or args.lower() == 'help':
            self.ui.add_message("System: /ping {message} - Send an alert to the other user with a message")
            self.ui.add_message("System: Example: /ping Come look at this!")
            return
        
        ping_message = args.strip()
        
        if not self.network or not self.network.is_connected():
            self.ui.add_message("System: Not connected to send ping")
            return
        
        # Play alert sound locally
        self.sound_manager.play_ping_alert()
        
        # Send ping message to peer with special marker
        ping_text = f"[PING] {ping_message}"
        self.network.send_text(ping_text)
        
        # Display locally
        from blessed import Terminal
        term = Terminal()
        color_func = getattr(term, self.chat_color, term.white)
        self.ui.add_message(color_func(f"You: ATTENTION: {ping_message}"))
    
    def _cmd_mute(self, args):
        """Mute or unmute all sounds."""
        if args.lower() == 'help':
            self.ui.add_message("System: /mute - Toggles all sounds on/off")
            return
        
        self.sound_manager.toggle_mute()
        status = "Muted" if self.sound_manager.muted else "Unmuted"
        self.ui.add_message(f"System: Sounds {status}")
    
    def _cmd_togglecam(self, args):
        """Toggle camera on or off."""
        if args.lower() == 'help':
            self.ui.add_message("System: /togglecam - Turns camera on/off")
            return
        
        self.camera_enabled = not self.camera_enabled
        status = "On" if self.camera_enabled else "Off"
        self.ui.add_message(f"System: Camera {status}")
    
    def _strip_ansi_codes(self, text):
        """Remove ANSI color codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard (cross-platform)."""
        system = platform.system()
        
        if system == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
                kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
                kernel32.GetClipboardData.argtypes = [ctypes.c_uint]
                kernel32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
                
                # Use PowerShell to copy to clipboard
                process = subprocess.Popen(
                    ['powershell', '-Command', f'$text = @"\n{text}\n"@ | Set-Clipboard'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate()
            except Exception:
                # Fallback: try using clip command
                process = subprocess.Popen(
                    'clip',
                    stdin=subprocess.PIPE,
                    shell=True
                )
                process.communicate(input=text.encode('utf-8'))
        
        elif system == 'Darwin':  # macOS
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE
            )
            process.communicate(input=text.encode('utf-8'))
        
        else:  # Linux
            try:
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE
                )
                process.communicate(input=text.encode('utf-8'))
            except FileNotFoundError:
                # Fallback to xsel if xclip is not available
                process = subprocess.Popen(
                    ['xsel', '--clipboard', '--input'],
                    stdin=subprocess.PIPE
                )
                process.communicate(input=text.encode('utf-8'))
    
    def stop(self):
        """Stop the session and clean up."""
        self.running = False
        self.connected = False
        
        # Stop UI components
        if self.input_handler:
            self.input_handler.stop()
        
        if self.ui:
            self.ui.set_status("Disconnected")
            time.sleep(0.5)  # Give UI time to update
            self.ui.stop()
        
        # Close network
        if self.network:
            self.network.close()
        
        if self.server:
            self.server.close()
        
        # Close camera
        if self.video_capture:
            self.video_capture.close()
        
        print("\nSession ended.")


if __name__ == "__main__":
    # Quick test
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'host':
        print("Starting in HOST mode on port 5000")
        session = ChatSession(mode='host', port=5000)
    else:
        print("Starting in CONNECT mode to localhost:5000")
        session = ChatSession(mode='connect', remote_host='127.0.0.1', port=5000)
    
    session.start()
