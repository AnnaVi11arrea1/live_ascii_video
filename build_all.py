#!/usr/bin/env python3
"""
Universal build script for ASCII Video Chat
Detects platform and builds appropriate executable
"""
import platform
import subprocess
import sys
import os

def main():
    system = platform.system().lower()
    
    print("=" * 50)
    print("ASCII Video Chat - Universal Build Script")
    print("=" * 50)
    print(f"\nDetected platform: {platform.system()}")
    print()
    
    # Install PyInstaller
    print("Step 1: Installing PyInstaller...")
    pip_cmd = "pip" if system == "windows" else "pip3"
    result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          capture_output=True)
    
    if result.returncode != 0:
        print("ERROR: Failed to install PyInstaller")
        print(result.stderr.decode())
        return 1
    
    print("✓ PyInstaller installed")
    print()
    
    # Build executable
    print("Step 2: Building executable...")
    print("This may take a few minutes...")
    print()
    
    exe_name = "ascii-video-chat"
    
    # Determine the data separator for --add-data (Windows uses ; , Unix uses :)
    data_separator = ";" if system == "windows" else ":"
    add_data_arg = f"sounds{data_separator}sounds"
    
    if system == "windows":
        exe_name += ".exe"
    
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "ascii-video-chat",
        "--console",
        "--add-data", add_data_arg,
        "main.py"
    ])
    
    if result.returncode != 0:
        print("\nERROR: Build failed")
        return 1
    
    print()
    print("=" * 50)
    print("Build Complete!")
    print("=" * 50)
    print()
    print(f"Executable created: dist/{exe_name}")
    print()
    print("To test:")
    
    if system == "windows":
        print(f"  Host:    dist\\{exe_name} --host --device 1")
        print(f"  Connect: dist\\{exe_name} --connect 192.168.1.100 --device 1")
    else:
        print(f"  Host:    ./dist/{exe_name} --host --device 0")
        print(f"  Connect: ./dist/{exe_name} --connect 192.168.1.100 --device 0")
    
    print()
    print(f"To distribute: Copy dist/{exe_name} to another {platform.system()} computer")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
