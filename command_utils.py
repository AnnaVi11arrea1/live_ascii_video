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
        return False
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows - open in new CMD window
            subprocess.Popen([
                'start',
                'cmd',
                '/k',
                f'type "{manual_path}" && echo. && echo Press any key to close... && pause > nul'
            ], shell=True)
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
        "/quit         - Exit game (when in game)",
        "",
        "During Battleship:",
        "  - Type coordinates to attack (e.g., A5, J10)",
        "  - Type messages normally to chat",
        "  - Type /quit to exit game",
        "",
        "Type /manual for complete documentation!",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
