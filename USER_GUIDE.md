# Quick Start - For Non-Technical Users

## What You Need
1. The `ascii-video-chat.exe` file (get from your friend)
2. A webcam
3. Windows 10 or 11
4. Same network as your chat partner

## Setup (One Time)

### Step 1: Get Your Camera Device Number
1. Double-click `find_camera.exe` (if available)
2. Note the device number (usually 0 or 1)

### Step 2: Allow Through Firewall
1. Windows may ask "Allow access?" - Click **Yes**
2. Or manually:
   - Search "Windows Defender Firewall"
   - Click "Allow an app"
   - Click "Change settings"
   - Find `ascii-video-chat.exe` and check both boxes
   - Click OK

## How to Use

### If You're Hosting (Person 1):

1. **Find your IP address:**
   - Press `Windows + R`
   - Type: `cmd` and press Enter
   - Type: `ipconfig` and press Enter
   - Look for "IPv4 Address" (e.g., 192.168.1.100)
   - Write it down or copy it

2. **Start hosting:**
   - Open Command Prompt (search "cmd")
   - Navigate to where you saved the .exe
   - Type: `ascii-video-chat.exe --host --device 1`
   - Press Enter
   - Share your IP address with your friend

3. **Wait for connection:**
   - You'll see "Waiting for peer to connect..."
   - Once connected, you'll see their video!

### If You're Connecting (Person 2):

1. **Get the host's IP address** (from Person 1)

2. **Connect:**
   - Open Command Prompt (search "cmd")
   - Navigate to where you saved the .exe
   - Type: `ascii-video-chat.exe --connect 192.168.1.100 --device 1`
     (Replace 192.168.1.100 with the actual IP)
   - Press Enter

3. **You're connected!**
   - You'll see their video at the top
   - Your video preview at the bottom

## Using the Chat

- **Send a message:** Type and press Enter
- **Exit:** Press Ctrl+C

## Troubleshooting

### "Failed to open camera"
- Close other apps using the camera (Zoom, Teams, etc.)
- Try `--device 0` instead of `--device 1`

### "Connection timeout"
- Make sure both computers are on the same WiFi network
- Check the IP address is correct
- Try turning off VPN
- Check Windows Firewall settings

### "Can't find the .exe file"
You need to navigate to it. If it's on Desktop:
```cmd
cd Desktop
ascii-video-chat.exe --host --device 1
```

### Video looks weird
- Make your terminal window bigger
- Try adding `--width 40` for smaller size
- Try adding `--width 60` for larger size

## Example Commands

```cmd
# Host with default settings
ascii-video-chat.exe --host --device 1

# Host with custom port
ascii-video-chat.exe --host --device 1 --port 6000

# Connect with custom width
ascii-video-chat.exe --connect 192.168.1.100 --device 1 --width 60
```

## Need Help?
- Make sure you're on the same WiFi network
- Make sure Windows Firewall allows the app
- Try restarting both computers
- Try a different camera device number (0, 1, or 2)
