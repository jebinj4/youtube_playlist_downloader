@echo off
title YouTube Playlist Downloader (Live Run)
cd /d "%~dp0\.."

if not exist ".venv_win" (
    echo Creating virtual environment...
    python -m venv .venv_win
    call .venv_win\Scripts\activate.bat
    pip install -r requirements.txt
    pip install pythonnet pywebview
) else (
    call .venv_win\Scripts\activate.bat
)

python app.py
pause
