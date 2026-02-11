# Building on Mac - Quick Start

## The Problem You're Having

**Windows .exe files cannot run on Mac.** Each platform needs its own executable built natively on that platform. This is a fundamental limitation - not a bug.

## Solution: Build on Mac

### Option 1: One Command (Easiest)

1. Copy all your source code to the Mac
2. Open Terminal in that folder
3. Run:
```bash
chmod +x setup_and_build_mac.sh
./setup_and_build_mac.sh
```

This single script will:
- Check if Python 3 is installed
- Install pip if needed
- Install all dependencies
- Build the Mac executable

**Done!** Your executable will be in `dist/ascii-video-chat`

---

### Option 2: Manual Steps

If the automated script doesn't work, here's the manual process:

#### 1. Install Python 3 (if not already installed)

Check if you have Python:
```bash
python3 --version
```

If not installed, install via Homebrew:
```bash
brew install python3
```

Or download from: https://www.python.org/downloads/

#### 2. Install pip

```bash
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip --user
```

#### 3. Install dependencies

```bash
python3 -m pip install --user -r requirements.txt
python3 -m pip install --user pyinstaller
```

#### 4. Build the executable

```bash
python3 -m PyInstaller --onefile --name ascii-video-chat --add-data "sounds:sounds" main.py
```

#### 5. Run it

```bash
./dist/ascii-video-chat --help
```

---

## Common Mac Issues

### "pip is not on PATH"

This means pip wasn't installed correctly. Fix:
```bash
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip --user
```

Always use `python3 -m pip` instead of just `pip`.

### "Permission denied" when running

Make the file executable:
```bash
chmod +x dist/ascii-video-chat
```

### "Cannot be opened because it is from an unidentified developer"

This is macOS Gatekeeper. Two options:

**Option A (Safe):** Right-click → Open → Open anyway

**Option B (For testing):** 
```bash
xattr -d com.apple.quarantine dist/ascii-video-chat
```

### Camera not working

Grant camera permissions:
System Preferences → Security & Privacy → Camera → Add your terminal app

---

## Why Can't You Just Use One Executable?

Python executables are NOT cross-platform because:

1. **Different binary formats:**
   - Windows: PE (.exe)
   - Mac: Mach-O
   - Linux: ELF

2. **Different system libraries:**
   - Each OS has different native libraries
   - System calls are different

3. **PyInstaller limitations:**
   - Cannot cross-compile
   - Must build on target platform

**This is normal for Python applications.** Even commercial apps need separate builds per platform.

---

## Easiest Distribution Method

If you want "one-click" for users without building:

### For Windows users:
- Give them `dist/ascii-video-chat.exe` (built on Windows)

### For Mac users:
- Give them `dist/ascii-video-chat` (built on Mac)

### For Linux users:
- Give them `dist/ascii-video-chat` (built on Linux)

Or just distribute the Python source and tell users to run:
```bash
pip install -r requirements.txt
python main.py
```

---

## Alternative: Docker (Advanced)

If you want ONE distribution method for all users:

```bash
docker run -it --rm \
  --device=/dev/video0 \
  -v $(pwd):/app \
  python:3.11 \
  bash -c "cd /app && pip install -r requirements.txt && python main.py"
```

But this still requires users to have Docker installed.

---

## Recommended Workflow

**For your own use:**
1. Build Windows .exe on your Windows PC → use on Windows
2. Build Mac binary on a Mac → use on Mac
3. Build Linux binary on Linux → use on Linux

**For distribution:**
1. Use GitHub Actions (see BUILD_ALL_PLATFORMS.md)
2. Automatically creates all 3 executables
3. Users download the one for their OS

---

## Quick Reference

| Platform | Build Command | Output |
|----------|--------------|---------|
| Windows | `build.bat` | `dist\ascii-video-chat.exe` |
| Mac | `./setup_and_build_mac.sh` | `dist/ascii-video-chat` |
| Linux | `./setup_and_build_mac.sh` | `dist/ascii-video-chat` |

Each must be built on its native platform. No exceptions.
