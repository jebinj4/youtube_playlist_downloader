# ERROR FIX LOG: DJ YouTube Playlist Downloader

This file logs all encountered errors, exceptions, root cause analyses, and solutions implemented.

| Date / Time | Error Code / Summary | Component | Root Cause | Solution Implemented |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-19 | Initial Setup | System | N/A | System initialized cleanly. |
| 2026-08-19 | `ModuleNotFoundError: No module named 'yt_dlp'` | Launcher (`Start_DJ_Downloader.command`) | macOS PEP 668 externally managed environment blocked system pip installs, and stderr was suppressed (`2>/dev/null`). | Updated launcher to create and activate a dedicated `.venv` virtual environment, install requirements cleanly, and keep terminal open on exit. |
| 2026-08-19 | All downloads failed at 0% with `PostProcessingError` | Downloader Engine (`parallel_downloader.py`) | Missing `ffmpeg` binary on macOS for MP3 audio conversion and non-ASCII/Tamil title sanitization. | Added `static-ffmpeg` and `imageio-ffmpeg` to `requirements.txt` to auto-provide native macOS ffmpeg binaries, configured `ffmpeg_location` in `yt-dlp`, and added error tooltips in UI. |
| 2026-08-19 | `Sign in to confirm you’re not a bot` | Downloader Engine (`parallel_downloader.py`) | YouTube web player anti-bot protection triggered during fast concurrent audio downloads. | Configured `yt-dlp` `extractor_args` to emulate official Android & iOS mobile app clients (`player_client: ["android", "ios", "mweb", "web"]`), bypassing web bot checks, and added native Mac browser cookie integration (`Safari`, `Chrome`, `Brave`, `Firefox`) in UI. |
