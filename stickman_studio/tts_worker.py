"""Isolated pyttsx3 worker, executed in a subprocess so that SAPI5/COM
threading issues or hangs can never freeze the Streamlit app.

Usage: python -m stickman_studio.tts_worker job.json      -> synthesize
       python -m stickman_studio.tts_worker --list-voices -> print voices JSON
"""
from __future__ import annotations

import json
import sys


def _engine():
    import pyttsx3
    return pyttsx3.init()


def list_voices():
    eng = _engine()
    out = []
    for v in eng.getProperty("voices") or []:
        langs = []
        for l in getattr(v, "languages", []) or []:
            langs.append(l.decode("utf-8", "ignore") if isinstance(l, bytes) else str(l))
        out.append({"id": v.id, "name": getattr(v, "name", v.id), "languages": langs})
    print(json.dumps(out))


def synth(job_path: str):
    with open(job_path, "r", encoding="utf-8") as f:
        job = json.load(f)
    eng = _engine()
    base = eng.getProperty("rate") or 200
    eng.setProperty("rate", int(base * float(job.get("rate", 1.0))))
    if job.get("voice_id"):
        try:
            eng.setProperty("voice", job["voice_id"])
        except Exception:
            pass
    for item in job["items"]:
        eng.save_to_file(item["text"], item["path"])
    eng.runAndWait()
    try:
        eng.stop()
    except Exception:
        pass
    print(json.dumps({"ok": True}))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list-voices":
        list_voices()
    else:
        synth(sys.argv[1])
