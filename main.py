#!/usr/bin/env python3
"""
ASCII Video Chat - Real-time P2P video chat with ASCII art rendering

Usage:
    Host mode:    python main.py --host [--port 5000]
    Connect mode: python main.py --connect <IP> [--port 5000]
"""
import argparse
import sys
from rich.console import Console
from rich.text import Text
from session import ChatSession

console = Console()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='ASCII Video Chat - Real-time P2P video chat in your terminal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Host a session:
    python main.py --host
    python main.py --host --port 5000
  
  Connect to a host:
    python main.py --connect 192.168.1.100
    python main.py --connect 192.168.1.100 --port 5000
  
  Localhost testing:
    Terminal 1: python main.py --host
    Terminal 2: python main.py --connect 127.0.0.1

Controls:
  - Type a message and press Enter to send
  - Ctrl+C to disconnect and exit
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--host',
        action='store_true',
        help='Host mode - wait for incoming connection'
    )
    mode_group.add_argument(
        '--connect',
        type=str,
        metavar='HOST',
        help='Connect mode - connect to specified host IP'
    )
    
    # Network settings
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port number (default: 5000)'
    )
    
    parser.add_argument(
        '--bind',
        type=str,
        default='0.0.0.0',
        help='Bind address for host mode (default: 0.0.0.0 for all interfaces)'
    )
    
    # Video settings
    parser.add_argument(
        '--width',
        type=int,
        default=None,
        help='ASCII art width in characters (default: auto-detect from terminal size)'
    )
    
    parser.add_argument(
        '--device',
        type=int,
        default=0,
        help='Camera device ID (default: 0 for default camera)'
    )
    
    parser.add_argument(
        '--color',
        type=str,
        choices=['rainbow', 'bw', 'normal'],
        default='rainbow',
        help='Color mode: rainbow (heatmap), bw (black/white), normal (original colors). Default: rainbow'
    )
    
    return parser.parse_args()


def print_banner():
    """Print ASCII art banner with gradient effect."""
    banner = r"""
                                                                           
     .oo .oPYo. .oPYo. o o   o      o 8       o                            
    .P 8 8      8    8 8 8   8      8 8                                    
   .P  8 `Yooo. 8      8 8   8      8 8oPYo. o8 .oPYo. .oPYo. .oPYo. oPYo. 
  oPooo8     `8 8      8 8   8  db  8 8    8  8 Yb..   8    8 8oooo8 8  `' 
 .P    8      8 8    8 8 8   `b.PY.d' 8    8  8   'Yb. 8    8 8.     8     
.P     8 `YooP' `YooP' 8 8    `8  8'  8    8  8 `YooP' 8YooP' `Yooo' 8     
..:::::..:.....::.....:....::::..:..::..:::..:..:.....:8 ....::.....:..::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::8 ::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::..::::::::::::::::::

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
    print()

    global user_name
    user_name = input("Enter your display name: ").strip()
    print(f"Welcome, {user_name}!")


def validate_settings(args):
    """Validate command line arguments."""
    errors = []
    
    if args.port < 1 or args.port > 65535:
        errors.append(f"Invalid port number: {args.port} (must be 1-65535)")
    
    if args.width is not None and (args.width < 40 or args.width > 300):
        errors.append(f"Invalid width: {args.width} (recommended 40-150)")
    
    if args.device < 0:
        errors.append(f"Invalid device ID: {args.device} (must be >= 0)")
    
    return errors


def ask_color_mode():
    """Ask user for color mode preference."""
    console.print("\n[bold]Color Mode Options:[/bold]")
    console.print("  [yellow]1.[/yellow] Rainbow Heatmap (colorful, brightness-based)")
    console.print("  [white]2.[/white] Black & White (classic ASCII)")
    console.print("  [cyan]3.[/cyan] Normal Colors (original image colors)")
    
    while True:
        choice = input("\nSelect color mode (1-3): ").strip()
        if choice == '1':
            return 'rainbow'
        elif choice == '2':
            return 'bw'
        elif choice == '3':
            return 'normal'
        else:
            console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")



def main():
    """Main entry point."""
    print_banner()
    
    # Parse arguments
    args = parse_args()
    
    # Ask for color mode if not specified
    if '--color' not in ' '.join(__import__('sys').argv):
        args.color = ask_color_mode()
        print()
    
    # Validate settings
    errors = validate_settings(args)
    if errors:
        console.print("[bold red]ERROR: Invalid settings:[/bold red]")
        for error in errors:
            console.print(f"  [red]- {error}[/red]")
        sys.exit(1)
    
    # Determine mode
    if args.host:
        mode = 'host'
        remote_host = None
        console.print(f"[bold green]Mode:[/bold green] HOST")
        console.print(f"[yellow]Listening on:[/yellow] {args.bind}:{args.port}")
        console.print(f"[yellow]Share your IP with your peer so they can connect[/yellow]")
    else:
        mode = 'connect'
        remote_host = args.connect
        console.print(f"[bold green]Mode:[/bold green] CONNECT")
        console.print(f"[yellow]Connecting to:[/yellow] {remote_host}:{args.port}")
    
    console.print(f"[cyan]Camera device:[/cyan] {args.device}")
    if args.width:
        console.print(f"[cyan]ASCII width:[/cyan] {args.width} characters (manual)")
    else:
        console.print(f"[cyan]ASCII width:[/cyan] Auto-detect from terminal size")
    console.print(f"[cyan]Color mode:[/cyan] {args.color}")
    print()
    console.print("[bold]Starting in 2 seconds... (Ctrl+C to cancel)[/bold]")
    print()
    
    import time
    time.sleep(2)
    
    # Create and start session
    try:
        session = ChatSession(
            mode=mode,
            host=args.bind if mode == 'host' else remote_host,
            port=args.port,
            remote_host=remote_host,
            ascii_width=args.width,
            device_id=args.device,
            color_mode=args.color,
            user_name=user_name
        )
        
        session.start()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
