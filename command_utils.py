"""
Command utilities - Helper functions for commands like /manual
"""
import subprocess
import platform
import os

def open_manual():
    """
    Open the COMMANDS.md manual in a separate terminal window.
    
    Returns:
        True if successful, False otherwise
    """
    # Get the path to COMMANDS.md
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manual_path = os.path.join(script_dir, "COMMANDS.txt")

    
    if not os.path.exists(manual_path):
        print(f"Manual not found at: {manual_path}")
        return False
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows - open in new CMD window with type command
            command = f'start cmd /k "chcp 65001 > nul && type \"{manual_path}\" && pause"'
            subprocess.Popen(command, shell=True)
            return True
        
        elif system == "Darwin":  # macOS
            # macOS - open in new Terminal window
            subprocess.Popen([
                'osascript',
                '-e',
                f'tell application "Terminal" to do script "less {manual_path}"'
            ])
            return True
        
        elif system == "Linux":
            # Linux - try common terminal emulators
            terminals = ['gnome-terminal', 'xterm', 'konsole', 'xfce4-terminal']
            
            for terminal in terminals:
                try:
                    if terminal == 'gnome-terminal':
                        subprocess.Popen([terminal, '--', 'less', manual_path])
                    else:
                        subprocess.Popen([terminal, '-e', f'less {manual_path}'])
                    return True
                except FileNotFoundError:
                    continue
            
            return False
        
        else:
            return False
    
    except Exception as e:
        print(f"Error opening manual: {e}")
        return False


def show_quick_help():
    """
    Return quick help text for display in chat.
    
    Returns:
        List of help message strings
    """
    return [
        "━━━━━━━━━ QUICK HELP ━━━━━━━━━",
        "/copyframe - Copy current ASCII frame to clipboard",
        "/color-mode {mode} - Change video color mode (normal, rainbow, grayscale)",
        "/color-chat {color} - Change your chat message color",
        "/ping {message} - Send an alert to the other user",
        "/mute         - Toggle all sounds on/off",
        "/togglecam    - Turn camera on/off",
        "/togglesound  - Turn sound on/off",
        "/manual       - Complete full documentation of Ascii Whisper in new window",
        "/battleship   - Start Battleship game",
        "/quit         - Exit Battleship Game (when in game)",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
