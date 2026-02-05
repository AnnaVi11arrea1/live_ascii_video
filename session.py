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
from battleship import BattleshipGame, BattleshipAI, Orientation, Ship
from command_utils import open_manual, show_quick_help


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
        
        # Camera state
        self.camera_enabled = True
        
        # Battleship game state
        self.battleship_game = None
        self.battleship_ai = None
        self.battleship_mode = None  # None, "vs_human", "vs_ai"
        self.battleship_setup_ship_index = 0
        self.battleship_my_turn = False
        self.battleship_invite_pending = False
        self.battleship_waiting_for_opponent = False
        self.battleship_last_attack_pos = None  # Track last attack coordinate for multiplayer
        self.battleship_my_hits = set()  # Track which of our attacks were hits (for multiplayer)
        self.battleship_my_ships_placed = False  # Track if we've placed all ships
        self.battleship_opponent_ships_placed = False  # Track if opponent placed all ships
        self.battleship_my_dice_roll = None  # Our dice roll result
        self.battleship_opponent_dice_roll = None  # Opponent's dice roll
        
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
                        styled_ping = self._apply_styles(ping_msg)
                        self.ui.add_message(color_func(f"{self.remote_name}: ATTENTION: {styled_ping}"))
                    else:
                        # Regular message - play ding sound
                        self.sound_manager.play_chat_ding()
                        
                        # Format with remote user's color and apply styles
                        from blessed import Terminal
                        term = Terminal()
                        color_func = getattr(term, self.remote_chat_color, term.white)
                        styled_text = self._apply_styles(text)
                        self.ui.add_message(color_func(f"{self.remote_name}: {styled_text}"))
                
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
                
                # Check for battleship messages
                battleship_msg = self.network.get_battleship_message(timeout=0.01)
                if battleship_msg:
                    self._handle_battleship_message(battleship_msg)
                
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
        # Check if responding to battleship invitation
        if self.battleship_invite_pending and not message.startswith('/'):
            response = message.strip().lower()
            if response in ['yes', 'y']:
                self.ui.add_message("System: Accepted invitation! Starting game...")
                from protocol import Protocol
                accept_msg = Protocol.create_battleship_accept(True)
                self.network.send(accept_msg)
                self.battleship_invite_pending = False
                self._start_battleship_game("vs_human")
                return
            elif response in ['no', 'n']:
                self.ui.add_message("System: Declined invitation")
                from protocol import Protocol
                decline_msg = Protocol.create_battleship_accept(False)
                self.network.send(decline_msg)
                self.battleship_invite_pending = False
                return
        
        # Check if message is a command
        if message.startswith('/'):
            # Check if it's a battleship game command (coordinate or placement)
            if self.battleship_game and self.battleship_game.game_phase in ["setup", "playing"]:
                cmd_upper = message[1:].strip().upper()  # Remove slash and convert to uppercase
                parts = cmd_upper.split()
                
                is_battleship_input = False
                
                if self.battleship_game.game_phase == "setup":
                    # Ship placement format: "/A5 H" or "/A5 V"
                    if len(parts) == 2 and parts[1] in ['H', 'V']:
                        pos = BattleshipGame.coord_to_pos(parts[0])
                        if pos:
                            is_battleship_input = True
                
                elif self.battleship_game.game_phase == "playing":
                    # Attack format: "/A5"
                    if len(parts) == 1:
                        pos = BattleshipGame.coord_to_pos(parts[0])
                        if pos:
                            is_battleship_input = True
                
                if is_battleship_input:
                    self._handle_battleship_input(cmd_upper)
                    return
            
            # Not a battleship command, handle as normal command
            self._handle_command(message)
        else:
            # Regular message - check for emoji shortcode
            message = self._process_emojis(message)
            
            if self.network and self.network.is_connected():
                self.network.send_text(message)
                # Display with our chat color and apply styles
                from blessed import Terminal
                term = Terminal()
                color_func = getattr(term, self.chat_color, term.white)
                styled_message = self._apply_styles(message)
                self.ui.add_message(color_func(f"You: {styled_message}"))
    
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
    
    def _apply_styles(self, text):
        """Apply text styling and colors based on markup syntax.
        
        Syntax: [style color]text[/style color]
        
        Styles: bold, italic, underline, strikeout
        Colors: white, red, green, yellow, blue, magenta, cyan, black
        
        Example: [bold red]Important[/bold red] [underline blue]link[/underline blue]
        """
        from blessed import Terminal
        term = Terminal()
        
        # Supported styles and colors
        styles = ['bold', 'italic', 'underline', 'strikeout']
        colors = ['white', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'black']
        
        result = ""
        i = 0
        
        while i < len(text):
            # Look for opening tag [style color]
            if text[i] == '[' and i + 1 < len(text):
                # Find the closing bracket
                bracket_end = text.find(']', i)
                if bracket_end != -1:
                    tag_content = text[i+1:bracket_end]
                    
                    # Check if this is a closing tag [/style color]
                    if tag_content.startswith('/'):
                        # Skip closing tags in the main parsing - they're handled with opening tags
                        i = bracket_end + 1
                        continue
                    
                    # Parse the tag for style and color
                    parts = tag_content.split()
                    style = None
                    color = None
                    
                    if len(parts) >= 1 and parts[0] in styles:
                        style = parts[0]
                    if len(parts) >= 2 and parts[1] in colors:
                        color = parts[1]
                    elif len(parts) >= 1 and parts[0] in colors:
                        color = parts[0]
                    
                    # If we found a valid tag, look for matching closing tag
                    if style or color:
                        closing_tag = f"[/{tag_content}]"
                        content_start = bracket_end + 1
                        content_end = text.find(closing_tag, content_start)
                        
                        if content_end != -1:
                            # Extract content between tags
                            styled_text = text[content_start:content_end]
                            
                            # Build the styled version
                            styled_text = self._apply_style_and_color(styled_text, style, color, term)
                            result += styled_text
                            
                            # Move past the closing tag
                            i = content_end + len(closing_tag)
                            continue
            
            # Regular character
            result += text[i]
            i += 1
        
        return result
    
    def _apply_style_and_color(self, text, style, color, term):
        """Apply a specific style and color to text using blessed Terminal."""
        # Build the function name
        if style and color:
            # Try: bold_red, italic_blue, etc.
            func_name = f"{style}_{color}"
            if hasattr(term, func_name):
                return getattr(term, func_name)(text)
            # Try just the color
            if hasattr(term, color):
                colored = getattr(term, color)(text)
                # Now apply style to the colored text
                if hasattr(term, style):
                    return getattr(term, style)(colored)
        elif style:
            # Just style
            if hasattr(term, style):
                return getattr(term, style)(text)
        elif color:
            # Just color
            if hasattr(term, color):
                return getattr(term, color)(text)
        
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
        elif command == '/theme':
            self._cmd_theme(args)
        elif command == '/ping':
            self._cmd_ping(args)
        elif command == '/togglesound':
            self._cmd_togglesound(args)
        elif command == '/togglecam':
            self._cmd_togglecam(args)
        elif command == '/exit':
            self._cmd_exit(args)
        elif command == '/style':
            self._cmd_style(args)
        elif command == '/manual':
            self._cmd_manual(args)
        elif command == '/battleship':
            self._cmd_battleship(args)
        elif command == '/quit':
            self._cmd_quit(args)
        elif command == '/help':
            self._cmd_help(args)
        elif command == '/map':
            self._cmd_map(args)
        else:
            self.ui.add_message(f"System: Unknown command '{command}'. Type /help for available commands or /manual for full documentation")
    
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
            self.ui.add_message("System: Solid colors: red, green, blue, yellow, magenta, cyan, white, black")
            return
        
        mode = args.lower().strip()
        valid_modes = ['normal', 'rainbow', 'grayscale', 'bw', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 'black']
        
        if mode not in valid_modes:
            self.ui.add_message(f"System: Invalid color mode '{mode}'.")
            self.ui.add_message("System: Valid modes: normal, rainbow, grayscale, red, green, blue, yellow, magenta, cyan, white, black")
            return
        
        # Map user-friendly names to internal names
        mode_mapping = {
            'normal': 'normal',
            'rainbow': 'rainbow',
            'grayscale': 'bw',
            'bw': 'bw',
            'red': 'red',
            'green': 'green',
            'blue': 'blue',
            'yellow': 'yellow',
            'magenta': 'magenta',
            'cyan': 'cyan',
            'white': 'white',
            'black': 'black'
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
    
    def _cmd_theme(self, args):
        """Set video color mode, frame color, and chat color to the same color."""
        if not args or args.lower() == 'help':
            self.ui.add_message("System: /theme {color} - Set video, frame, and chat colors to the same color")
            self.ui.add_message("System: Available theme colors: white, red, green, yellow, blue, magenta, cyan, black")
            return
        
        color = args.lower().strip()
        valid_colors = ['white', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'black']
        
        if color not in valid_colors:
            self.ui.add_message(f"System: Invalid theme color '{color}'. Valid colors: {', '.join(valid_colors)}")
            return
        
        # Set all three colors to the selected color
        self.color_mode = color
        self.ascii_converter.set_color_mode(color)
        self.chat_color = color
        self.ui.add_message(f"System: Theme set to {color} (video, frame, and chat colors updated)")
    
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
    
    def _cmd_togglesound(self, args):
        """Toggle all sounds on or off."""
        if args.lower() == 'help':
            self.ui.add_message("System: /togglesound - Toggles all sounds on/off")
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
    
    def _cmd_exit(self, args):
        """Exit the program."""
        if args.lower() == 'help':
            self.ui.add_message("System: /exit - Exits the program and closes the connection")
            return
        
        self.ui.add_message("System: Exiting...")
        self.running = False
        self.connected = False
    
    def _cmd_style(self, args):
        """Show text styling help."""
        self.ui.add_message("System: Text Styling Syntax: [style color]text[/style color]")
        self.ui.add_message("System: Styles: bold, italic, underline, strikeout")
        self.ui.add_message("System: Colors: white, red, green, yellow, blue, magenta, cyan, black")
        self.ui.add_message("System: Examples:")
        self.ui.add_message("System:   [bold red]Important[/bold red]")
        self.ui.add_message("System:   [italic blue]Comment[/italic blue]")
        self.ui.add_message("System:   [underline green]Link[/underline green]")
        self.ui.add_message("System:   [bold yellow]Warning[/bold yellow]")
    
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
    
    def _cmd_manual(self, args):
        """Open command manual in new terminal window."""
        if open_manual():
            self.ui.add_message("System: Opening manual in new window...")
        else:
            self.ui.add_message("System: Failed to open manual. Check COMMANDS.md file exists.")
    
    def _cmd_help(self, args):
        """Show quick help in chat."""
        help_messages = show_quick_help()
        for msg in help_messages:
            self.ui.add_message(f"System: {msg}")
    
    def _cmd_battleship(self, args):
        """Start a battleship game."""
        if self.battleship_game:
            self.ui.add_message("System: A game is already in progress. Type /quit to exit current game.")
            return
        
        # Check if connected for multiplayer option
        if self.connected and self.network and self.network.is_connected():
            self.ui.add_message("System: Inviting opponent to play Battleship...")
            self.ui.add_message("System: Waiting for response...")
            
            # Send invitation
            from protocol import Protocol
            invite_msg = Protocol.create_battleship_invite()
            self.network.send(invite_msg)
            
            # Note: battleship_invite_pending should NOT be set here
            # That flag is only for the person RECEIVING an invitation
            self.battleship_waiting_for_opponent = True
            
            # Set a timeout or let user cancel with /quit
        else:
            self.ui.add_message("System: Not connected. Starting Battleship vs AI...")
            self._start_battleship_game("vs_ai")
    
    def _cmd_quit(self, args):
        """Quit battleship game."""
        if not self.battleship_game:
            self.ui.add_message("System: No active game to quit.")
            return
        
        self._end_battleship_game()
        self.ui.add_message("System: Exited Battleship game")
    
    def _cmd_map(self, args):
        """Show attack history map."""
        if not self.battleship_game:
            self.ui.add_message("System: No active game. Start a game with /battleship")
            return
        
        if self.battleship_game.game_phase != "playing":
            self.ui.add_message("System: Game must be in progress to view attack map")
            return
        
        self._show_attack_history()
    
    def _start_battleship_game(self, mode):
        """Start a new battleship game."""
        self.battleship_mode = mode
        self.battleship_game = BattleshipGame(mode=mode)
        self.battleship_setup_ship_index = 0
        
        # Initialize AI if needed
        if mode == "vs_ai":
            self.battleship_ai = BattleshipAI(self.battleship_game)
            self.battleship_ai.place_ships()
        elif mode == "vs_human":
            # For multiplayer, create placeholder opponent ships so check_winner() works
            # We don't know their positions, but we need to track which ones are sunk
            for ship_name, ship_size in BattleshipGame.SHIP_TYPES:
                # Create dummy ships at position (0,0) - positions don't matter for multiplayer
                # We only care about tracking which ships are sunk via hit_positions
                dummy_ship = Ship(ship_name, ship_size, (0, 0), Orientation.HORIZONTAL)
                # Don't set is_sunk directly - it's a computed property
                # When we get a "sunk" result, we'll fill hit_positions
                self.battleship_game.opponent_ships.append(dummy_ship)
        
        # Activate game UI
        self.ui.start_battleship()
        
        # Start ship placement phase
        self.ui.add_message("System: ═══ BATTLESHIP GAME STARTED ═══")
        self.ui.add_message("System: Place your ships! Use /coordinate orientation (e.g., /A5 H)")
        self._prompt_next_ship_placement()
    
    def _prompt_next_ship_placement(self):
        """Prompt user to place the next ship."""
        if self.battleship_setup_ship_index >= len(BattleshipGame.SHIP_TYPES):
            # All ships placed
            self._start_battleship_attack_phase()
            return
        
        ship_name, ship_size = BattleshipGame.SHIP_TYPES[self.battleship_setup_ship_index]
        self.ui.add_message(f"System: Place {ship_name} (size {ship_size})")
        self.ui.add_message(f"System: Enter: /<coordinate> <H/V> (e.g., /A5 H or /D3 V)")
        
        # Update display
        self._update_battleship_display()
    
    def _show_placement_preview(self):
        """Show a text preview of the current ship placement in chat."""
        board = self.battleship_game.get_board_display(is_player_grid=True, show_ships=True, use_color=False)
        lines = board.split('\n')
        
        self.ui.add_message("System: ┌─── Current Setup ───┐")
        for line in lines:
            self.ui.add_message(f"System: │ {line}")
        self.ui.add_message("System: └─────────────────────┘")
    
    def _show_attack_history(self):
        """Show a visual chart of all attacks (hits and misses) in chat."""
        if not self.battleship_game:
            return
        
        # Use blessed Terminal for colors in chat
        from blessed import Terminal
        term = Terminal()
        
        self.ui.add_message("System: ┌─── Your Attack History ───┐")
        
        # Build the board with colors
        lines = []
        # Header - use 3 chars per column for proper spacing
        header = "     " + "".join(f"{i:3}" for i in range(1, self.battleship_game.grid_size + 1))
        lines.append(header)
        
        # Rows
        for row in range(self.battleship_game.grid_size):
            row_char = chr(ord('A') + row)
            row_str = f"  {row_char}  "
            
            for col in range(self.battleship_game.grid_size):
                pos = (row, col)
                
                if pos in self.battleship_game.player_attacks:
                    # For multiplayer, use the hits set; for AI, check ship positions
                    is_hit = False
                    if self.battleship_mode == "vs_human":
                        is_hit = pos in self.battleship_my_hits
                    else:
                        # For AI mode, check actual ship positions
                        for ship in self.battleship_game.opponent_ships:
                            if pos in ship.positions:
                                is_hit = True
                                break
                    
                    if is_hit:
                        # Red X for hits
                        row_str += f"{term.red('X')}  "
                    else:
                        # White O for misses
                        row_str += f"{term.white('O')}  "
                else:
                    # Cyan ~ for unknown
                    row_str += f"{term.cyan('~')}  "
            
            lines.append(row_str)
        
        # Display in chat
        for line in lines:
            self.ui.add_message(f"System: │ {line}")
        
        # Add legend
        self.ui.add_message(f"System: │ Legend: {term.red('X')}=Hit {term.white('O')}=Miss {term.cyan('~')}=Unknown")
        self.ui.add_message("System: └──────────────────────────┘")
    
    def _start_battleship_attack_phase(self):
        """Start the attack phase of the game."""
        from blessed import Terminal
        term = Terminal()
        
        if self.battleship_mode == "vs_human":
            # Multiplayer - mark that we've placed our ships
            self.battleship_my_ships_placed = True
            
            # Show blue "waiting for opponent" message
            self.ui.add_message(term.blue("System: ✓ All your ships placed! Waiting for opponent to finish..."))
            
            # Send notification to opponent
            from protocol import Protocol
            ready_msg = Protocol.create_battleship_ship_placement()
            self.network.send(ready_msg)
            
            # If opponent is also ready, start dice roll
            if self.battleship_opponent_ships_placed:
                self._start_dice_roll()
        else:
            # AI mode - start immediately
            self.battleship_game.game_phase = "playing"
            self.battleship_my_turn = True
            
            self.ui.add_message("System: ═══ ALL SHIPS PLACED - BATTLE BEGINS! ═══")
            self.ui.add_message("System: Enter coordinates to attack (e.g., /A5)")
            self.ui.add_message("System: Type /quit to exit game anytime")
            
            self._update_battleship_display()
    
    def _start_dice_roll(self):
        """Roll dice to determine who goes first."""
        import random
        from blessed import Terminal
        term = Terminal()
        
        self.ui.add_message("System: ═══ BOTH PLAYERS READY! ═══")
        self.ui.add_message("System: Rolling d20 to determine first turn...")
        
        # Roll our dice
        self.battleship_my_dice_roll = random.randint(1, 20)
        self.ui.add_message(f"System: You rolled: {self.battleship_my_dice_roll}")
        
        # Send our roll to opponent
        from protocol import Protocol
        roll_msg = Protocol.create_battleship_move(str(self.battleship_my_dice_roll))  # Reusing move message
        self.network.send(roll_msg)
        
        # If we have both rolls, determine winner
        if self.battleship_opponent_dice_roll is not None:
            self._determine_first_turn()
    
    def _determine_first_turn(self):
        """Determine who goes first based on dice rolls."""
        from blessed import Terminal
        term = Terminal()
        
        self.ui.add_message(f"System: {self.remote_name} rolled: {self.battleship_opponent_dice_roll}")
        
        if self.battleship_my_dice_roll > self.battleship_opponent_dice_roll:
            self.battleship_my_turn = True
            self.ui.add_message(term.bright_green("System: You go first!"))
        elif self.battleship_my_dice_roll < self.battleship_opponent_dice_roll:
            self.battleship_my_turn = False
            self.ui.add_message(term.blue(f"System: {self.remote_name} goes first!"))
        else:
            # Tie - roll again
            self.ui.add_message("System: Tie! Rolling again...")
            self.battleship_my_dice_roll = None
            self.battleship_opponent_dice_roll = None
            self._start_dice_roll()
            return
        
        # Start the game
        self.battleship_game.game_phase = "playing"
        self.ui.add_message("System: ═══ BATTLE BEGINS! ═══")
        if self.battleship_my_turn:
            self.ui.add_message("System: Enter coordinates to attack (e.g., /A5)")
        else:
            self.ui.add_message("System: Waiting for opponent's move...")
        self.ui.add_message("System: Type /quit to exit game anytime")
        self._update_battleship_display()
    
    def _handle_battleship_input(self, message):
        """Handle input during battleship game."""
        message = message.strip().upper()
        
        if self.battleship_game.game_phase == "setup":
            # Ship placement phase
            self._handle_ship_placement(message)
        elif self.battleship_game.game_phase == "playing":
            # Attack phase
            self._handle_battleship_attack(message)
    
    def _handle_ship_placement(self, message):
        """Handle ship placement input."""
        parts = message.split()
        if len(parts) != 2:
            self.ui.add_message("System: Invalid format. Use: /<coordinate> <H/V>  (e.g., /A5 H)")
            return
        
        coord_str, orientation_str = parts
        
        # Parse coordinate
        pos = BattleshipGame.coord_to_pos(coord_str)
        if not pos:
            self.ui.add_message(f"System: Invalid coordinate '{coord_str}'. Use A-J and 1-10")
            return
        
        # Parse orientation
        if orientation_str not in ['H', 'V']:
            self.ui.add_message("System: Invalid orientation. Use H (horizontal) or V (vertical)")
            return
        
        orientation = Orientation.HORIZONTAL if orientation_str == 'H' else Orientation.VERTICAL
        
        # Try to place ship
        ship_name, ship_size = BattleshipGame.SHIP_TYPES[self.battleship_setup_ship_index]
        
        if self.battleship_game.place_ship(ship_name, ship_size, pos, orientation, is_player=True):
            self.ui.add_message(f"System: {ship_name} placed successfully!")
            
            # Show preview of current board setup
            self._show_placement_preview()
            
            self.battleship_setup_ship_index += 1
            self._prompt_next_ship_placement()
        else:
            self.ui.add_message("System: Invalid placement! Ship doesn't fit or overlaps another ship.")
            self.ui.add_message("System: Try again.")
    
    def _handle_battleship_attack(self, coord_str):
        """Handle attack input."""
        if not self.battleship_my_turn:
            self.ui.add_message("System: It's not your turn yet!")
            return
        
        # Parse coordinate
        pos = BattleshipGame.coord_to_pos(coord_str)
        if not pos:
            self.ui.add_message(f"System: Invalid coordinate '{coord_str}'. Use A-J and 1-10")
            return
        
        # For multiplayer, send move to opponent
        if self.battleship_mode == "vs_human":
            from protocol import Protocol
            move_msg = Protocol.create_battleship_move(coord_str)
            self.network.send(move_msg)
            self.ui.add_message(f"System: Attacking {coord_str}...")
            # Store the position for when we get the result back
            self.battleship_last_attack_pos = pos
            # Result will come back via MSG_BATTLESHIP_RESULT
            return
        
        # For AI mode, process attack immediately
        # Attack
        result, ship_name = self.battleship_game.attack(pos, is_player_attacking=True)
        
        if result == "invalid":
            self.ui.add_message("System: Invalid coordinate!")
            return
        elif result == "already_attacked":
            self.ui.add_message("System: You already attacked that position!")
            return
        
        # Display result
        if result == "miss":
            self.ui.add_message(f"System: {coord_str} - MISS! ○")
        elif result == "hit":
            self.ui.add_message(f"System: {coord_str} - HIT! ✕")
        elif result == "sunk":
            self.ui.add_message(f"System: {coord_str} - HIT! You sunk their {ship_name}! ✗")
        
        # Show attack history chart
        self._show_attack_history()
        
        # Check for winner
        winner = self.battleship_game.check_winner()
        if winner:
            from blessed import Terminal
            term = Terminal()
            if winner == "player":
                self.ui.add_message(term.bright_green("System: ★★★ VICTORY! You sunk all enemy ships! ★★★"))
            else:
                self.ui.add_message("System: ☠ DEFEAT! All your ships were sunk! ☠")
            
            self.battleship_game.game_phase = "finished"
            self.ui.add_message("System: Game over. Type /quit to exit or /battleship to play again")
            self._update_battleship_display()
            return
        
        # AI's turn
        if self.battleship_mode == "vs_ai":
            self.battleship_my_turn = False
            self._update_battleship_display()
            
            # Small delay for realism
            time.sleep(1)
            
            # AI attacks
            ai_pos = self.battleship_ai.choose_attack()
            ai_result, ai_ship = self.battleship_game.attack(ai_pos, is_player_attacking=False)
            ai_coord = BattleshipGame.pos_to_coord(ai_pos)
            
            # Process AI result
            self.battleship_ai.process_result(ai_pos, ai_result, ai_ship)
            
            # Display AI attack
            if ai_result == "miss":
                self.ui.add_message(f"System: AI attacks {ai_coord} - MISS! ○")
            elif ai_result == "hit":
                self.ui.add_message(f"System: AI attacks {ai_coord} - HIT! ✕")
            elif ai_result == "sunk":
                self.ui.add_message(f"System: AI attacks {ai_coord} - HIT! Your {ai_ship} was sunk! ✗")
            
            # Check for winner again
            winner = self.battleship_game.check_winner()
            if winner:
                from blessed import Terminal
                term = Terminal()
                if winner == "player":
                    self.ui.add_message(term.bright_green("System: ★★★ VICTORY! You sunk all enemy ships! ★★★"))
                else:
                    self.ui.add_message("System: ☠ DEFEAT! All your ships were sunk! ☠")
                
                self.battleship_game.game_phase = "finished"
                self.ui.add_message("System: Game over. Type /quit to exit or /battleship to play again")
            else:
                self.battleship_my_turn = True
                self.ui.add_message("System: Your turn! Enter coordinates to attack (e.g., /A5)")
        
        self._update_battleship_display()
    
    def _update_battleship_display(self):
        """Update the battleship game display."""
        if not self.battleship_game:
            return
        
        # Get player's board (shows own ships)
        player_board = self.battleship_game.get_board_display(is_player_grid=True, show_ships=True)
        
        # Get attack board (shows attacks on opponent, no ships)
        attack_board = self.battleship_game.get_board_display(is_player_grid=False, show_ships=False)
        
        # Create status text
        player_ships_left = self.battleship_game.get_remaining_ships(is_player=True)
        opponent_ships_left = self.battleship_game.get_remaining_ships(is_player=False)
        
        if self.battleship_game.game_phase == "setup":
            status = f"Setup Phase - Placing ships..."
        elif self.battleship_game.game_phase == "playing":
            turn_text = "YOUR TURN" if self.battleship_my_turn else "OPPONENT'S TURN"
            status = f"{turn_text} | Your Ships: {player_ships_left} | Enemy Ships: {opponent_ships_left}"
        else:
            status = "Game Over"
        
        # Add headers to boards
        player_board_titled = "YOUR SHIPS\n" + player_board
        attack_board_titled = "YOUR ATTACKS\n" + attack_board
        
        self.ui.update_battleship_boards(player_board_titled, attack_board_titled, status)
    
    def _end_battleship_game(self):
        """End the current battleship game."""
        # Send quit message if in multiplayer
        if self.battleship_mode == "vs_human" and self.network and self.network.is_connected():
            from protocol import Protocol
            quit_msg = Protocol.create_battleship_quit()
            self.network.send(quit_msg)
        
        self.battleship_game = None
        self.battleship_ai = None
        self.battleship_mode = None
        self.battleship_setup_ship_index = 0
        self.battleship_my_turn = False
        self.battleship_invite_pending = False
        self.battleship_waiting_for_opponent = False
        self.battleship_last_attack_pos = None
        self.battleship_my_hits = set()
        self.battleship_my_ships_placed = False
        self.battleship_opponent_ships_placed = False
        self.battleship_my_dice_roll = None
        self.battleship_opponent_dice_roll = None
        self.ui.stop_battleship()
    
    def _handle_battleship_message(self, msg_data):
        """Handle received battleship protocol messages."""
        from protocol import (Protocol, MSG_BATTLESHIP_INVITE, MSG_BATTLESHIP_ACCEPT,
                            MSG_BATTLESHIP_SHIP_PLACEMENT, MSG_BATTLESHIP_MOVE,
                            MSG_BATTLESHIP_RESULT, MSG_BATTLESHIP_QUIT)
        
        msg_type, payload = msg_data
        
        if msg_type == MSG_BATTLESHIP_INVITE:
            # Received game invitation
            if self.battleship_game:
                # Already in a game, decline
                decline_msg = Protocol.create_battleship_accept(False)
                self.network.send(decline_msg)
                self.ui.add_message(f"System: {self.remote_name} wants to play Battleship, but you're already in a game!")
            else:
                self.ui.add_message(f"System: {self.remote_name} invited you to play Battleship!")
                self.ui.add_message("System: Type 'yes' or 'y' to accept, 'no' or 'n' to decline")
                self.battleship_invite_pending = True
        
        elif msg_type == MSG_BATTLESHIP_ACCEPT:
            # Response to our invitation
            accepted = Protocol.parse_battleship_accept(payload)
            if accepted:
                self.ui.add_message(f"System: {self.remote_name} accepted! Starting game...")
                self.battleship_waiting_for_opponent = False
                self._start_battleship_game("vs_human")
            else:
                self.ui.add_message(f"System: {self.remote_name} declined the invitation")
                self.battleship_invite_pending = False
                self.battleship_waiting_for_opponent = False
        
        elif msg_type == MSG_BATTLESHIP_SHIP_PLACEMENT:
            # Opponent finished ship placement
            if self.battleship_game and self.battleship_mode == "vs_human":
                from blessed import Terminal
                term = Terminal()
                self.battleship_opponent_ships_placed = True
                self.ui.add_message(term.blue(f"System: {self.remote_name} has finished placing ships!"))
                
                # If we're also done, start dice roll
                if self.battleship_my_ships_placed:
                    self._start_dice_roll()
        
        elif msg_type == MSG_BATTLESHIP_MOVE:
            # Could be opponent's attack OR dice roll
            if self.battleship_game and self.battleship_mode == "vs_human":
                coord_str = Protocol.parse_battleship_move(payload)
                
                # Check if this is a dice roll (numeric value 1-20 during setup)
                if self.battleship_game.game_phase == "setup" and coord_str.isdigit():
                    roll = int(coord_str)
                    if 1 <= roll <= 20:
                        self.battleship_opponent_dice_roll = roll
                        # If we have both rolls, determine winner
                        if self.battleship_my_dice_roll is not None:
                            self._determine_first_turn()
                        return
                
                # Otherwise it's an attack
                pos = BattleshipGame.coord_to_pos(coord_str)
                
                if pos:
                    # Process attack on our grid
                    result, ship_name = self.battleship_game.attack(pos, is_player_attacking=False)
                    
                    # Send result back
                    result_msg = Protocol.create_battleship_result(result, ship_name)
                    self.network.send(result_msg)
                    
                    # Display what happened
                    if result == "miss":
                        self.ui.add_message(f"System: {self.remote_name} attacks {coord_str} - MISS! ○")
                    elif result == "hit":
                        self.ui.add_message(f"System: {self.remote_name} attacks {coord_str} - HIT! ✕")
                    elif result == "sunk":
                        self.ui.add_message(f"System: {self.remote_name} attacks {coord_str} - Your {ship_name} was sunk! ✗")
                    
                    # Check for winner
                    winner = self.battleship_game.check_winner()
                    if winner:
                        from blessed import Terminal
                        term = Terminal()
                        if winner == "opponent":
                            # Opponent sunk all our ships - they win, we lose
                            self.ui.add_message("System: ☠ DEFEAT! All your ships were sunk! ☠")
                        else:
                            # We sunk all opponent's ships - we win
                            self.ui.add_message(term.bright_green("System: ★★★ VICTORY! You sunk all enemy ships! ★★★"))
                        self.battleship_game.game_phase = "finished"
                    else:
                        # Now it's our turn
                        self.battleship_my_turn = True
                        self.ui.add_message("System: Your turn! (e.g., /A5)")
                    
                    self._update_battleship_display()
        
        elif msg_type == MSG_BATTLESHIP_RESULT:
            # Result of our attack  
            if self.battleship_game and self.battleship_mode == "vs_human":
                result, ship_name = Protocol.parse_battleship_result(payload)
                
                # Record the attack locally now that we have the result
                if self.battleship_last_attack_pos and result in ["miss", "hit", "sunk"]:
                    # Manually record the attack in our attack set
                    self.battleship_game.player_attacks.add(self.battleship_last_attack_pos)
                    
                    # Track hits separately for multiplayer (we don't know actual ship positions)
                    if result in ["hit", "sunk"]:
                        self.battleship_my_hits.add(self.battleship_last_attack_pos)
                    
                    # If a ship was sunk, mark it in our opponent_ships list
                    if result == "sunk" and ship_name:
                        for ship in self.battleship_game.opponent_ships:
                            if ship.name == ship_name:
                                # Mark ship as sunk by filling all its hit_positions
                                # is_sunk is a computed property based on hit_positions
                                for pos in ship.positions:
                                    ship.hit_positions.add(pos)
                                break
                
                # Display the result of our attack
                coord_str = BattleshipGame.pos_to_coord(self.battleship_last_attack_pos) if self.battleship_last_attack_pos else "?"
                if result == "miss":
                    self.ui.add_message(f"System: {coord_str} - MISS! ○")
                elif result == "hit":
                    self.ui.add_message(f"System: {coord_str} - HIT! ✕")
                elif result == "sunk":
                    self.ui.add_message(f"System: {coord_str} - HIT! You sunk their {ship_name}! ✗")
                elif result == "already_attacked":
                    self.ui.add_message(f"System: You already attacked that position!")
                
                # Clear the stored position
                self.battleship_last_attack_pos = None
                
                # Show attack history chart
                self._show_attack_history()
                
                # Check if we won (all opponent ships sunk)
                winner = self.battleship_game.check_winner()
                if winner:
                    from blessed import Terminal
                    term = Terminal()
                    if winner == "player":
                        self.ui.add_message(term.bright_green("System: ★★★ VICTORY! You sunk all enemy ships! ★★★"))
                    else:
                        self.ui.add_message("System: ☠ DEFEAT! All your ships were sunk! ☠")
                    self.battleship_game.game_phase = "finished"
                    self.ui.add_message("System: Game over. Type /quit to exit or /battleship to play again")
                else:
                    # Now opponent's turn
                    self.battleship_my_turn = False
                    self.ui.add_message("System: Opponent's turn...")
                
                self._update_battleship_display()
        
        elif msg_type == MSG_BATTLESHIP_QUIT:
            # Opponent quit the game
            self.ui.add_message(f"System: {self.remote_name} quit the game")
            self._end_battleship_game()
    
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
