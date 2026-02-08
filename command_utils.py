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
    manual_path = os.path.join(script_dir, "COMMANDS.md")
    
    if not os.path.exists(manual_path):
        print(f"Manual not found at: {manual_path}")
        return False
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows - open in new CMD window
            # We use a single string with shell=True to avoid Python's list-to-commandline escaping quirks on Windows
            # chcp 65001 sets the terminal to UTF-8 to display box characters correctly
            command = f'start "ASCII Whisper Manual" cmd /k "chcp 65001 > nul & type \"{manual_path}\" & echo. & echo. & echo Press any key to close... & pause > nul"'
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
        "/manual       - Open full manual in new window",
        "/help         - Show this quick help",
        "/battleship   - Start Battleship game",
        "/map          - Show attack history (during game)",
        "/ai <msg>     - Talk to AI commentator",
        "/quit         - Exit game (when in game)",
        "",
        "During Battleship:",
        "  - Ship placement: /A5 H (coordinate + H/V)",
        "  - Attack: /A5 (just coordinate)",
        "  - Chat normally (no slash = chat message)",
        "",
        "Type /manual for complete documentation!",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
