#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

VOL_NAME="YouTube Playlist Downloader"
DMG_FINAL="$DIR/YouTube_Playlist_Downloader_v2.0.dmg"
DMG_TEMP="/tmp/yt_temp.dmg"
MOUNT_DIR="/Volumes/$VOL_NAME"

# Unmount any existing instances
if [ -d "$MOUNT_DIR" ]; then
    hdiutil detach "$MOUNT_DIR" -force 2>/dev/null || true
fi

rm -f "$DMG_TEMP" "$DMG_FINAL"

echo "Creating temporary DMG..."
hdiutil create -size 300m -fs HFS+ -volname "$VOL_NAME" "$DMG_TEMP"

echo "Mounting temporary DMG..."
hdiutil attach "$DMG_TEMP" -readwrite -mountpoint "$MOUNT_DIR"

echo "Copying application and assets..."
cp -R "$DIR/YouTube Playlist Downloader.app" "$MOUNT_DIR/"
ln -s /Applications "$MOUNT_DIR/Applications"

mkdir -p "$MOUNT_DIR/.background"
cp "$DIR/build_assets/dmg_background.png" "$MOUNT_DIR/.background/"

echo "Styling DMG window via AppleScript..."
osascript <<EOF
tell application "Finder"
    tell disk "$VOL_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {300, 150, 960, 550}
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 96
        set background picture of theViewOptions to file ".background:dmg_background.png"
        set position of item "YouTube Playlist Downloader.app" of container window to {160, 200}
        set position of item "Applications" of container window to {500, 200}
        update without registering applications
        delay 2
        close
    end tell
end tell
EOF

sync
sleep 2

echo "Unmounting temporary DMG..."
hdiutil detach "$MOUNT_DIR" -force

echo "Compressing into final read-only DMG..."
hdiutil convert "$DMG_TEMP" -format UDZO -imagekey zlib-level=9 -o "$DMG_FINAL"
rm -f "$DMG_TEMP"

echo "✅ Styled DMG created successfully at: $DMG_FINAL"
