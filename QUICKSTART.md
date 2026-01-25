# Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test Your Camera (Optional)
```bash
python test_pipeline.py
```
You should see your webcam feed as ASCII art! Press Ctrl+C to stop.

### Step 3: Start a Video Chat

#### On Computer 1 (Host):
```bash
python main.py --host
```
The terminal will show your IP address. Share this with your friend.

#### On Computer 2 (Connect):
```bash
python main.py --connect <IP_ADDRESS>
```
Replace `<IP_ADDRESS>` with the IP from Computer 1.

### Step 4: Chat!
- You'll see your friend's video at the top as ASCII art
- Your own video preview is in the middle
- Messages appear at the bottom
- Type a message and press Enter to send
- Press Ctrl+C to disconnect

## Testing Locally

Open two terminal windows:

**Terminal 1 (Host):**
```bash
python main.py --host
```

**Terminal 2 (Connect):**
```bash
python main.py --connect 127.0.0.1
```

You'll see both video streams and can test messaging!

## Finding Your IP Address

### Windows:
```bash
ipconfig
```
Look for "IPv4 Address" under your network adapter.

### Mac/Linux:
```bash
ifconfig
# or
ip addr show
```
Look for your local network IP (usually starts with 192.168.x.x or 10.x.x.x).

## Tips for Best Experience

1. **Resize your terminal** to at least 120x50 characters for better quality
2. **Good lighting** helps the camera capture clearer video
3. **Stable network** - use wired connection if possible for lower latency
4. **Firewall** - You may need to allow the port (default: 5000) through your firewall

## Troubleshooting

**"Failed to open camera":**
- Check if another app is using your webcam
- Try a different device: `python main.py --host --device 1`

**"Connection timeout":**
- Make sure both computers are on the same network
- Check firewall settings
- Verify the IP address is correct

**"Video is choppy":**
- Reduce ASCII width: `python main.py --host --width 80`
- Close bandwidth-heavy applications
- Check your network connection

**"Terminal too small":**
- Maximize your terminal window
- Use a smaller width: `--width 80`

## Advanced Usage

### Custom Port
```bash
python main.py --host --port 8080
python main.py --connect 192.168.1.100 --port 8080
```

### Adjust Video Quality
```bash
# Lower width = faster, less detail
python main.py --host --width 80

# Higher width = slower, more detail
python main.py --host --width 150
```

### Specific Camera Device
```bash
# Try different camera devices if you have multiple
python main.py --host --device 0  # Default camera
python main.py --host --device 1  # Second camera
```

## Having Fun!

- Try different facial expressions and watch them render as ASCII
- Test the latency by waving at the camera
- Send messages while streaming
- Show objects to the camera and see how they look in ASCII

Enjoy your ASCII video chat! 🎥✨
