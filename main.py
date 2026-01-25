#!/usr/bin/env python3
"""
ASCII Video Chat - Real-time P2P video chat with ASCII art rendering

Usage:
    Host mode:    python main.py --host [--port 5000]
    Connect mode: python main.py --connect <IP> [--port 5000]
"""
import argparse
import sys
from rich import print
from rich.highlighter import Highlighter
from random import randint
from session import ChatSession


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

class RainbowHighlighter(Highlighter):
    def highlight(self, text):
        colorcode = 1
        for index in range(len(text)):     
            if text[index] == '\n':       
                index += 1

            text.stylize(f"color({int(colorcode)})", index, index + 1)
            


rainbow = RainbowHighlighter()

def print_banner():
    """Print ASCII art banner."""
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
    print(rainbow(banner))
    print("Real-time P2P Video Chat with ASCII Art - v2.0")
    print("=" * 80)
    print()


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
    print("Color Mode Options:")
    print("  1. Rainbow Heatmap (colorful, brightness-based)")
    print("  2. Black & White (classic ASCII)")
    print("  3. Normal Colors (original image colors)")
    
    while True:
        choice = input("\nSelect color mode (1-3): ").strip()
        if choice == '1':
            return 'rainbow'
        elif choice == '2':
            return 'bw'
        elif choice == '3':
            return 'normal'
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


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
        print("ERROR: Invalid settings:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    # Determine mode
    if args.host:
        mode = 'host'
        remote_host = None
        print(f"Mode: HOST")
        print(f"Listening on: {args.bind}:{args.port}")
        print(f"Share your IP with your peer so they can connect")
    else:
        mode = 'connect'
        remote_host = args.connect
        print(f"Mode: CONNECT")
        print(f"Connecting to: {remote_host}:{args.port}")
    
    print(f"Camera device: {args.device}")
    if args.width:
        print(f"ASCII width: {args.width} characters (manual)")
    else:
        print(f"ASCII width: Auto-detect from terminal size")
    print(f"Color mode: {args.color}")
    print()
    print("Starting in 2 seconds... (Ctrl+C to cancel)")
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
            color_mode=args.color
        )
        
        session.start()
        
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
