# TECHNICAL DOCUMENTATION: YouTube Playlist Downloader PRO

## 1. System Overview
The **YouTube Playlist Downloader** is a high-performance macOS desktop application engineered for fast, lossless audio downloading from YouTube playlists. It downloads tracks across 5 parallel turbo workers, automatically organizing files into dedicated subfolders named after the playlist inside a customizable default base directory (`/Volumes/External Storage SSD 1/DJ`).

---

## 2. macOS Application & Installer Packaging

### 2.1 Native `.app` Bundle
- **Location**: `YouTube Playlist Downloader.app`
- **Icon**: High-resolution `AppIcon.icns` embedded in `Contents/Resources/`.
- **Self-Contained Code**: Complete application code (`app.py`, `parallel_downloader.py`, `ui/`, `requirements.txt`, `config.json`) bundled directly in `Contents/Resources/`.
- **Execution Model**: Runs completely silently via `Contents/MacOS/launcher`.
- **Environment Management**: Automatically creates and maintains an isolated virtual environment in `~/Library/Application Support/YouTubePlaylistDownloader/.venv`, ensuring seamless execution regardless of installation location (e.g. `/Applications` or external drives) without root permission constraints.
- **Error Handling**: Displays native macOS alert dialogs via AppleScript if an unexpected issue occurs, logging details to `~/Library/Application Support/YouTubePlaylistDownloader/app_launch.log`.

### 2.2 Commercial `.dmg` Installer
- **File**: `YouTube_Playlist_Downloader_v2.0.dmg`
- **Format**: UDZO Compressed Apple Disk Image with custom background styling and drag-to-install `/Applications` link.
- **Workflow**: Double-clicking mounts the disk image showing the Application icon and a direct symlink to `/Applications` for standard macOS drag-and-drop installation.

---

## 3. Directory & Storage Architecture

### Base Path Configuration
- **Default Base Directory**: `/Volumes/External Storage SSD 1/DJ`
- **Configuration File**: `config.json` (persists user-defined path, audio format, browser cookies, and parallel worker count).
- **Target Folder Structure**:
  ```
  /Volumes/External Storage SSD 1/DJ/
  └── <Sanitized Playlist Title>/
      ├── 01 - <Artist> - <Track Title>.mp3
      ├── 02 - <Artist> - <Track Title>.mp3
      └── ...
  ```

---

## 4. Core Components

### 4.1 Metadata Extraction & Selective Downloads (`analyze_playlist`)
- **Engine**: `yt-dlp` in flat-extraction mode (`extract_flat=True`).
- **Anti-Bot Mobile Emulation**: Passes `player_client: ["android", "ios", "mweb", "web"]` to bypass web captcha blocks.
- **Selective Track Checkboxes**: Allows users to selectively check/uncheck individual tracks or select all.
- **Speed**: Fetches complete playlist metadata in ~1–3 seconds without downloading video/audio streams.

### 4.2 In-App Audio Preview Player (`get_track_audio_stream_url`)
- Directly fetches the audio stream URL for any track in the playlist.
- Plays instant in-app audio previews inside the floating bottom player bar with seek and volume control.

### 4.3 5x Parallel Download Engine (`download_playlist_parallel`)
- **Concurrency**: Python `concurrent.futures.ThreadPoolExecutor(max_workers=5)`
- **Task Queue**: Partitioned across 5 worker threads.
- **Audio Processing Pipeline**:
  1. Extract best audio stream via `yt-dlp` mobile client signatures.
  2. Convert audio to target format using bundled native `static-ffmpeg` / `imageio-ffmpeg`:
     - **MP3 320kbps**: `-codec:a libmp3lame -b:a 320k`
     - **M4A**: `-codec:a aac -b:a 256k`
     - **FLAC**: `-codec:a flac`
  3. Fetch high-resolution thumbnail and embed as ID3 `APIC` frame / cover art.
  4. Write ID3v2.3 tags (`mutagen.id3`):
     - `TIT2` (Title)
     - `TPE1` (Artist)
     - `TALB` (Album = Playlist Name)
     - `TRCK` (Track Number formatted as `01`, `02`, etc.)
  5. Resume / Skip logic: Checks if destination file exists and is non-empty before downloading.

### 4.4 Application Architecture & UI
- **Desktop Window**: `pywebview` (native macOS WebKit window) with local server fallback (`http://127.0.0.1:8765`).
- **Responsive Fluid Layout**: Adapts dynamically across 100% of available screen width, seamlessly supporting small laptop screens up to 4K / Ultrawide displays without fixed width black borders.
- **Top Navigation & Multi-View Architecture**:
  - **New Playlist Tab**: Dedicated workspace for pasting URLs, selecting formats, choosing cookie auth, previewing audio tracks, and selective checkbox picking.
  - **Active Downloads & Queue Tab**: Non-blocking background download manager featuring real-time 5-worker turbo progress bars, multi-batch job cards, transfer speeds, and Finder reveal buttons.
  - **About Us Tab**: Company profile for **Just Rise Technologies W.L.L.** (Bahrain), with direct interactive links to website (`https://justrise.bh`), email (`info@justrise.bh`), phone (`+973 33051719`), and product specifications.
- **Backend API Bridge**:
  - `api.get_config()`: Retrieves save path, cookies, and preferences (with smart fallback to `~/Music/YouTube Downloads` when external SSD is absent)
  - `api.save_config(path, format, cookies)`: Updates configuration
  - `api.select_folder()`: Native macOS folder picker dialog
  - `api.analyze_playlist(url, cookies)`: Fetches playlist metadata
  - `api.get_audio_preview(video_id, cookies)`: Fetches preview stream
  - `api.start_download(playlist_data, options)`: Launches 5-worker download pool in background
  - `api.open_folder(path)`: Reveals directory in macOS Finder
  - `api.open_url(url)`: Launches external links / emails in default browser or mail client
- **Frontend Stack**: Professional Solid Dark Theme (Obsidian Black `#0b0d13`, Slate Surfaces `#12151d`, Crisp YouTube Red `#e50914`, Solid Emerald `#10b981`), Zero Gradients, Zero Neon Glows, Vanilla HTML5/CSS3/JavaScript.

---

## 5. Data Models

### Playlist Metadata Model
```json
{
  "playlist_id": "PL4fGHI...",
  "playlist_title": "Dj Tamil Remix Songs",
  "folder_path": "/Volumes/External Storage SSD 1/DJ/Dj Tamil Remix Songs",
  "track_count": 118,
  "tracks": [
    {
      "index": 1,
      "id": "dQw4w9WgXcQ",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "title": "Flame",
      "artist": "ARTBAT",
      "duration": 394,
      "duration_formatted": "6:34",
      "thumbnail": "https://i.ytimg.com/vi/...",
      "status": "Queued",
      "selected": true
    }
  ]
}
```

### Worker Progress Event Model
```json
{
  "worker_id": 1,
  "track_index": 1,
  "track_title": "Flame",
  "artist": "ARTBAT",
  "status": "downloading",
  "percent": 68.5,
  "speed_str": "4.2 MB/s",
  "eta_str": "00:08",
  "overall_completed": 14,
  "overall_total": 45
}
```
