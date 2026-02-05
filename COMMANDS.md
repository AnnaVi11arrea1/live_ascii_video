```
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║                                                                           ║
 ║      █████╗ ███████╗ ██████╗██╗██╗    ██╗██╗  ██╗██╗███████╗██████╗     ║
 ║     ██╔══██╗██╔════╝██╔════╝██║██║    ██║██║  ██║██║██╔════╝██╔══██╗    ║
 ║     ███████║███████╗██║     ██║██║ █╗ ██║███████║██║███████╗██████╔╝    ║
 ║     ██╔══██║╚════██║██║     ██║██║███╗██║██╔══██║██║╚════██║██╔═══╝     ║
 ║     ██║  ██║███████║╚██████╗██║╚███╔███╔╝██║  ██║██║███████║██║         ║
 ║     ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝         ║
 ║                                                                           ║
 ║                        COMMAND REFERENCE MANUAL                           ║
 ║                              Version 2.0                                  ║
 ║                                                                           ║
 ╚═══════════════════════════════════════════════════════════════════════════╝
```

## TABLE OF CONTENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Getting Started
2. Chat Commands
3. Battleship Game
4. Application Controls
5. Troubleshooting
6. Tips & Tricks

═══════════════════════════════════════════════════════════════════════════════
1. GETTING STARTED
═══════════════════════════════════════════════════════════════════════════════

ASCII Whisper is a real-time peer-to-peer video chat application that renders
video as ASCII art in your terminal. You can chat, see each other's video feeds,
and play games like Battleship together!

HOST MODE:
  python main.py --host [--port 5000]
  
  Starts a server and waits for incoming connections.
  Share your IP address with your peer so they can connect.

CONNECT MODE:
  python main.py --connect <IP> [--port 5000]
  
  Connects to a host at the specified IP address.

EXAMPLE (Localhost testing):
  Terminal 1: python main.py --host
  Terminal 2: python main.py --connect 127.0.0.1


═══════════════════════════════════════════════════════════════════════════════
2. CHAT COMMANDS
═══════════════════════════════════════════════════════════════════════════════

Commands can be typed at any time during chat or gameplay.

┌─────────────────────────────────────────────────────────────────────────────┐
│ /manual                                                                     │
│   Opens this command manual in a separate terminal window.                 │
│   The window stays open until you close it.                                │
│   Can be used anytime - during chat, during games, etc.                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ /help                                                                       │
│   Displays quick help information in the chat area.                        │
│   Shows available commands and basic usage.                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ /battleship                                                                 │
│   Starts a game of Battleship.                                             │
│   - If connected to another player: Choose to play vs Human or vs AI       │
│   - If not connected: Automatically plays vs AI                            │
│   See section 3 for full Battleship instructions.                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ /quit (during game)                                                         │
│   Exits the current game and returns to normal chat.                       │
│   Your opponent will be notified that you left the game.                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Regular Messages                                                            │
│   Just type normally to send chat messages.                                │
│   Messages work during gameplay - you can chat while playing!              │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
3. BATTLESHIP GAME
═══════════════════════════════════════════════════════════════════════════════

HOW TO PLAY:
───────────────────────────────────────────────────────────────────────────────
Battleship is a classic guessing game where two players try to sink each other's
fleet of ships by calling out grid coordinates. The first player to sink all of
their opponent's ships wins!

GAME MODES:
───────────────────────────────────────────────────────────────────────────────
• VS HUMAN: Play against the connected player (if someone is connected)
• VS AI: Play against the computer opponent (available anytime)

THE GRID:
───────────────────────────────────────────────────────────────────────────────
• 10x10 grid with coordinates
• Rows: A, B, C, D, E, F, G, H, I, J (vertical)
• Columns: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 (horizontal)
• Example coordinates: A5, D9, J10

THE FLEET:
───────────────────────────────────────────────────────────────────────────────
Each player has 5 ships:
  • Carrier    (5 cells) ███████████
  • Battleship (4 cells) █████████
  • Cruiser    (3 cells) ███████
  • Submarine  (3 cells) ███████
  • Destroyer  (2 cells) █████

GAME PHASES:
───────────────────────────────────────────────────────────────────────────────

PHASE 1: SHIP PLACEMENT
  • Place your 5 ships on your grid
  • For each ship, enter:
    - /coordinate orientation (e.g., /A5 H)
    - Orientation: H (horizontal) or V (vertical)
  • Ships cannot overlap or go out of bounds
  • Your opponent cannot see your ship positions

PHASE 2: BATTLE
  • Take turns attacking coordinates
  • Enter /coordinate to attack (e.g., /B7)
  • Results:
    ○ MISS  - Empty water
    ✕ HIT   - You hit part of a ship
    ✗ SUNK  - You destroyed an entire ship
  • First player to sink all 5 enemy ships wins!

VISUAL INDICATORS:
───────────────────────────────────────────────────────────────────────────────
  ~  Empty water / Unknown
  S  Your ship (only visible on your grid)
  O  Miss (you or opponent missed here)
  X  Hit (a ship was hit here)
  #  Sunk ship

YOUR DISPLAY:
───────────────────────────────────────────────────────────────────────────────
┌─────────────────────────┬─────────────────────────┐
│   YOUR SHIPS GRID       │   YOUR ATTACKS GRID     │
│   (Shows your fleet)    │   (Your guesses)        │
│                         │                         │
│   See your ships (S)    │   Track hits (X)        │
│   See enemy hits on you │   Track misses (O)      │
└─────────────────────────┴─────────────────────────┘

COORDINATE INPUT:
───────────────────────────────────────────────────────────────────────────────
Valid formats (must use slash prefix):
  • /A5     ✓ (letter + number)
  • /a5     ✓ (lowercase is converted automatically)
  • /J10    ✓ (double-digit column)
  • A5      ✗ (missing slash - will be sent as chat message)
  • /A 5    ✗ (no spaces)
  • /5A     ✗ (wrong order)

Ship placement format:
  • /A5 H   ✓ (coordinate + H for horizontal)
  • /D3 V   ✓ (coordinate + V for vertical)
  • A5 H    ✗ (missing slash)

GAME COMMANDS:
───────────────────────────────────────────────────────────────────────────────
  /battleship - Start a new Battleship game
  /map        - Display your attack history chart (during game)
  /quit       - Exit game and return to chat
  /manual     - Open this manual
  /help       - Show quick help
  
During game, you can still send regular chat messages - just don't start them
with a slash! For example:
  • "nice shot!" - Sent as chat message ✓
  • /B7          - Attack coordinate B7 ✓
  • /map         - Show attack history ✓

CHATTING DURING GAME:
───────────────────────────────────────────────────────────────────────────────
You can send regular chat messages while playing! Just type anything that isn't
a coordinate or command:

  "A5"           → Attack coordinate A5
  "Nice shot!"   → Sends chat message
  "/quit"        → Exits game

AI OPPONENT:
───────────────────────────────────────────────────────────────────────────────
The AI opponent uses intelligent strategies:
  • Random search until it finds a ship
  • After a hit, it checks adjacent cells (hunt mode)
  • After consecutive hits, it continues in that direction
  • The AI makes realistic delays to simulate thinking


═══════════════════════════════════════════════════════════════════════════════
4. APPLICATION CONTROLS
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ Ctrl+C                                                                      │
│   Disconnect and exit the application completely.                          │
│   Use this to close ASCII Whisper.                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Enter                                                                       │
│   Send your typed message or game input.                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Terminal Resize                                                             │
│   The application automatically adjusts to terminal size changes.          │
│   For best experience, use a large terminal window.                        │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
5. TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

CONNECTION ISSUES:
───────────────────────────────────────────────────────────────────────────────
Q: Cannot connect to host?
A: • Verify the IP address is correct
   • Check that both computers are on the same network (or have port forwarding)
   • Ensure firewall isn't blocking the port
   • Make sure host started before client tried to connect

Q: Connection lost during game?
A: • In vs Human mode, the game will end if connection drops
   • In vs AI mode, games are local and won't be affected
   • Try reconnecting and starting a new game

GAMEPLAY ISSUES:
───────────────────────────────────────────────────────────────────────────────
Q: Invalid coordinate error?
A: • Make sure format is correct: Letter (A-J) + Number (1-10)
   • Examples: A5, B10, J3
   • No spaces allowed

Q: Can't place ship?
A: • Ships cannot overlap with existing ships
   • Ships must fit entirely within the grid
   • Check orientation (H for horizontal, V for vertical)

Q: Game feels stuck?
A: • Use /quit to exit and restart
   • Check if it's your turn or opponent's turn
   • Check the status line for current game state


═══════════════════════════════════════════════════════════════════════════════
6. TIPS & TRICKS
═══════════════════════════════════════════════════════════════════════════════

GENERAL TIPS:
───────────────────────────────────────────────────────────────────────────────
• Use a large terminal window (at least 120x40) for best experience
• The video feeds, chat, and game all work simultaneously
• Commands always start with "/" - everything else is a chat message
• You can open /manual anytime to reference this guide

BATTLESHIP STRATEGY:
───────────────────────────────────────────────────────────────────────────────
• Use a checkerboard pattern for initial attacks (e.g., A1, A3, A5...)
• When you get a hit, attack the cells directly adjacent (N/S/E/W)
• Place ships in unpredictable locations - avoid corners and edges
• Keep track of which ships your opponent has lost
• The Carrier (5 cells) is easiest to find, Destroyer (2 cells) is hardest

CHAT ETIQUETTE:
───────────────────────────────────────────────────────────────────────────────
• Be respectful - it's just a game!
• Say "gg" (good game) at the end
• Let opponent know if you need to leave suddenly
• Have fun and enjoy the ASCII art!


═══════════════════════════════════════════════════════════════════════════════
QUICK REFERENCE CARD
═══════════════════════════════════════════════════════════════════════════════

COMMANDS:
  /manual              Open this manual
  /help                Quick help
  /battleship          Start Battleship game
  /quit                Exit game

COORDINATES:
  A-J (rows) + 1-10 (columns)
  Examples: A5, D9, J10

SHIP PLACEMENT:
  Coordinate + Orientation
  Example: A5 H (horizontal from A5)
           A5 V (vertical from A5)

DURING GAME:
  A5                   Attack coordinate
  "message"            Send chat
  /quit                Exit game

═══════════════════════════════════════════════════════════════════════════════

For more information and updates, visit the project repository.
For bug reports or feature requests, please open an issue.

Enjoy ASCII Whisper!

═══════════════════════════════════════════════════════════════════════════════
