@echo off
echo =========================================
echo Updating ASCII Converter
echo =========================================
echo.

if exist ascii_converter_new.py (
    echo Found new converter file!
    echo Backing up old file...
    if exist ascii_converter.py (
        copy ascii_converter.py ascii_converter.backup.py >nul
        echo Old file backed up to ascii_converter.backup.py
    )
    
    echo Installing new file...
    del ascii_converter.py 2>nul
    ren ascii_converter_new.py ascii_converter.py
    
    if exist ascii_converter.py (
        echo.
        echo =========================================
        echo SUCCESS! File updated successfully
        echo =========================================
        echo.
        echo Test it with:
        echo   python ascii_converter.py
        echo.
    ) else (
        echo ERROR: Update failed!
    )
) else (
    echo ERROR: ascii_converter_new.py not found!
    echo The file may not have been created yet.
)

pause

