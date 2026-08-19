#!/bin/bash

# Change directory to the folder where this script is located
cd "$(dirname "$0")"

echo "=================================================="
echo "          YOUTUBE PLAYLIST DOWNLOADER             "
echo "           5x Turbo Parallel Engine               "
echo "=================================================="
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed on your Mac."
    echo "Please install Python 3 or brew install python"
    read -p "Press Enter to exit..."
    exit 1
fi

# Create dedicated virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "📦 Initializing isolated Python environment (.venv)..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install / update required packages
echo "🔍 Checking dependencies..."
python3 -m pip install --upgrade pip -q
python3 -m pip install -r requirements.txt

# Launch Application
echo ""
echo "🚀 Starting YouTube Playlist Downloader..."
python3 app.py

# If app exits with error, keep terminal window open
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️ Application stopped with an error."
    read -p "Press Enter to close this window..."
fi
