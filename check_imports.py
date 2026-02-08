"""
Quick diagnostic script to find the import error
"""
import sys
import traceback

print("Testing imports in order...\n")

# Test 1: Basic imports
try:
    import threading
    import time
    print("✓ threading, time")
except Exception as e:
    print(f"✗ Basic imports failed: {e}")
    sys.exit(1)

# Test 2: video_capture
try:
    from video_capture import VideoCapture
    print("✓ video_capture.VideoCapture")
except Exception as e:
    print(f"✗ video_capture failed:")
    traceback.print_exc()

# Test 3: ascii_converter
try:
    from ascii_converter import AsciiConverter
    print("✓ ascii_converter.AsciiConverter")
except Exception as e:
    print(f"✗ ascii_converter failed:")
    traceback.print_exc()

# Test 4: network
try:
    from network import NetworkConnection, NetworkServer
    print("✓ network.NetworkConnection, NetworkServer")
except Exception as e:
    print(f"✗ network failed:")
    traceback.print_exc()

# Test 5: terminal_ui
try:
    from terminal_ui import TerminalUI, InputHandler
    print("✓ terminal_ui.TerminalUI, InputHandler")
except Exception as e:
    print(f"✗ terminal_ui failed:")
    traceback.print_exc()

# Test 6: session
try:
    from session import ChatSession
    print("✓ session.ChatSession")
    print("\n✅ All imports successful!")
except Exception as e:
    print(f"✗ session.ChatSession failed:")
    traceback.print_exc()
