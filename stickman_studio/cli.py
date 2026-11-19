"""Command line interface (headless rendering).

python -m stickman_studio.cli --theme latte_money --duration 60 --format vertical -o out.mp4
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import RenderSettings, THEMES, FORMATS, CTA_TYPES
from .pipeline import build_video
from .script_gen import generate_script, list_themes
from .script_model import Script


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stickman Video Studio - offline renderer")
    ap.add_argument("--theme", default=None, help="theme id (see --list)")
    ap.add_argument("--topic", default="", help="custom topic (overrides theme)")
    ap.add_argument("--duration", type=float, default=60)
    ap.add_argument("--format", choices=list(FORMATS), default="vertical")
    ap.add_argument("--visual", choices=list(THEMES), default="light")
    ap.add_argument("--fps", type=int, choices=[24, 30], default=30)
    ap.add_argument("--lang", choices=["en", "ro"], default="en")
    ap.add_argument("--cta", choices=list(CTA_TYPES), default="subscribe")
    ap.add_argument("--cta-text", default="")
    ap.add_argument("--energy", type=int, default=3)
    ap.add_argument("--voice-rate", type=float, default=1.0)
    ap.add_argument("--tts", choices=["auto", "pyttsx3", "procedural"], default="auto")
    ap.add_argument("--scale", type=float, default=1.0, help="resolution multiplier (0.5 = fast draft)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--script", default=None, help="load script JSON instead of generating")
    ap.add_argument("--save-script", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("-o", "--out", default="output/stickman_video.mp4")
    a = ap.parse_args(argv)
    if a.list:
        for tid, cat, title in list_themes(a.lang):
            print(f"{tid:18s} [{cat}] {title}")
        return 0
    if a.script:
        with open(a.script, encoding="utf-8") as f:
            script = Script.from_dict(json.load(f))
    else:
        script = generate_script(a.theme, a.duration, a.lang, a.cta, a.cta_text, a.energy, a.seed,
                                 custom_topic=a.topic)
    if a.save_script:
        with open(a.save_script, "w", encoding="utf-8") as f:
            json.dump(script.to_dict(), f, ensure_ascii=False, indent=2)
    st = RenderSettings(format=a.format, fps=a.fps, theme=a.visual, scale=a.scale, language=a.lang,
                        voice_rate=a.voice_rate, tts_engine=a.tts, target_duration=a.duration,
                        energy=a.energy)

    def progress(f, msg):
        sys.stdout.write(f"\r[{int(f * 100):3d}%] {msg[:70]:70s}")
        sys.stdout.flush()

    r = build_video(script, st, a.out, progress=progress, log=lambda m: print("\n" + m))
    print(f"\nOK -> {r.path}  ({r.duration:.1f}s, {r.frames} frames, TTS: {r.tts_engine}, "
          f"{r.render_seconds:.0f}s render)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
