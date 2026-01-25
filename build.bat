@echo off
REM Build script for creating Windows executable

echo =========================================
echo ASCII Video Chat - Build Executable
echo =========================================
echo.

echo Step 1: Installing PyInstaller...
python -m pip install PyInstaller

if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo.

echo Step 2: Building executable...
echo This may take a few minutes...
echo.

python -m PyInstaller --onefile --name ascii-video-chat --console main.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo.

echo =========================================
echo Build Complete!
echo =========================================
echo.
echo Executable created: dist\ascii-video-chat.exe
echo.
echo To test:
echo   Host:    dist\ascii-video-chat.exe --host --device 1
echo   Connect: dist\ascii-video-chat.exe --connect 192.168.1.100 --device 1
echo.
echo To distribute: Copy dist\ascii-video-chat.exe to other computer
echo.
pause
