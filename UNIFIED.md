# Unified Ableton MCP

Foundation: wstierhout/ableton-live-mcp  
Grafted: nicholasbien warp markers + groove pool  
Batch: propagate_warp_markers / batch_add_warp_markers

## What was added

Remote Script (`ableton_live_mcp/remote_script/__init__.py`):
- get_warp_markers
- add_warp_marker
- move_warp_marker
- remove_warp_marker
- get_groove_pool
- set_groove_params

MCP tools (`ableton_live_mcp/tools/warp_groove.py`):
- matching wrappers + batch_add_warp_markers + propagate_warp_markers + set_clip_audio re-export

Registered in the `clips` tool group.

## Install Remote Script

From this directory (with uv or the project's install flow):

```bash
uvx --from . mcp-server-ableton-live install
# or copy ableton_live_mcp/remote_script to:
# ~/Music/Ableton/User Library/Remote Scripts/AbletonMCP/
```

Restart Ableton Live, enable the control surface, then run the server.

## Still not included

- set_1_1_1_here / warp_from_here
- tempo leader
- Seg. BPM
- track delay / utility phase
- live onset/correlation analysis
- full jpoindexter tool surface (only the batch pattern)

These can be added the same way later.
