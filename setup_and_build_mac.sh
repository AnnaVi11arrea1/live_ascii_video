#!/bin/bash
# One-click Mac setup and build script
# This script installs everything needed and builds the executable

set -e  # Exit on any error

echo "========================================="
echo "ASCII Video Chat - Mac Setup & Build"
echo "========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo ""
    echo "Please install Python 3 from:"
    echo "  https://www.python.org/downloads/"
    echo ""
    echo "Or use Homebrew:"
    echo "  brew install python3"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Ensure pip is available
echo "Step 1: Ensuring pip is installed..."
python3 -m ensurepip --upgrade 2>/dev/null || true
python3 -m pip install --upgrade pip --user

if [ $? -ne 0 ]; then
    echo "❌ Failed to setup pip"
    exit 1
fi

echo "✓ pip is ready"
echo ""

# Install requirements
echo "Step 2: Installing dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install --user -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
else
    echo "⚠ Warning: requirements.txt not found, skipping..."
fi
echo ""

# Install PyInstaller
echo "Step 3: Installing PyInstaller..."
python3 -m pip install --user pyinstaller

if [ $? -ne 0 ]; then
    echo "❌ Failed to install PyInstaller"
    exit 1
fi

echo "✓ PyInstaller installed"
echo ""

# Build executable
echo "Step 4: Building macOS executable..."
echo "This may take a few minutes..."
echo ""

python3 -m PyInstaller --onefile --name ascii-video-chat --add-data "sounds:sounds" main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ Build Complete!"
echo "========================================="
echo ""
echo "Executable created: dist/ascii-video-chat"
echo ""
echo "To test:"
echo "  Host:    ./dist/ascii-video-chat --host --device 0"
echo "  Connect: ./dist/ascii-video-chat --connect 192.168.1.100 --device 0"
echo ""
echo "To distribute:"
echo "  Copy dist/ascii-video-chat to another Mac"
echo "  Make it executable: chmod +x ascii-video-chat"
echo ""
echo "Note: Users may need to right-click → Open the first time"
echo "      (macOS security feature for unsigned apps)"
echo ""
