# Testing Instructions

## Quick Setup & Test

Since PowerShell 6+ is not available on your system, here are the manual steps:

### 1. Install Dependencies

Open Command Prompt or Windows PowerShell and run:

```cmd
cd C:\Users\Anna\desktop\Codestuff\live_ascii_video
python -m pip install -r requirements.txt
```

Or simply double-click: **setup.bat**

### 2. Test Individual Components

#### Test Protocol (no camera needed):
```cmd
python protocol.py
```
You should see: "✅ All protocol tests passed!"

#### Test Network (no camera needed):
```cmd
python network.py
```
You should see: "✅ Network test complete!"

#### Test Camera + ASCII Conversion:
```cmd
python test_pipeline.py
```
You should see your live webcam as ASCII art! Press Ctrl+C to stop.

### 3. Test Full Application (Localhost)

You need **TWO terminal windows** for this:

#### Terminal 1 (Host):
```cmd
cd C:\Users\Anna\desktop\Codestuff\live_ascii_video
python main.py --host
```

Wait until you see "Waiting for peer to connect..."

#### Terminal 2 (Connect):
```cmd
cd C:\Users\Anna\desktop\Codestuff\live_ascii_video
python main.py --connect 127.0.0.1
```

You should see:
- Remote video at the top (from other terminal's camera)
- Your video in the middle
- Message area at the bottom
- Type messages and press Enter to send

Press Ctrl+C in either terminal to disconnect.

### 4. Test Over Network (Two Computers)

#### Computer 1 (Host):
1. Find your IP address:
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Start host:
   ```cmd
   python main.py --host
   ```

3. Share your IP address with your friend

#### Computer 2 (Connect):
```cmd
python main.py --connect 192.168.1.100
```
(Replace with the actual IP from Computer 1)

## Troubleshooting

### "No module named 'cv2'" or similar:
```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### "Failed to open camera device":
- Close any other apps using the camera (Zoom, Teams, etc.)
- Try a different device ID:
  ```cmd
  python main.py --host --device 1
  ```

### Connection timeout:
- Make sure both computers are on the same network
- Check Windows Firewall - allow Python through for port 5000
- Verify the IP address is correct

### Video is choppy:
- Reduce width for better performance:
  ```cmd
  python main.py --host --width 80
  ```

### Terminal is too small:
- Maximize your terminal window
- Right-click title bar → Properties → Layout → Window Size
  - Width: 120 or more
  - Height: 40 or more

## Expected Behavior

### test_pipeline.py
- Shows your webcam feed as ASCII art
- Updates ~15 times per second
- Shows FPS counter

### main.py (connected)
- Top section: Remote peer's video (ASCII art)
- Middle section: Your video preview
- Bottom section: Chat messages
- Very bottom: Status bar with FPS
- Last line: Message input (type and press Enter)

## Performance Notes

- First frame may take a moment to appear
- FPS should be 10-15 for both local and remote
- Compression ratio is typically 30-40% of original size
- Heartbeat keeps connection alive every 5 seconds

## Next Steps

Once testing is successful:
1. Try different ASCII widths (--width 80, 120, 150)
2. Test with different lighting conditions
3. Try messaging while video streams
4. Test over internet using port forwarding or ngrok

Enjoy your ASCII video chat! 🎥✨
