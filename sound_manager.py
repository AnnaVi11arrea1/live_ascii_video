"""
Sound Manager - Handles audio playback for notifications and alerts
"""
import os
import sys
import threading
import platform


class SoundManager:
    """Manages sound playback for the application."""
    
    def __init__(self, muted=False):
        """Initialize sound manager with configurable sound paths."""
        self.startup_sound = self._get_default_sound_path('startup.wav')
        self.chat_ding_sound = self._get_default_sound_path('ding.wav')
        self.app_start_sound = self._get_default_sound_path('appstart.wav')
        self.ping_alert_sound = self._get_default_sound_path('alert.wav')
        self.battleship_start_sound = self._get_default_sound_path('battleship_start.wav')
        self.battleship_miss_sound = self._get_default_sound_path('battleship_miss.wav')
        self.battleship_hit_sound = self._get_default_sound_path('battleship_hit.wav')
        self.battleship_sink_sound = self._get_default_sound_path('sinking_ship.wav')
        self.battleship_win_sound = self._get_default_sound_path('victory_sound.wav')
        self.muted = muted
    
    def _get_default_sound_path(self, filename):
        """Get the default path for a sound file."""
        # Sounds are stored in a 'sounds' directory next to this file
        sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
        sound_path = os.path.join(sounds_dir, filename)
        return sound_path
    
    # this will play when the application starts
    def play_app_start_sound(self):
        """Play app start sound when starting the application."""
        self._play_sound(self.app_start_sound)
    
    def set_startup_sound(self, path):
        """Set custom path for startup sound."""
        if os.path.exists(path):
            self.startup_sound = path
            return True
        return False
    
    def set_chat_ding_sound(self, path):
        """Set custom path for chat ding sound."""
        if os.path.exists(path):
            self.chat_ding_sound = path
            return True
        return False
    
    def set_ping_alert_sound(self, path):
        """Set custom path for ping alert sound."""
        if os.path.exists(path):
            self.ping_alert_sound = path
            return True
        return False
    
    # Set Battleship sounds
    def set_battleship_miss_sound(self, path):
        """Set custom path for battleship miss sound."""
        if os.path.exists(path):
            self.battleship_miss_sound = path
            return True
        return False
    
    def set_battleship_hit_sound(self, path):
        """Set custom path for battleship hit sound."""
        if os.path.exists(path):
            self.battleship_hit_sound = path
            return True
        return False
    
    def set_battleship_win_sound(self, path):
        """Set custom path for battleship win sound."""
        if os.path.exists(path):
            self.battleship_win_sound = path
            return True
        return False
    
    def set_battleship_sink_sound(self, path):
        """Set custom path for battleship sink sound."""
        if os.path.exists(path):
            self.battleship_sink_sound = path
            return True
        return False
    
    def set_battleship_start_sound(self, path):
        """Set custom path for battleship start sound."""
        if os.path.exists(path):
            self.battleship_start_sound = path
            return True
        return False
    
    def set_muted(self, muted):
        """Set mute state."""
        self.muted = muted
    
    def toggle_mute(self):
        """Toggle mute state and return new state."""
        self.muted = not self.muted
        return self.muted
    
    def play_startup_sound(self):
        """Play startup sound on application start."""
        if not self.muted:
            self._play_sound(self.startup_sound)
    
    def play_chat_ding(self):
        """Play ding sound when receiving a chat message."""
        if not self.muted:
            # Play in background thread to not block
            thread = threading.Thread(target=self._play_sound, args=(self.chat_ding_sound,), daemon=True)
            thread.start()
    
    def play_ping_alert(self):
        """Play loud alert sound for ping command."""
        if not self.muted:
            # Play in background thread to not block
            thread = threading.Thread(target=self._play_sound, args=(self.ping_alert_sound,), daemon=True)
            thread.start()
            
    # Play Battleship sounds
    def play_battleship_miss(self):
        """Play sound for battleship miss."""
        if not self.muted:
            thread = threading.Thread(target=self._play_sound, args=(self.battleship_miss_sound,), daemon=True)
            thread.start()
        
    def play_battleship_hit(self):
        """Play sound for battleship hit."""
        if not self.muted:
            thread = threading.Thread(target=self._play_sound, args=(self.battleship_hit_sound,), daemon=True)
            thread.start()
    
    def play_battleship_sink(self):
        """Play sound for battleship sinking a ship."""
        if not self.muted:
            thread = threading.Thread(target=self._play_sound, args=(self.battleship_sink_sound,), daemon=True)
            thread.start()
            
    def play_battleship_win(self):
        """Play sound for battleship win."""
        if not self.muted:
            thread = threading.Thread(target=self._play_sound, args=(self.battleship_win_sound,), daemon=True)
            thread.start()
            
    def play_battleship_start(self):
        """Play sound for battleship game start."""
        if not self.muted:
            thread = threading.Thread(target=self._play_sound, args=(self.battleship_start_sound,), daemon=True)
            thread.start()
    
    def _play_sound(self, sound_path):
        """Play a sound file using OS-specific methods."""
        if not os.path.exists(sound_path):
            # Sound file not found, silently skip
            return
        
        try:
            system = platform.system()
            
            if system == 'Windows':
                self._play_sound_windows(sound_path)
            elif system == 'Darwin':  # macOS
                self._play_sound_macos(sound_path)
            else:  # Linux
                self._play_sound_linux(sound_path)
        
        except Exception as e:
            # Silently fail - don't interrupt application if sound fails
            pass
    
    def _play_sound_windows(self, sound_path):
        """Play sound on Windows using winsound."""
        try:
            import winsound
            winsound.PlaySound(sound_path, winsound.SND_FILENAME)
        except Exception:
            pass
    
    def _play_sound_macos(self, sound_path):
        """Play sound on macOS using afplay."""
        try:
            import subprocess
            subprocess.run(['afplay', sound_path], check=False, timeout=10)
        except Exception:
            pass
    
    def _play_sound_linux(self, sound_path):
        """Play sound on Linux using available tools."""
        import subprocess
        
        # Try multiple tools in order of preference
        tools = [
            ['paplay', sound_path],
            ['aplay', sound_path],
            ['ffplay', '-nodisp', '-autoexit', sound_path],
        ]
        
        for tool in tools:
            try:
                subprocess.run(tool, check=False, timeout=10, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except FileNotFoundError:
                continue
            except Exception:
                continue
