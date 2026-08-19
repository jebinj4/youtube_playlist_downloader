# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None
project_dir = os.path.abspath(os.path.join(SPECPATH, ".."))

added_files = [
    (os.path.join(project_dir, "ui"), "ui"),
    (os.path.join(project_dir, "config.json"), "."),
    (os.path.join(project_dir, "build_windows", "app_icon.ico"), ".")
]

hidden_imports = [
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.edgechromium',
    'static_ffmpeg',
    'imageio_ffmpeg',
    'mutagen',
    'mutagen.mp3',
    'mutagen.id3',
    'mutagen.flac',
    'mutagen.mp4',
    'yt_dlp',
    'yt_dlp.extractor',
    'yt_dlp.downloader',
    'yt_dlp.postprocessor',
    'urllib.parse',
    'http.server',
    'json',
    'socket',
    'threading',
    'tkinter',
    'tkinter.filedialog',
    'clr'
]

a = Analysis(
    [os.path.join(project_dir, 'app.py')],
    pathex=[project_dir],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['Foundation', 'AppKit', 'PyObjCTools', 'objc'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTube_Playlist_Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_dir, "build_windows", "app_icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTube Playlist Downloader',
)
