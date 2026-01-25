@echo off
REM Quick test script for ASCII Video Chat

echo =========================================
echo ASCII Video Chat - Quick Test
echo =========================================
echo.

echo Step 1: Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo.

echo Step 2: Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo =========================================
echo Installation complete!
echo =========================================
echo.
echo Quick Test Options:
echo.
echo 1. Test camera and ASCII conversion:
echo    python test_pipeline.py
echo.
echo 2. Start a localhost chat (need 2 terminals):
echo    Terminal 1: python main.py --host
echo    Terminal 2: python main.py --connect 127.0.0.1
echo.
echo 3. Chat over network:
echo    Computer 1: python main.py --host
echo    Computer 2: python main.py --connect [IP_ADDRESS]
echo.
echo Press any key to test your camera...
pause > nul

python test_pipeline.py
