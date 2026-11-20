"""Registry of explainer videos.

Each video is a module exposing a VIDEO dict:
    VIDEO = dict(slug, title, steps, scene, initial, overlays=None, tracker=None, voice_rate=None)
New videos go in this folder as <slug>.py (copy the structure of ../elevator.py) and are
picked up automatically. Older/example videos can be listed in EXTRA."""
from __future__ import annotations

import importlib
import pkgutil

EXTRA = {"elevator": "stickman_studio.explainer.elevator"}


def modules():
    found = dict(EXTRA)
    for m in pkgutil.iter_modules(__path__):
        if not m.name.startswith("_"):
            found[m.name] = f"{__name__}.{m.name}"
    return found


def load(slug):
    mods = modules()
    if slug not in mods:
        raise KeyError(f"unknown video '{slug}'. Available: {', '.join(sorted(mods))}")
    return importlib.import_module(mods[slug]).VIDEO


def module_file(slug):
    import inspect
    return inspect.getsourcefile(importlib.import_module(modules()[slug]))
