#!/bin/bash
# Build script for macOS/Linux

echo "========================================="
echo "ASCII Video Chat - Build Executable"
echo "========================================="
echo ""

echo "Step 1: Installing PyInstaller..."
python3 -m pip install pyinstaller

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyInstaller"
    exit 1
fi
echo ""

echo "Step 2: Building executable..."
echo "This may take a few minutes..."
echo ""

pyinstaller --onefile --name ascii-video-chat --add-data "sounds:sounds" main.py

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi
echo ""

echo "========================================="
echo "Build Complete!"
echo "========================================="
echo ""
echo "Executable created: dist/ascii-video-chat"
echo ""
echo "To test:"
echo "  Host:    ./dist/ascii-video-chat --host --device 0"
echo "  Connect: ./dist/ascii-video-chat --connect 192.168.1.100 --device 0"
echo ""
echo "To distribute: Copy dist/ascii-video-chat to other computer"
echo ""
