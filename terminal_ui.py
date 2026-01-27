"""
Terminal UI - Blessed-based terminal interface for video chat
"""
from blessed import Terminal
import threading
import time


class TerminalUI:
    """Manages the terminal user interface."""
    
    def __init__(self, user_name="You", theme_color="green"):
        """Initialize terminal UI.
        
        Args:
            user_name: Display name for the local user
            theme_color: Theme color for video frame
        """
        self.term = Terminal()
        self.running = False
        self.render_thread = None
        self.user_name = user_name
        self.theme_color = theme_color
        self.remote_name = "Remote"
        self.remote_theme_color = "blue"
        
        # UI state
        self.remote_frame = ""
        self.local_frame = ""
        self.messages = []
        self.status_text = "Initializing..."
        self.input_text = ""
        self.fps_remote = 0
        self.fps_local = 0
        self.layout_changed = False
        
        # Layout
        self.update_layout()
        
        # Lock for thread-safe updates
        self.lock = threading.Lock()
    
    def update_layout(self):
        """Calculate layout dimensions based on terminal size."""
        self.width = self.term.width
        self.height = self.term.height
        
        # Side-by-side layout: Left = Remote, Right = Local, Bottom = Chat
        # Keep video height fixed, give more space to chat below
        # Minimum video height to be usable
        min_video_height = 30
        
        # Calculate video height: keep it fixed unless terminal is very small
        self.video_height = min_video_height
        self.video_width = max(50, (self.width - 2) // 2)  # Split width in half with divider
        
        # Chat gets remaining space after video + separator + status + input
        # Layout: video (20) + separator (1) + header (1) + status (1) + input (1) = 24 lines minimum
        # Remaining space goes to chat messages
        reserved_lines = 4  # separator + header + status + input
        available_chat_height = max(5, self.height - self.video_height - reserved_lines)
        self.chat_height = available_chat_height
        
        # Positions
        self.left_x = 0
        self.right_x = self.video_width + 2  # +2 for divider
        self.chat_y = self.video_height + 1
        self.status_y = self.height - 2
        self.input_y = self.height - 1
    
    def start(self):
        """Start the UI rendering loop."""
        self.running = True
        self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self.render_thread.start()
    
    def stop(self):
        """Stop the UI rendering."""
        self.running = False
        if self.render_thread:
            self.render_thread.join(timeout=1)
    
    def _render_loop(self):
        """Background rendering loop."""
        with self.term.hidden_cursor(), self.term.fullscreen(), self.term.cbreak():
            while self.running:
                try:
                    self._render_frame()
                    time.sleep(0.1)  # Slower refresh to reduce flicker (10 FPS UI)
                except Exception as e:
                    # Don't crash the UI thread
                    if self.running:
                        pass
    
    def _render_frame(self):
        """Render a single frame of the UI."""
        with self.lock:
            # Check for resize
            if self.term.width != self.width or self.term.height != self.height:
                self.update_layout()
                # Signal that layout changed
                self.layout_changed = True
            
            # Build output - don't clear entire screen every frame
            output = []
            
            # Only clear on first render or layout change
            if not hasattr(self, '_first_render_done') or self.layout_changed:
                output.append(self.term.home + self.term.clear)
                self._first_render_done = True
                self.layout_changed = False
            else:
                output.append(self.term.home)
            
            # Headers with dynamic colors
            remote_header = f" {self.remote_name.upper()} ".center(self.video_width)
            local_header = f" {self.user_name.upper()} ".center(self.video_width)
            
            # Get color functions based on theme
            remote_color_func = getattr(self.term, f'bold_white_on_{self.remote_theme_color}', self.term.bold_white_on_blue)
            local_color_func = getattr(self.term, f'bold_white_on_{self.theme_color}', self.term.bold_white_on_green)
            
            output.append(self.term.move_xy(self.left_x, 0) + remote_color_func(remote_header))
            output.append(self.term.move_xy(self.right_x, 0) + local_color_func(local_header))
            
            # Split frames into lines
            remote_lines = self.remote_frame.split('\n') if self.remote_frame else []
            local_lines = self.local_frame.split('\n') if self.local_frame else []
            
            # Render videos side by side (cap at reasonable max to leave room for chat)
            max_video_lines = min(self.video_height - 1, 50)
            for i in range(max_video_lines):
                y_pos = i + 1
                
                # Remote video (left) - keep ANSI codes, just truncate
                if i < len(remote_lines):
                    line = remote_lines[i]
                else:
                    line = ""
                output.append(self.term.move_xy(self.left_x, y_pos) + line + self.term.clear_eol)
                
                # Divider
                output.append(self.term.move_xy(self.video_width, y_pos) + self.term.bold(" │ "))
                
                # Local video (right) - keep ANSI codes
                if i < len(local_lines):
                    line = local_lines[i]
                else:
                    line = ""
                output.append(self.term.move_xy(self.right_x, y_pos) + line + self.term.clear_eol)
            
            # Chat section separator
            separator = "Commands: /copyframe /color-mode /color-chat /ping /togglesound /togglecam /exit /style. For help, type /help.".center(self.width, '─')
            output.append(self.term.move_xy(0, self.chat_y) + self.term.bold_black_on_white(separator))
            
            # Messages header
            output.append(self.term.move_xy(0, self.chat_y + 1) + self.term.bold(" MESSAGES "))
            
            # Show recent messages (show as many as fit in chat_height)
            num_visible_msgs = self.chat_height - 1  # -1 for header
            start_idx = max(0, len(self.messages) - num_visible_msgs)
            for i, msg in enumerate(self.messages[start_idx:]):
                if i >= num_visible_msgs:
                    break
                y_pos = self.chat_y + i + 2
                truncated_msg = msg[:self.width-1]
                output.append(self.term.move_xy(0, y_pos) + truncated_msg + self.term.clear_eol)
            
            # Clear remaining chat lines
            for i in range(len(self.messages[start_idx:]), num_visible_msgs):
                output.append(self.term.move_xy(0, self.chat_y + i + 2) + self.term.clear_eol)
            
            # Status bar
            status = f"Status: {self.status_text} | FPS: Remote={self.fps_remote:.1f} Local={self.fps_local:.1f}"
            status_line = status[:self.width]
            output.append(self.term.move_xy(0, self.status_y) + self.term.on_blue(status_line.ljust(self.width)))
            
            # Input line
            input_prompt = f"> {self.input_text}"
            input_line = input_prompt[:self.width-1]
            output.append(self.term.move_xy(0, self.input_y) + self.term.clear_eol + input_line)
            
            # Print all at once
            print(''.join(output), end='', flush=True)
    
    def update_remote_frame(self, frame):
        """Update the remote video frame."""
        with self.lock:
            # Truncate frame if too long to prevent overflow
            lines = frame.split('\n')
            max_lines = min(len(lines), 50)  # Cap at 50 lines for video
            self.remote_frame = '\n'.join(lines[:max_lines])
    
    def update_local_frame(self, frame):
        """Update the local video frame."""
        with self.lock:
            # Truncate frame if too long to prevent overflow
            lines = frame.split('\n')
            max_lines = min(len(lines), 50)  # Cap at 50 lines for video
            self.local_frame = '\n'.join(lines[:max_lines])
    
    def add_message(self, message):
        """Add a message to the chat."""
        with self.lock:
            self.messages.append(message)
            # Keep only recent messages
            if len(self.messages) > 100:
                self.messages = self.messages[-100:]
    
    def set_status(self, status):
        """Update status text."""
        with self.lock:
            self.status_text = status
    
    def update_fps(self, remote_fps, local_fps):
        """Update FPS counters."""
        with self.lock:
            self.fps_remote = remote_fps
            self.fps_local = local_fps
    
    def set_input_text(self, text):
        """Set the input text."""
        with self.lock:
            self.input_text = text
    
    def get_input_text(self):
        """Get the current input text."""
        with self.lock:
            return self.input_text
    
    def clear_input(self):
        """Clear the input text."""
        with self.lock:
            self.input_text = ""
    
    def update_remote_name(self, name, theme_color):
        """Update remote user's name and theme color."""
        with self.lock:
            self.remote_name = name
            self.remote_theme_color = theme_color


class InputHandler:
    """Handles keyboard input for the terminal UI."""
    
    def __init__(self, term, on_input_callback):
        """
        Initialize input handler.
        
        Args:
            term: Blessed Terminal instance
            on_input_callback: Function to call when user presses Enter
        """
        self.term = term
        self.on_input_callback = on_input_callback
        self.running = False
        self.input_thread = None
        self.input_buffer = ""
        
        # History tracking
        self.history = []
        self.history_index = -1
        self.history_search = ""  # Temporarily stores input while browsing history
    
    def start(self):
        """Start the input handling loop."""
        self.running = True
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
    
    def stop(self):
        """Stop the input handling."""
        self.running = False
    
    def _input_loop(self):
        """Background input loop."""
        while self.running:
            try:
                with self.term.cbreak():
                    key = self.term.inkey(timeout=0.1)
                    
                    if key:
                        if key.name == 'KEY_ENTER':
                            # User pressed Enter
                            if self.input_buffer.strip():
                                # Add to history before sending
                                self._add_to_history(self.input_buffer.strip())
                                self.on_input_callback(self.input_buffer.strip())
                                self.input_buffer = ""
                                self.history_index = -1  # Reset history index
                        
                        elif key.name == 'KEY_BACKSPACE':
                            # Backspace
                            if self.input_buffer:
                                self.input_buffer = self.input_buffer[:-1]
                        
                        elif key.name == 'KEY_ESCAPE':
                            # Escape - clear input
                            self.input_buffer = ""
                            self.history_index = -1  # Reset history
                        
                        elif key.name == 'KEY_UP':
                            # Go back in history
                            self._history_previous()
                        
                        elif key.name == 'KEY_DOWN':
                            # Go forward in history
                            self._history_next()
                        
                        elif key.is_sequence:
                            # Ignore other special keys
                            pass
                        
                        else:
                            # Regular character
                            if len(self.input_buffer) < 200:  # Limit input length
                                self.input_buffer += key
                        
            except Exception as e:
                # Don't crash on input errors
                pass
    
    def _add_to_history(self, command):
        """Add a command to the history."""
        self.history.append(command)
        # Keep history to last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def _history_previous(self):
        """Go back one entry in history."""
        if not self.history:
            return
        
        # If at the end of history, save current input
        if self.history_index == -1:
            self.history_search = self.input_buffer
        
        # Move back in history
        new_index = self.history_index - 1
        
        # Prevent going beyond the start of history
        if new_index < -len(self.history):
            new_index = -len(self.history)
        
        self.history_index = new_index
        
        # Load the history entry
        if self.history_index < 0:
            self.input_buffer = self.history[self.history_index]
        else:
            self.input_buffer = self.history_search
    
    def _history_next(self):
        """Go forward one entry in history."""
        if not self.history or self.history_index == -1:
            return
        
        # Move forward in history
        self.history_index += 1
        
        # If we've gone past the end, restore the saved input
        if self.history_index >= 0:
            self.input_buffer = self.history_search
            self.history_index = -1
        else:
            # Load the history entry
            self.input_buffer = self.history[self.history_index]
    
    def get_buffer(self):
        """Get current input buffer."""
        return self.input_buffer


if __name__ == "__main__":
    # Test the terminal UI
    print("Terminal UI Test")
    print("Starting in 2 seconds...")
    time.sleep(2)
    
    ui = TerminalUI()
    
    def on_message(text):
        ui.add_message(f"You: {text}")
    
    input_handler = InputHandler(ui.term, on_message)
    
    ui.set_status("Testing UI...")
    ui.start()
    input_handler.start()
    
    # Simulate video frames
    test_frame = "\n".join([" .:-=+*#%@" * 10 for _ in range(20)])
    
    try:
        for i in range(100):
            ui.update_remote_frame(test_frame)
            ui.update_local_frame(test_frame[::-1])  # Reversed for variety
            ui.update_fps(15.0, 14.5)
            ui.set_input_text(input_handler.get_buffer())
            
            if i % 30 == 0:
                ui.add_message(f"System: Test message {i}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    
    finally:
        input_handler.stop()
        ui.stop()
        print("\nUI test complete!")
