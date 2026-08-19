# ACTIVITES LOG: YouTube Playlist Downloader

All system operations, installations, updates, and major feature executions are logged here chronologically.

| Date / Time | Action / Step | Details | Status |
| :--- | :--- | :--- | :--- |
| 2026-08-19 | Project Initialization | Established project architecture for 5-worker parallel YouTube playlist downloader. | Completed |
| 2026-08-19 | Technical Doc Creation | Created `TECHNICAL_DOC.md` outlining data models, workflow, and engine specs. | Completed |
| 2026-08-19 | Logging Setup | Initialized `ActivitesLog.MD` and `ErrorFixLog.MD`. | Completed |
| 2026-08-19 | Configuration Setup | Created `config.json` with default save path `/Volumes/External Storage SSD 1/DJ`. | Completed |
| 2026-08-19 | Core Downloader Engine | Created `parallel_downloader.py` with flat-metadata analyzer, 5-worker ThreadPoolExecutor, and ID3/Cover Art tagger. | Completed |
| 2026-08-19 | UI Design System & Dashboard | Created `ui/style.css`, `ui/index.html`, and `ui/app.js` with dark studio theme. | Completed |
| 2026-08-19 | Application & Native Window | Created `app.py` combining PyWebView macOS desktop window with REST/HTTP API server fallback. | Completed |
| 2026-08-19 | 1-Click Mac Launcher | Created executable `Start_DJ_Downloader.command` for direct desktop launching. | Completed |
| 2026-08-19 | Launcher Environment Fix | Added auto-creation of dedicated `.venv` in launcher to ensure dependency isolation and error visibility. | Completed |
| 2026-08-19 | Static FFmpeg & Unicode Engine Update | Added `static-ffmpeg` and `imageio-ffmpeg` to provide zero-config native ffmpeg binaries on macOS, and enhanced Unicode/Tamil title handling. | Completed |
| 2026-08-19 | YouTube Anti-Bot Bypass & Cookies | Added Android/iOS mobile client signature emulation in `yt-dlp` and added browser cookie selector (`Safari`, `Chrome`, `Brave`, `Firefox`) in UI. | Completed |
| 2026-08-19 | UI Refinement & Rebranding | Rebranded to **YouTube Playlist Downloader**, added selective track checkboxes, built-in floating audio player preview, and new playlist reset flow. | Completed |
| 2026-08-19 | Native `.app` & Styled `.dmg` Installer Build | Generated native macOS app bundle and commercial installer `YouTube_Playlist_Downloader_v2.0.dmg` with branded background graphic and drag-to-install arrow. | Completed |
| 2026-08-19 | Git Repository Migration | Synced clean source code, UI, build assets, documentation, and `.gitignore` to `/Volumes/Files/AppDev/justrise_bahrain/youtube_playlist` for version control. | Completed |
