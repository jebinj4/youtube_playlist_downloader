========================================================================
  YouTube Playlist Downloader PRO v2.0 - Windows Build Instructions
  Developed by Just Rise Technologies W.L.L. (https://justrise.bh)
========================================================================

HOW TO BUILD STANDALONE WINDOWS APP (.EXE):
--------------------------------------------
1. Copy or clone this project folder to your Windows PC/Laptop.
2. Make sure Python 3.9+ is installed with "Add Python to PATH" checked.
3. Open the "build_windows" folder.
4. Double-click:
   --> build_windows_exe.bat

The script will automatically:
- Create a dedicated virtual environment (.venv_win)
- Install all required dependencies (yt-dlp, static-ffmpeg, mutagen, pywebview, etc.)
- Compile the standalone executable using PyInstaller.
- Output the complete standalone app into:
   dist\YouTube Playlist Downloader\YouTube_Playlist_Downloader.exe

--------------------------------------------
HOW TO RUN LOCALLY WITHOUT COMPILING:
--------------------------------------------
1. Open the "build_windows" folder.
2. Double-click:
   --> run_dev_windows.bat

--------------------------------------------
HOW TO CREATE 1-FILE SETUP WIZARD (OPTIONAL):
--------------------------------------------
1. Install Inno Setup (Free: https://jrsoftware.org/isdl.php).
2. Right-click "build_windows\installer_inno_setup.iss" and select "Compile".
3. It will create "dist\YouTube_Playlist_Downloader_Setup_v2.0.exe".
========================================================================
