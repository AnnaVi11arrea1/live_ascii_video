# Build Instructions - Creating Executable

## Option 1: PyInstaller (Recommended)

### Step 1: Install PyInstaller
```cmd
pip install pyinstaller
```

### Step 2: Build the executable
```cmd
cd C:\Users\Anna\desktop\Codestuff\live_ascii_video
pyinstaller --onefile --name ascii-video-chat --icon=NONE main.py
```

This creates:
- `dist\ascii-video-chat.exe` - The standalone executable

### Step 3: Distribute
Copy `ascii-video-chat.exe` to the other computer. That's it!

### Usage on other computer:
```cmd
# Host mode
ascii-video-chat.exe --host --device 1

# Connect mode
ascii-video-chat.exe --connect 192.168.1.100 --device 1
```

---

## Option 2: PyInstaller with Dependencies (Smaller, Faster)

If the executable is too large, create a folder with dependencies:

```cmd
pyinstaller --name ascii-video-chat main.py
```

This creates `dist\ascii-video-chat\` folder with the .exe and DLLs.
Distribute the entire folder.

---

## Option 3: Simple Python Distribution (No Compilation)

If both computers have Python installed:

### Create a distributable package:

1. **Zip the project folder:**
   ```cmd
   # Include only needed files
   ```

2. **On other computer:**
   ```cmd
   unzip ascii-video-chat.zip
   cd ascii-video-chat
   pip install -r requirements.txt
   python main.py --host --device 1
   ```

---

## Testing Between Computers

### Computer 1 (Host):
1. Find your IP address:
   ```cmd
   ipconfig
   ```
   Look for IPv4 Address (e.g., 192.168.1.100)

2. Allow through firewall:
   - Windows Defender Firewall → Allow an app
   - Add `ascii-video-chat.exe` or `python.exe`
   - Allow on Private networks

3. Run as host:
   ```cmd
   ascii-video-chat.exe --host --device 1
   ```

### Computer 2 (Connect):
```cmd
ascii-video-chat.exe --connect 192.168.1.100 --device 1
```

---

## File Sizes (Approximate)

- **--onefile**: ~100-150 MB (everything bundled, slower startup)
- **--onedir**: ~200 MB folder (faster startup)
- **Python package**: ~5 MB (requires Python installation)

---

## Troubleshooting Build Issues

### "Module not found" errors:
Add hidden imports:
```cmd
pyinstaller --onefile --hidden-import=cv2 --hidden-import=blessed main.py
```

### "DLL not found" errors:
Use onedir mode instead:
```cmd
pyinstaller main.py
```

### Antivirus blocks exe:
- Sign the executable (advanced)
- Use --onedir mode
- Add exception in antivirus
