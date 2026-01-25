#!/bin/bash
# Quick setup script for macOS/Linux

echo "========================================="
echo "ASCII Video Chat - Quick Setup"
echo "========================================="
echo ""

echo "Step 1: Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi

python3 --version
echo ""

echo "Step 2: Installing dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "Quick Test Options:"
echo ""
echo "1. Test camera and ASCII conversion:"
echo "   python3 test_pipeline.py"
echo ""
echo "2. Start a localhost chat (need 2 terminals):"
echo "   Terminal 1: python3 main.py --host"
echo "   Terminal 2: python3 main.py --connect 127.0.0.1"
echo ""
echo "3. Chat over network:"
echo "   Computer 1: python3 main.py --host"
echo "   Computer 2: python3 main.py --connect [IP_ADDRESS]"
echo ""
echo "Press Enter to test your camera..."
read

python3 test_pipeline.py
