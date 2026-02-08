# ASCII Video Chat CLI

A real-time peer-to-peer video chat application that renders video as ASCII art in your terminal!

## Features
- 🎥 Live webcam streaming as ASCII art
- 💬 Real-time text messaging
- 🔄 Bidirectional video (see each other)
- 🎮 Built-in Battleship game (vs Human)
- 📚 Interactive command manual
- 🖥️ Cross-platform (Windows, Mac, Linux)
- ⚡ 10-15 FPS smooth streaming
- 🎨 Multiple color modes and customization options

## Installation

### Prerequisites
- Python 3.8 or higher
- A webcam
- Terminal with at least 100x40 characters (larger is better!)

### Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test your setup (optional):**
   ```bash
   # Test camera
   python video_capture.py
   
   # Test ASCII pipeline
   python test_pipeline.py
   ```

## Usage

### Host Mode (Person 1)
```bash
python main.py --host --port 5000
```

### Connect Mode (Person 2)
```bash
python main.py --connect <HOST_IP> --port 5000
```

Example:
```bash
# Person 1 (host)
python main.py --host

# Person 2 (connect to person 1)
python main.py --connect 192.168.1.100
```

## Controls
- Type a message and press Enter to send
- Ctrl+C to disconnect and exit

## Project Structure
```
live_ascii_video/
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── main.py                # Entry point
├── ascii_converter.py     # Image to ASCII conversion
├── video_capture.py       # Webcam capture
├── network.py             # TCP networking
├── protocol.py            # Message protocol
├── terminal_ui.py         # Terminal interface
└── session.py             # Session coordinator
```

## Technical Details

### ASCII Conversion
- Character set: ` .:-=+*#%@` (light to dark)
- Configurable width (default: 100 chars)
- Maintains aspect ratio

## Commands & Features

### Quick Commands
- `/help` - Show quick help in chat
- `/manual` - Open full command manual in new terminal window
- `/battleship` - Start a Battleship game
- `/quit` - Exit current game
- `/color-mode {mode}` - Change video color mode
- `/color-chat {color}` - Change chat message color
- `/togglecam` - Turn camera on/off
- `/exit` - Exit the application
- `/togglesound` - Mutes the sound
- `/ping {message}` - Pings both users with an attention message
- `/theme {color}` - Switches the theme (ascii camera, chat font) to color

For complete command documentation, type `/manual` in the chat!

### Battleship Game 🎮

Play the classic naval combat game during your chat session!

**Features:**
- Play against another human (if connected) or AI opponent
- Traditional 10x10 grid with 5 ships
- Color-coded display (ships, hits, misses, sunk)
- Intelligent AI with hunt-and-target strategy
- Chat continues working during gameplay

**How to Play:**
1. Type `/battleship` to start
2. Choose vs Human or vs AI (if connected)
3. Place your 5 ships by entering coordinates and orientation
   - Example: `A5 H` (horizontal) or `A5 V` (vertical)
4. Take turns attacking coordinates
   - Example: `D7`
5. Sink all enemy ships to win!
6. Type `/quit` anytime to exit the game
7. Type `/map` anytime to view the battleship grid

**Ships:**
- Carrier (5 cells)
- Battleship (4 cells)
- Cruiser (3 cells)
- Submarine (3 cells)
- Destroyer (2 cells)

### Network Protocol
```
[Type: 1 byte][Length: 4 bytes][Payload: N bytes]
- 0x01: Video Frame
- 0x02: Text Message
- 0x03: Heartbeat
- 0x04: User Info
- 0x05-0x0A: Battleship Game Messages
```

### Performance
- Target: 10-15 FPS
- Compression: zlib on ASCII frames
- Frame dropping under load

## Troubleshooting

**Camera not found:**
- Check if another app is using the camera
- Try a different device ID: `python main.py --device 1`

**Connection issues:**
- Check firewall settings
- Ensure both machines are on the same network
- Try port forwarding for internet connections

**Low FPS:**
- Reduce ASCII width: `python main.py --width 80`
- Check network bandwidth
- Close other resource-intensive apps

## Development Status

### ✅ ALL FEATURES COMPLETE!
- [x] ASCII art converter with compression
- [x] Webcam capture with FPS control
- [x] TCP P2P networking with protocol
- [x] Terminal UI with split panes
- [x] Full integration with threading
- [x] CLI arguments and optimization
- [x] Message chat functionality
- [x] Battleship game (vs Human & AI)
- [x] Interactive command manual
- [x] Color customization

**Status: Ready to use! 🚀**

## Future Enhancements
- Audio streaming with ASCII waveforms
- Multi-party chat
- Recording/playback
- Filters and effects
- NAT traversal
- End-to-end encryption
- More mini-games (Chess, Tic-Tac-Toe, etc.)

## License
MIT

## Contributing
Pull requests welcome! This is an experimental project for fun and learning.
