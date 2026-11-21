"""Selects which project is built: the main video (default) or the hook (VIDEO=hook)."""
import importlib, os
HOOK = os.environ.get("VIDEO") == "hook"
SHOTS = importlib.import_module("hook_story" if HOOK else "story").SHOTS
TLF = "timeline_hook.json" if HOOK else "timeline.json"
NARR = "narration_hook.mp3" if HOOK else "narration.mp3"
AOUT = "hook_audio" if HOOK else "final_audio"
