import os
import re
import io
import time
import urllib.request
import threading
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp

# Automatically add static ffmpeg paths if available
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

try:
    import imageio_ffmpeg
    STATIC_FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    STATIC_FFMPEG_EXE = None

try:
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.flac import FLAC, Picture
    from PIL import Image
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


def get_ffmpeg_location():
    """Detect available ffmpeg executable path."""
    if STATIC_FFMPEG_EXE and os.path.exists(STATIC_FFMPEG_EXE):
        return STATIC_FFMPEG_EXE
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    return None


def sanitize_name(name: str) -> str:
    """Sanitize strings for folder and file names while preserving Unicode (e.g. Tamil, Japanese, etc.)."""
    if not name:
        return "Unknown"
    cleaned = re.sub(r'[\\/*?:"<>|\x00-\x1f]', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(". ")
    return cleaned if cleaned else "Untitled"


def format_duration(seconds) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS."""
    if not seconds or not isinstance(seconds, (int, float)):
        return "--:--"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def parse_artist_title(raw_title: str, uploader: str = ""):
    """Parse 'Artist - Track Title' from YouTube title string."""
    title = raw_title.strip()
    separators = [" - ", " – ", " — ", " | "]
    artist = uploader or "Unknown Artist"
    track_title = title

    for sep in separators:
        if sep in title:
            parts = title.split(sep, 1)
            artist = parts[0].strip()
            track_title = parts[1].strip()
            break

    track_title = re.sub(r"(?i)\s*[\(\[]\s*(official\s*(music\s*)?(video|audio|visualizer|lyric video|hd|4k)?|lyrics|audio|video|visualizer|out now)\s*[\)\]]", "", track_title).strip()
    return sanitize_name(artist), sanitize_name(track_title)


def analyze_playlist(url: str, browser_cookies: str = "none") -> dict:
    """
    Fast extraction of playlist metadata using yt-dlp flat-playlist mode.
    Emulates mobile app clients to avoid YouTube bot-check.
    """
    ydl_opts = {
        "extract_flat": "in_playlist",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "ignoreerrors": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "mweb", "web"],
                "player_skip": ["webpage", "configs"]
            }
        }
    }

    if browser_cookies and browser_cookies.lower() != "none":
        try:
            ydl_opts["cookiesfrombrowser"] = (browser_cookies.lower(), None, None, None)
        except Exception:
            pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return {"success": False, "error": "Could not extract playlist information. Please check the URL."}

            playlist_title = sanitize_name(info.get("title") or "YouTube Playlist")
            playlist_id = info.get("id") or "playlist"
            
            entries = info.get("entries") or []
            if not entries and info.get("_type") != "playlist":
                entries = [info]
                playlist_title = sanitize_name(info.get("title") or "Single Download")

            tracks = []
            valid_index = 1
            for entry in entries:
                if not entry:
                    continue
                
                vid_id = entry.get("id")
                raw_title = entry.get("title") or "Untitled Track"
                uploader = entry.get("uploader") or entry.get("channel") or ""
                artist, clean_title = parse_artist_title(raw_title, uploader)
                duration = entry.get("duration")
                
                thumbnails = entry.get("thumbnails") or []
                thumbnail_url = ""
                if thumbnails:
                    thumbnail_url = thumbnails[-1].get("url", "")
                elif vid_id:
                    thumbnail_url = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"

                vid_url = entry.get("url") or entry.get("webpage_url")
                if not vid_url and vid_id:
                    vid_url = f"https://www.youtube.com/watch?v={vid_id}"

                tracks.append({
                    "index": valid_index,
                    "id": vid_id,
                    "url": vid_url,
                    "raw_title": raw_title,
                    "title": clean_title,
                    "artist": artist,
                    "duration": duration,
                    "duration_formatted": format_duration(duration),
                    "thumbnail": thumbnail_url,
                    "status": "Queued",
                    "selected": True
                })
                valid_index += 1

            if not tracks:
                return {"success": False, "error": "No downloadable tracks found in this playlist."}

            return {
                "success": True,
                "playlist_id": playlist_id,
                "playlist_title": playlist_title,
                "track_count": len(tracks),
                "tracks": tracks
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_track_audio_stream_url(video_id_or_url: str, browser_cookies: str = "none") -> dict:
    """Fetch direct audio stream URL for in-app preview playback."""
    url = video_id_or_url if video_id_or_url.startswith("http") else f"https://www.youtube.com/watch?v={video_id_or_url}"
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "mweb", "web"],
                "player_skip": ["webpage", "configs"]
            }
        }
    }
    if browser_cookies and browser_cookies.lower() != "none":
        try:
            ydl_opts["cookiesfrombrowser"] = (browser_cookies.lower(), None, None, None)
        except Exception:
            pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info.get("url")
            if not stream_url and "formats" in info:
                for f in reversed(info["formats"]):
                    if f.get("acodec") != "none" and f.get("url"):
                        stream_url = f["url"]
                        break
            return {"success": True, "stream_url": stream_url}
    except Exception as e:
        return {"success": False, "error": str(e)}


def tag_audio_file(file_path: str, track: dict, playlist_title: str, total_tracks: int):
    """Embed ID3 / MP4 / FLAC metadata and thumbnail cover art."""
    if not MUTAGEN_AVAILABLE or not os.path.exists(file_path):
        return

    ext = os.path.splitext(file_path)[1].lower()
    cover_bytes = None
    if track.get("thumbnail"):
        try:
            req = urllib.request.Request(
                track["thumbnail"],
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                raw_img = response.read()
                img = Image.open(io.BytesIO(raw_img))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img_out = io.BytesIO()
                img.save(img_out, format="JPEG", quality=95)
                cover_bytes = img_out.getvalue()
        except Exception:
            cover_bytes = None

    try:
        if ext == ".mp3":
            try:
                audio = EasyID3(file_path)
            except Exception:
                audio = EasyID3()
            audio["title"] = track["title"]
            audio["artist"] = track["artist"]
            audio["album"] = playlist_title
            audio["tracknumber"] = f"{track['index']}/{total_tracks}"
            audio.save(file_path)

            if cover_bytes:
                id3 = ID3(file_path)
                id3.add(APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=cover_bytes
                ))
                id3.save(file_path, v2_version=3)

        elif ext == ".m4a":
            audio = MP4(file_path)
            audio["\xa9nam"] = [track["title"]]
            audio["\xa9ART"] = [track["artist"]]
            audio["\xa9alb"] = [playlist_title]
            audio["trkn"] = [(track["index"], total_tracks)]
            if cover_bytes:
                audio["covr"] = [MP4Cover(cover_bytes, imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()

        elif ext == ".flac":
            audio = FLAC(file_path)
            audio["title"] = track["title"]
            audio["artist"] = track["artist"]
            audio["album"] = playlist_title
            audio["tracknumber"] = str(track["index"])
            audio["totaltracks"] = str(total_tracks)
            if cover_bytes:
                pic = Picture()
                pic.type = 3
                pic.mime = "image/jpeg"
                pic.desc = "Front Cover"
                pic.data = cover_bytes
                audio.add_picture(pic)
            audio.save()

    except Exception:
        pass


class ParallelDownloader:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def download_track_worker(
        self,
        worker_id: int,
        track: dict,
        total_tracks: int,
        playlist_title: str,
        target_dir: str,
        audio_format: str,
        browser_cookies: str,
        progress_callback
    ):
        if self.is_cancelled:
            return {"index": track["index"], "status": "Cancelled"}

        track_idx = track["index"]
        idx_prefix = f"{track_idx:02d}"
        filename_base = f"{idx_prefix} - {track['artist']} - {track['title']}"
        filename_base = sanitize_name(filename_base)

        ext_map = {
            "mp3_320k": "mp3",
            "mp3_256k": "mp3",
            "m4a": "m4a",
            "flac": "flac"
        }
        target_ext = ext_map.get(audio_format, "mp3")
        final_file_path = os.path.join(target_dir, f"{filename_base}.{target_ext}")

        # Skip if already downloaded
        if os.path.exists(final_file_path) and os.path.getsize(final_file_path) > 50000:
            progress_callback({
                "worker_id": worker_id,
                "track_index": track_idx,
                "track_title": track["title"],
                "artist": track["artist"],
                "status": "Downloaded",
                "percent": 100.0,
                "speed_str": "Skipped (Exists)",
                "eta_str": "Done"
            })
            return {"index": track_idx, "status": "Downloaded", "file": final_file_path}

        def ytdl_hook(d):
            if self.is_cancelled:
                raise Exception("Download cancelled by user.")
            if d["status"] == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                percent = (downloaded / total_bytes * 100) if total_bytes > 0 else 0.0
                speed_str = d.get("_speed_str") or "Downloading..."
                eta_str = d.get("_eta_str") or "--:--"

                progress_callback({
                    "worker_id": worker_id,
                    "track_index": track_idx,
                    "track_title": track["title"],
                    "artist": track["artist"],
                    "status": "Downloading",
                    "percent": round(percent, 1),
                    "speed_str": speed_str,
                    "eta_str": eta_str
                })
            elif d["status"] == "finished":
                progress_callback({
                    "worker_id": worker_id,
                    "track_index": track_idx,
                    "track_title": track["title"],
                    "artist": track["artist"],
                    "status": "Converting",
                    "percent": 99.0,
                    "speed_str": "Converting Audio...",
                    "eta_str": "00:01"
                })

        # Post-processor codec settings
        if audio_format in ("mp3_320k", "mp3_256k"):
            codec = "mp3"
            quality = "320" if audio_format == "mp3_320k" else "256"
        elif audio_format == "m4a":
            codec = "m4a"
            quality = "0"
        elif audio_format == "flac":
            codec = "flac"
            quality = "0"
        else:
            codec = "mp3"
            quality = "320"

        temp_template = os.path.join(target_dir, f"{filename_base}.%(ext)s")
        ffmpeg_bin = get_ffmpeg_location()

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": temp_template,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [ytdl_hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": quality,
            }],
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios", "mweb", "web"],
                    "player_skip": ["webpage", "configs"]
                }
            },
            "writethumbnail": False,
            "retries": 5,
            "fragment_retries": 5,
        }

        if ffmpeg_bin:
            ydl_opts["ffmpeg_location"] = ffmpeg_bin

        if browser_cookies and browser_cookies.lower() != "none":
            try:
                ydl_opts["cookiesfrombrowser"] = (browser_cookies.lower(), None, None, None)
            except Exception:
                pass

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([track["url"]])

            # Apply ID3 / Mutagen tagging & album art
            if os.path.exists(final_file_path):
                tag_audio_file(final_file_path, track, playlist_title, total_tracks)

            progress_callback({
                "worker_id": worker_id,
                "track_index": track_idx,
                "track_title": track["title"],
                "artist": track["artist"],
                "status": "Downloaded",
                "percent": 100.0,
                "speed_str": "Completed",
                "eta_str": "00:00"
            })
            return {"index": track_idx, "status": "Downloaded", "file": final_file_path}

        except Exception as e:
            err_msg = str(e)
            if "cancelled" in err_msg.lower():
                status = "Cancelled"
            else:
                status = "Failed"
            progress_callback({
                "worker_id": worker_id,
                "track_index": track_idx,
                "track_title": track["title"],
                "artist": track["artist"],
                "status": status,
                "percent": 0.0,
                "speed_str": "Error",
                "eta_str": err_msg[:50],
                "error_details": err_msg
            })
            return {"index": track_idx, "status": status, "error": err_msg}

    def start_parallel_download(
        self,
        tracks: list,
        playlist_title: str,
        base_dir: str,
        audio_format: str,
        browser_cookies: str,
        progress_callback,
        completion_callback
    ):
        self.is_cancelled = False
        target_dir = os.path.join(base_dir, sanitize_name(playlist_title))
        os.makedirs(target_dir, exist_ok=True)

        total_tracks = len(tracks)
        completed_count = 0

        available_workers = list(range(1, self.max_workers + 1))
        worker_lock = threading.Lock()

        def acquire_worker_id():
            with worker_lock:
                if available_workers:
                    return available_workers.pop(0)
                return 1

        def release_worker_id(wid):
            with worker_lock:
                if wid not in available_workers:
                    available_workers.append(wid)
                    available_workers.sort()

        def worker_task(track):
            wid = acquire_worker_id()
            try:
                res = self.download_track_worker(
                    wid,
                    track,
                    total_tracks,
                    playlist_title,
                    target_dir,
                    audio_format,
                    browser_cookies,
                    progress_callback
                )
                return res
            finally:
                release_worker_id(wid)

        def runner():
            nonlocal completed_count
            results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_track = {executor.submit(worker_task, t): t for t in tracks}
                for future in as_completed(future_to_track):
                    res = future.result()
                    results.append(res)
                    completed_count += 1

            completion_callback({
                "target_dir": target_dir,
                "total": total_tracks,
                "completed": completed_count,
                "is_cancelled": self.is_cancelled
            })

        t = threading.Thread(target=runner, daemon=True)
        t.start()
        return target_dir
