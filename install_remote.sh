#!/usr/bin/env bash
set -euo pipefail
DEST="${HOME}/Music/Ableton/User Library/Remote Scripts/AbletonMCP"
mkdir -p "$DEST"
cp ableton_live_mcp/remote_script/__init__.py "$DEST/__init__.py"
echo "Remote Script copied to $DEST"
echo "Restart Ableton Live and enable AbletonMCP in Preferences > Link/Tempo/MIDI"
