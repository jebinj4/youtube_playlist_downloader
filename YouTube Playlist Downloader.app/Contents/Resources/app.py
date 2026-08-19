import os
import sys
import json
import subprocess
import threading
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse

# Auto-add static ffmpeg binaries to PATH
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

# Set macOS Process and Menu Bar title from 'Python' to 'YouTube Playlist Downloader'
if sys.platform == "darwin":
    try:
        from Foundation import NSProcessInfo
        NSProcessInfo.processInfo().setProcessName_("YouTube Playlist Downloader")
    except Exception:
        pass

from parallel_downloader import (
    analyze_playlist,
    ParallelDownloader,
    sanitize_name,
    get_track_audio_stream_url
)

if sys.platform == "win32":
    SUPPORT_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "YouTubePlaylistDownloader")
else:
    SUPPORT_DIR = os.path.expanduser("~/Library/Application Support/YouTubePlaylistDownloader")

USER_CONFIG_FILE = os.path.join(SUPPORT_DIR, "config.json")
LOCAL_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
HISTORY_FILE = os.path.join(SUPPORT_DIR, "history.json")
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")

# Global downloader instance
downloader = ParallelDownloader(max_workers=5)
current_window = None


def get_active_config_path() -> str:
    if os.path.exists(USER_CONFIG_FILE):
        return USER_CONFIG_FILE
    if os.path.exists(LOCAL_CONFIG_FILE):
        return LOCAL_CONFIG_FILE
    return USER_CONFIG_FILE


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []


def save_history_data(history_list: list) -> bool:
    try:
        os.makedirs(SUPPORT_DIR, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=2)
        return True
    except Exception:
        return False


def clear_history_data() -> bool:
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        return True
    except Exception:
        return False


def load_config() -> dict:
    if sys.platform == "win32":
        default_save = "D:\\DJ" if os.path.exists("D:\\DJ") else os.path.join(os.path.expanduser("~"), "Music", "YouTube Downloads")
    else:
        default_save = "/Volumes/External Storage SSD 1/DJ" if os.path.exists("/Volumes/External Storage SSD 1/DJ") else os.path.expanduser("~/Music/YouTube Downloads")

    default_cfg = {
        "default_save_path": default_save,
        "default_format": "mp3_320k",
        "browser_cookies": "none",
        "parallel_workers": 5,
        "embed_thumbnail": True,
        "embed_metadata": True,
        "auto_open_folder": True
    }
    cfg_path = get_active_config_path()
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_cfg.update(saved)
                # If the saved path doesn't exist on this system, fallback gracefully
                if default_cfg.get("default_save_path") and not os.path.exists(default_cfg["default_save_path"]):
                    if not default_cfg["default_save_path"].startswith(os.path.expanduser("~")):
                        default_cfg["default_save_path"] = default_save
        except Exception:
            pass
    return default_cfg


def save_config_file(cfg: dict) -> bool:
    try:
        os.makedirs(SUPPORT_DIR, exist_ok=True)
        with open(USER_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        try:
            with open(LOCAL_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass
        return True
    except Exception:
        return False


def native_select_folder(initial_dir: str = "") -> str:
    """Use native folder dialog for macOS and Windows."""
    global current_window
    if current_window:
        try:
            import webview
            result = current_window.create_file_dialog(webview.FOLDER_DIALOG, directory=initial_dir)
            if result and len(result) > 0:
                return result[0]
        except Exception:
            pass
    if sys.platform == "darwin":
        try:
            cmd = """osascript -e 'set chosenFolder to choose folder with prompt "Select Default Download Folder:"' -e 'POSIX path of chosenFolder'"""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
    elif sys.platform == "win32":
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askdirectory(title="Select Default Download Folder")
            root.destroy()
            if chosen:
                return chosen
        except Exception:
            pass
    return ""


def native_open_folder(folder_path: str):
    """Open folder in macOS Finder or Windows Explorer."""
    if not folder_path:
        return
    try:
        os.makedirs(folder_path, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
    except Exception:
        pass


class AppAPIBridge:
    """API bridge exposed directly to PyWebView JavaScript runtime."""

    def get_config(self):
        return load_config()

    def save_config(self, cfg):
        save_config_file(cfg)
        return {"success": True}

    def select_folder(self):
        chosen = native_select_folder()
        if chosen:
            cfg = load_config()
            cfg["default_save_path"] = chosen
            save_config_file(cfg)
            return {"success": True, "path": chosen}
        return {"success": False, "path": ""}

    def analyze_playlist(self, url: str, browser_cookies: str = "none"):
        return analyze_playlist(url, browser_cookies)

    def get_audio_preview(self, video_id: str, browser_cookies: str = "none"):
        return get_track_audio_stream_url(video_id, browser_cookies)

    def start_download(self, payload: dict):
        tracks = payload.get("tracks", [])
        playlist_title = payload.get("playlist_title", "Playlist")
        base_dir = payload.get("base_dir") or load_config().get("default_save_path", "/Volumes/External Storage SSD 1/DJ")
        audio_format = payload.get("audio_format", "mp3_320k")
        browser_cookies = payload.get("browser_cookies", "none")

        def on_progress(data):
            if current_window:
                try:
                    js_code = f"if(window.onWorkerProgress) window.onWorkerProgress({json.dumps(data)});"
                    current_window.evaluate_js(js_code)
                except Exception:
                    pass

        def on_complete(data):
            if current_window:
                try:
                    js_code = f"if(window.onDownloadComplete) window.onDownloadComplete({json.dumps(data)});"
                    current_window.evaluate_js(js_code)
                except Exception:
                    pass
            cfg = load_config()
            if cfg.get("auto_open_folder") and data.get("target_dir"):
                native_open_folder(data.get("target_dir"))

        target_dir = downloader.start_parallel_download(
            tracks=tracks,
            playlist_title=playlist_title,
            base_dir=base_dir,
            audio_format=audio_format,
            browser_cookies=browser_cookies,
            progress_callback=on_progress,
            completion_callback=on_complete
        )

        return {"success": True, "target_dir": target_dir}

    def cancel_download(self):
        downloader.cancel()
        return {"success": True}

    def open_folder(self, folder_path: str):
        native_open_folder(folder_path)
        return {"success": True}

    def open_url(self, url: str):
        if url and (url.startswith("http://") or url.startswith("https://") or url.startswith("mailto:") or url.startswith("tel:")):
            try:
                import webbrowser
                webbrowser.open(url)
                return {"success": True}
            except Exception:
                if sys.platform == "darwin":
                    subprocess.run(["open", url])
                elif sys.platform == "win32":
                    os.startfile(url)
                return {"success": True}
        return {"success": False}

    def get_history(self):
        return load_history()

    def save_history(self, history_list):
        save_history_data(history_list)
        return {"success": True}

    def clear_history(self):
        clear_history_data()
        return {"success": True}


# Local HTTP Handler supporting static UI and REST API fallback
class CustomHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/config":
            self.send_json_response(load_config())
        elif self.path == "/api/history":
            self.send_json_response(load_history())
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        bridge = AppAPIBridge()

        if parsed.path == "/api/config":
            res = bridge.save_config(data)
            self.send_json_response(res)
        elif parsed.path == "/api/history":
            res = bridge.save_history(data if isinstance(data, list) else data.get("history", []))
            self.send_json_response(res)
        elif parsed.path == "/api/clear_history":
            res = bridge.clear_history()
            self.send_json_response(res)
        elif parsed.path == "/api/select_folder":
            res = bridge.select_folder()
            self.send_json_response(res)
        elif parsed.path == "/api/analyze":
            url = data.get("url", "")
            cookies = data.get("browser_cookies", "none")
            res = bridge.analyze_playlist(url, cookies)
            self.send_json_response(res)
        elif parsed.path == "/api/preview":
            vid = data.get("video_id", "")
            cookies = data.get("browser_cookies", "none")
            res = bridge.get_audio_preview(vid, cookies)
            self.send_json_response(res)
        elif parsed.path == "/api/download":
            res = bridge.start_download(data)
            self.send_json_response(res)
        elif parsed.path == "/api/cancel":
            res = bridge.cancel_download()
            self.send_json_response(res)
        elif parsed.path == "/api/open_folder":
            folder = data.get("folder_path", "")
            res = bridge.open_folder(folder)
            self.send_json_response(res)
        elif parsed.path == "/api/open_url":
            url = data.get("url", "")
            res = bridge.open_url(url)
            self.send_json_response(res)
        else:
            self.send_error(404, "Endpoint not found")

    def send_json_response(self, obj):
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def find_free_port(start_port=8765):
    port = start_port
    while port < 8800:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return start_port


def start_server(port):
    server = HTTPServer(("127.0.0.1", port), CustomHTTPHandler)
    server.serve_forever()


def main():
    global current_window
    port = find_free_port(8765)
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{port}/index.html"
    bridge = AppAPIBridge()

    try:
        import webview
        current_window = webview.create_window(
            title="YouTube Playlist Downloader",
            url=url,
            js_api=bridge,
            width=1260,
            height=880,
            min_size=(980, 700),
            background_color="#0b0d13"
        )
        webview.start(debug=False)
    except Exception as e:
        print(f"[YouTube Playlist Downloader] PyWebView not active, opening in browser: {e}")
        subprocess.run(["open", url])
        try:
            while True:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
