@echo off
setlocal enabledelayedexpansion

title YouTube Playlist Downloader - Windows Build Tool
echo =====================================================================
echo   YouTube Playlist Downloader PRO v2.0 - 1-Click Windows Build Tool
echo   Developed by Just Rise Technologies W.L.L. (Kingdom of Bahrain)
echo =====================================================================
echo.

cd /d "%~dp0\.."

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3 is not found in your system PATH!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/4] Setting up dedicated Python Virtual Environment...
if not exist ".venv_win" (
    python -m venv .venv_win
)

call .venv_win\Scripts\activate.bat

echo [2/4] Installing dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
python -m pip install pyinstaller pythonnet pywebview --quiet

echo [3/4] Generating Windows Icon...
python build_windows\generate_ico.py

echo [4/4] Compiling Standalone Windows Application with PyInstaller...
if exist "dist\YouTube Playlist Downloader" (
    rmdir /s /q "dist\YouTube Playlist Downloader"
)

pyinstaller --noconfirm --clean build_windows\youtube_downloader.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo   [SUCCESS] Windows Application Build Complete!
    echo.
    echo   Location:
    echo   %CD%\dist\YouTube Playlist Downloader\YouTube_Playlist_Downloader.exe
    echo.
    echo   You can run the application directly or distribute the entire
    echo   "dist\YouTube Playlist Downloader" folder.
    echo =====================================================================
    echo.
) else (
    echo.
    echo [ERROR] Build failed. Please inspect the logs above.
    echo.
)

pause
