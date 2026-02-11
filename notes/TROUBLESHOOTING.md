# Fixing Color Display Issues

## Step 1: Update ascii_converter.py

The file needs to be replaced. You have two files:
- `ascii_converter.py` (old version)
- `ascii_converter_new.py` (new version with colors)

**Manually replace:**
1. Delete `ascii_converter.py`
2. Rename `ascii_converter_new.py` to `ascii_converter.py`

**Or run:**
```cmd
update_converter.bat
```

**Verify it worked:**
```cmd
check_update.bat
```

## Step 2: Test Camera (Without Colors First)

```cmd
python debug_camera.py
```

This will:
- Ask for your camera device (enter 1)
- Ask for color mode (choose 1 for Black & White first)
- Capture 5 test frames
- Show detailed output

**What to look for:**
- ✓ "Camera opened!"
- ✓ "Captured [640, 480, 3]" or similar
- ✓ "ASCII: XX lines generated"
- ✓ Preview shows actual ASCII characters

## Step 3: Simple Color Test

```cmd
python test_color.py
```

This shows 3 frames in black & white mode first (safest).

## Step 4: Run Main Application

```cmd
python main.py --host --device 1
```

Now it will ASK you which color mode before starting!

Options when asked:
1. Rainbow Heatmap
2. Black & White (safest if colors aren't working)
3. Normal Colors

## Common Issues & Fixes

### Issue: "Only a few colored lines appear"

**Cause:** Terminal doesn't support ANSI colors OR aspect ratio too small

**Fix:**
1. Use Windows Terminal (not CMD) for best color support
2. Try black & white mode: `--color bw`
3. Increase width: `--width 60`

### Issue: "Camera image distorted"

**Fix:**
1. Make terminal window larger (at least 120 columns wide)
2. Try: `python main.py --host --device 1 --width 40 --color bw`
3. Adjust width until it looks right

### Issue: "Test crashes"

**Cause:** Import error or camera access issue

**Fix:**
1. Run `update_converter.bat` first
2. Close other apps using camera
3. Try `python debug_camera.py` for detailed error

### Issue: "No colors showing"

**Cause:** Terminal doesn't support 24-bit color

**Fix:**
1. Use Windows Terminal instead of CMD
2. Or use: `--color bw` for black & white

## Best Settings for Testing

### For Clear Display:
```cmd
python main.py --host --device 1 --color bw --width 50
```

### For Colors (needs Windows Terminal):
```cmd
python main.py --host --device 1 --color rainbow --width 50
```

### For Maximum Detail:
```cmd
python main.py --host --device 1 --color bw --width 70
```

## Terminal Requirements

**For Colors to Work:**
- Windows Terminal (recommended)
- PowerShell 7+
- Modern terminal with 24-bit color support

**CMD (Command Prompt) limitations:**
- May not show colors properly
- Use `--color bw` for CMD

## Debugging Steps

1. First ensure camera works: `python debug_camera.py`
2. Test without colors: `python test_color.py`
3. Try main app with BW: `python main.py --host --device 1 --color bw`
4. If BW works, try colors: `python main.py --host --device 1 --color rainbow`

## Width Guide

- **40** - Narrow, fast, low detail
- **50** - Default, balanced
- **60** - More detail, needs wider terminal
- **70+** - High detail, needs large terminal (120+ columns)

Terminal width needed = (ASCII width × 2) + 10
- Width 40 → Need 90 column terminal
- Width 50 → Need 110 column terminal
- Width 60 → Need 130 column terminal
