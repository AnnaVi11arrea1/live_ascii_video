# Building for All Platforms

## Important Note About Cross-Platform Builds

**PyInstaller cannot cross-compile executables.** This means:
- Windows executables must be built on Windows
- Linux executables must be built on Linux
- macOS executables must be built on macOS

You need access to each platform to create executables for it.

## Quick Build (Current Platform)

Run the universal build script on any platform:

```bash
# On Windows:
python build_all.py

# On Linux/Mac:
python3 build_all.py
```

Or use the platform-specific scripts:

```bash
# Windows:
build.bat

# Linux/Mac:
./build.sh
```

## Building for All Three Platforms

### Method 1: Manual (You Have Access to All Systems)

1. **On Windows:**
   ```bash
   python build_all.py
   # Creates: dist/ascii-video-chat.exe
   ```

2. **On Linux:**
   ```bash
   python3 build_all.py
   # Creates: dist/ascii-video-chat
   ```

3. **On macOS:**
   ```bash
   python3 build_all.py
   # Creates: dist/ascii-video-chat
   ```

4. **Organize the builds:**
   ```
   releases/
   ├── windows/
   │   └── ascii-video-chat.exe
   ├── linux/
   │   └── ascii-video-chat
   └── macos/
       └── ascii-video-chat
   ```

### Method 2: Using Virtual Machines

If you don't have physical access to all platforms:

1. **Windows:** Use your current machine
2. **Linux:** Use VirtualBox/VMware with Ubuntu
3. **macOS:** 
   - Use a Mac if available
   - Use cloud services (MacStadium, AWS EC2 Mac instances)
   - Note: Building for macOS on non-Apple hardware violates Apple's EULA

### Method 3: CI/CD (GitHub Actions)

Create `.github/workflows/build.yml` to automatically build on all platforms:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build executable
        run: python build_all.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ascii-video-chat-${{ matrix.os }}
          path: dist/*
```

Then download all three builds from GitHub Actions artifacts.

### Method 4: Docker (Linux Only)

Docker can build Linux executables on any host:

```bash
# Build Linux executable in Docker
docker run --rm -v "$(pwd):/app" python:3.11 bash -c "
  cd /app && 
  pip install -r requirements.txt && 
  python build_all.py
"
```

Note: This only works for Linux builds. Windows/Mac builds still need native systems.

## Platform-Specific Build Notes

### Windows
- No special requirements
- Executable will be: `dist/ascii-video-chat.exe`

### Linux
- May need to install `python3-dev` for some dependencies
- Make the executable runnable: `chmod +x dist/ascii-video-chat`
- Consider building on the oldest supported Linux version for compatibility

### macOS
- May need to sign the executable for Gatekeeper
- Universal binary (Intel + Apple Silicon) requires building on macOS
- Users may need to right-click → Open first time due to Gatekeeper

## Recommended Workflow

1. **Local Development:** Use your current OS (Windows)
2. **Testing:** Test on Windows directly
3. **Release Builds:**
   - Set up GitHub Actions for automated builds
   - OR use VMs for Linux/Mac builds
   - Tag a release and let CI build all three

## File Naming Convention

When distributing, rename files to be clear:

```
ascii-video-chat-v1.0-windows.exe
ascii-video-chat-v1.0-linux
ascii-video-chat-v1.0-macos
```

## Testing Builds

After creating executables, test each one:

```bash
# Windows
dist\ascii-video-chat.exe --help

# Linux/Mac
./dist/ascii-video-chat --help
```

## Troubleshooting

**Build fails on Linux/Mac:**
- Install missing system dependencies: `sudo apt-get install python3-dev` (Ubuntu)
- Install OpenCV dependencies if needed

**Executable doesn't run:**
- Ensure all dependencies are included in PyInstaller spec
- Check the `.spec` file if you need custom build configurations

**Large file size:**
- PyInstaller bundles Python + all dependencies
- Typical size: 50-100MB per executable
- Consider `--onefile` (current) vs `--onedir` (faster but more files)
