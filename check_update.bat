@echo off
echo Checking if ascii_converter.py is updated...
findstr /C:"color_mode" ascii_converter.py >nul
if %errorlevel% equ 0 (
    echo ✓ File is updated!
    echo.
    echo You can now run:
    echo   python debug_camera.py
    echo   python main.py --host --device 1
) else (
    echo ✗ File not updated yet
    echo Please run: update_converter.bat
)
pause
