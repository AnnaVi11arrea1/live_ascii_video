# ASCII Video Chat CLI

A real-time peer-to-peer video chat application that renders video as ASCII art in your terminal!

## Features
- 🎥 Live webcam streaming as ASCII art
- 💬 Real-time text messaging
- 🔄 Bidirectional video (see each other)
- 🖥️ Cross-platform (Windows, Mac, Linux)
- ⚡ 10-15 FPS smooth streaming

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

### Network Protocol
```
[Type: 1 byte][Length: 4 bytes][Payload: N bytes]
- 0x01: Video Frame
- 0x02: Text Message
- 0x03: Heartbeat
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

### ✅ ALL PHASES COMPLETE!
- [x] ASCII art converter with compression
- [x] Webcam capture with FPS control
- [x] TCP P2P networking with protocol
- [x] Terminal UI with split panes
- [x] Full integration with threading
- [x] CLI arguments and optimization
- [x] Message chat functionality

**Status: Ready to use! 🚀**

## Future Enhancements
- Audio streaming with ASCII waveforms
- Multi-party chat
- Recording/playback
- Filters and effects
- NAT traversal
- End-to-end encryption

## License
MIT

## Contributing
Pull requests welcome! This is an experimental project for fun and learning.
