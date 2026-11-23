"""
Consolidated MCP tools for ableton-MCP (wstierhout foundation + nicholasbien warp/groove graft).

Drop into the tools package and import from tools/__init__.py.
All tools use the existing send_command socket path.
"""

import json
from mcp.server.fastmcp import Context
from mcp.types import ToolAnnotations

from ..app import mcp
from ..connection import get_ableton_connection


def _send(cmd: str, params: dict) -> str:
    return json.dumps(get_ableton_connection().send_command(cmd, params), indent=2)


# ── Warp markers (nicholasbien) ──────────────────────────────────────────────

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_warp_markers(ctx: Context, track_index: int, clip_index: int = 0,
                     arrangement_clip_index: int | None = None) -> str:
    """List warp markers on an audio clip (beat_time, sample_time)."""
    return _send("get_warp_markers", {
        "track_index": track_index,
        "clip_index": clip_index,
        "arrangement_clip_index": arrangement_clip_index,
    })


@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def add_warp_marker(ctx: Context, track_index: int, clip_index: int, beat_time: float,
                    sample_time: float | None = None,
                    arrangement_clip_index: int | None = None) -> str:
    """Add a warp marker. Requires warping on. sample_time pins that file second to beat_time."""
    return _send("add_warp_marker", {
        "track_index": track_index,
        "clip_index": clip_index,
        "beat_time": beat_time,
        "sample_time": sample_time,
        "arrangement_clip_index": arrangement_clip_index,
    })


@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def move_warp_marker(ctx: Context, track_index: int, clip_index: int,
                     beat_time: float, beat_time_distance: float,
                     arrangement_clip_index: int | None = None) -> str:
    """Move the marker at beat_time by beat_time_distance."""
    return _send("move_warp_marker", {
        "track_index": track_index,
        "clip_index": clip_index,
        "beat_time": beat_time,
        "beat_time_distance": beat_time_distance,
        "arrangement_clip_index": arrangement_clip_index,
    })


@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def remove_warp_marker(ctx: Context, track_index: int, clip_index: int, beat_time: float,
                       arrangement_clip_index: int | None = None) -> str:
    """Remove the warp marker at beat_time."""
    return _send("remove_warp_marker", {
        "track_index": track_index,
        "clip_index": clip_index,
        "beat_time": beat_time,
        "arrangement_clip_index": arrangement_clip_index,
    })


# ── Groove (nicholasbien; wstierhout already has basic set_clip_groove) ─────

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_groove_pool(ctx: Context) -> str:
    """List grooves in the Groove Pool and the global amount."""
    return _send("get_groove_pool", {})


@mcp.tool(annotations=ToolAnnotations(destructiveHint=False))
def set_clip_groove(ctx: Context, track_index: int, clip_index: int, groove_index: int,
                    arrangement_clip_index: int | None = None) -> str:
    """Apply a Groove Pool groove. groove_index -1 clears."""
    return _send("set_clip_groove", {
        "track_index": track_index,
        "clip_index": clip_index,
        "groove_index": groove_index,
        "arrangement_clip_index": arrangement_clip_index,
    })


@mcp.tool(annotations=ToolAnnotations(destructiveHint=False))
def set_groove_params(ctx: Context, groove_index: int = -1,
                      timing_amount: float | None = None,
                      random_amount: float | None = None,
                      velocity_amount: float | None = None,
                      quantization_amount: float | None = None,
                      base: int | None = None,
                      global_amount: float | None = None) -> str:
    """Edit groove amounts and/or the set's global groove amount."""
    return _send("set_groove_params", {
        "groove_index": groove_index,
        "timing_amount": timing_amount,
        "random_amount": random_amount,
        "velocity_amount": velocity_amount,
        "quantization_amount": quantization_amount,
        "base": base,
        "global_amount": global_amount,
    })


# ── Batch / propagate (jpoindexter-style) ───────────────────────────────────

@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def batch_add_warp_markers(ctx: Context, targets: list[dict], markers: list[dict]) -> str:
    """
    targets: [{"track_index": int, "clip_index": int}, ...]
    markers: [{"beat_time": float, "sample_time": float | None}, ...]
    Adds the same markers to every target clip.
    """
    conn = get_ableton_connection()
    results = []
    for t in targets:
        for m in markers:
            r = conn.send_command("add_warp_marker", {
                "track_index": t["track_index"],
                "clip_index": t.get("clip_index", 0),
                "beat_time": m["beat_time"],
                "sample_time": m.get("sample_time"),
            })
            results.append({"target": t, "marker": m, "ok": bool(r)})
    return json.dumps({"applied": len(results)}, indent=2)


@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def propagate_warp_markers(ctx: Context, source_track: int, source_clip: int,
                           targets: list[dict]) -> str:
    """Copy all warp markers from source to each target clip."""
    conn = get_ableton_connection()
    src = conn.send_command("get_warp_markers", {
        "track_index": source_track, "clip_index": source_clip
    })
    markers = src.get("warp_markers", [])
    for t in targets:
        for m in markers:
            conn.send_command("add_warp_marker", {
                "track_index": t["track_index"],
                "clip_index": t.get("clip_index", 0),
                "beat_time": m["beat_time"],
                "sample_time": m["sample_time"],
            })
    return json.dumps({"source_markers": len(markers), "targets": len(targets)}, indent=2)


# ── Supporting (already in wstierhout; re-exported for catalog clarity) ─────

@mcp.tool(annotations=ToolAnnotations(destructiveHint=False))
def set_clip_audio(ctx: Context, track_index: int, clip_index: int,
                   warping: bool | None = None, warp_mode: int | None = None,
                   gain: float | None = None, pitch_coarse: int | None = None,
                   pitch_fine: float | None = None) -> str:
    """Set audio-clip properties. warp_mode: 0=Beats 1=Tones 2=Texture 3=Re-Pitch 4=Complex 6=Complex Pro."""
    params = {"track_index": track_index, "clip_index": clip_index}
    for k, v in (("warping", warping), ("warp_mode", warp_mode), ("gain", gain),
                 ("pitch_coarse", pitch_coarse), ("pitch_fine", pitch_fine)):
        if v is not None:
            params[k] = v
    return _send("set_clip_audio", params)
