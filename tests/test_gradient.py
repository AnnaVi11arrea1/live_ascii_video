"""
Test the gradient banner
"""
from rich.console import Console
from rich.text import Text

console = Console()

def test_gradient_banner():
    """Test the gradient banner effect."""
    banner = r"""
    ___   _______________   _    ___     __                ____ __          __ 
   /   | / ___/ ____/  _/  | |  / (_)___/ /__  ____      / __ )/ /_  ______/ /_
  / /| | \__ \/ /    / /   | | / / / __  / _ \/ __ \    / __  / / / / / __  / /
 / ___ |___/ / /____/ /    | |/ / / /_/ /  __/ /_/ /   / /_/ / / /_/ / /_/ / /_
/_/  |_/____/\____/___/    |___/_/\__,_/\___/\____/   /_____/_/\__,_/\__,_/\__/
                                                     
    """
    
    # Create gradient from yellow → lime → blue → purple → magenta
    text = Text(banner)
    
    # Calculate gradient steps
    lines = banner.split('\n')
    total_chars = sum(len(line) for line in lines)
    
    # Define gradient colors (hex format)
    colors = [
        "#FFFF00",  # Yellow
        "#BFFF00",  # Yellow-Lime transition
        "#7FFF00",  # Lime
        "#00FFFF",  # Cyan (transition to blue)
        "#0080FF",  # Blue
        "#4000FF",  # Blue-Purple
        "#8000FF",  # Purple
        "#BF00FF",  # Purple-Magenta
        "#FF00FF",  # Magenta
    ]
    
    # Apply gradient character by character
    char_index = 0
    for line_num, line in enumerate(lines):
        for char_pos, char in enumerate(line):
            if char.strip():  # Only color non-whitespace
                # Calculate which color to use based on position
                progress = char_index / max(total_chars - 1, 1)
                color_idx = int(progress * (len(colors) - 1))
                color_idx = min(color_idx, len(colors) - 1)
                
                # Calculate position in output
                offset = sum(len(lines[i]) + 1 for i in range(line_num)) + char_pos
                text.stylize(colors[color_idx], offset, offset + 1)
            
            char_index += 1
    
    console.print(text)
    console.print("[bold cyan]Real-time P2P Video Chat with ASCII Art - v2.0[/bold cyan]")
    console.print("=" * 80)


if __name__ == "__main__":
    print("\nTesting gradient banner...\n")
    test_gradient_banner()
    print("\nIf you see a smooth color gradient from yellow → lime → blue → purple → magenta,")
    print("your terminal supports it! This will appear when you run main.py")
