"""Piper neural voice models: catalog, one-time download, local lookup.

Models are downloaded ONCE (e.g. by START_STUDIO.bat or the "Descarcă voci" button)
into ./models/piper and afterwards everything runs fully offline.

CLI:  python -m stickman_studio.voices --download en ro
"""
from __future__ import annotations

import glob
import io
import json
import os
import shutil
import sys
import tarfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, "models", "piper")
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

# voice id -> (language, label, [download sources])
# A source is either ("files", base_url_without_extension) or ("tar", url, onnx_name_inside)
CATALOG = {
    "en_US-ryan-high": ("en", "Ryan (EN, bărbat, energic)", [
        ("files", f"{HF}/en/en_US/ryan/high/en_US-ryan-high"),
        ("tar", "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-high.tar.gz",
         "en-us-ryan-high.onnx"),
    ]),
    "en_US-lessac-medium": ("en", "Lessac (EN, natural)", [
        ("files", f"{HF}/en/en_US/lessac/medium/en_US-lessac-medium"),
        ("tar", "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz",
         "en-us-lessac-medium.onnx"),
    ]),
    "ro_RO-mihai-medium": ("ro", "Mihai (RO, bărbat)", [
        ("files", f"{HF}/ro/ro_RO/mihai/medium/ro_RO-mihai-medium"),
    ]),
}
DEFAULT_VOICE = {"en": "en_US-ryan-high", "ro": "ro_RO-mihai-medium"}


def piper_installed() -> bool:
    try:
        import piper  # noqa: F401
        return True
    except Exception:
        return False


def _lang_of_file(path: str) -> str:
    try:
        with open(path + ".json", encoding="utf-8") as f:
            cfg = json.load(f)
        code = (cfg.get("language") or {}).get("code") or cfg.get("espeak", {}).get("voice", "")
        return str(code)[:2].lower()
    except Exception:
        name = os.path.basename(path).lower()
        return name[:2]


def local_voices() -> list:
    """[(voice_id, language, path)] for every .onnx model found locally."""
    out = []
    for p in sorted(glob.glob(os.path.join(MODELS_DIR, "*.onnx"))):
        if os.path.exists(p + ".json"):
            vid = os.path.basename(p)[:-5]
            out.append((vid, _lang_of_file(p), p))
    return out


def find_voice(language: str, voice_id: str | None = None):
    """Path of the best local model for a language (or the explicitly chosen one)."""
    voices = local_voices()
    if voice_id:
        for vid, _, p in voices:
            if vid == voice_id:
                return p
    preferred = DEFAULT_VOICE.get(language)
    for vid, lang, p in voices:
        if vid == preferred:
            return p
    for vid, lang, p in voices:
        if lang == language:
            return p
    return None


def _fetch(url: str, timeout: float = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "stickman-video-studio"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download_voice(voice_id: str, log=print) -> str:
    """Downloads a catalog voice (once). Returns the .onnx path. Raises on failure."""
    if voice_id not in CATALOG:
        raise KeyError(voice_id)
    os.makedirs(MODELS_DIR, exist_ok=True)
    dst = os.path.join(MODELS_DIR, voice_id + ".onnx")
    if os.path.exists(dst) and os.path.exists(dst + ".json"):
        return dst
    errors = []
    for src in CATALOG[voice_id][2]:
        try:
            if src[0] == "files":
                log(f"Descarc {voice_id} ...")
                try:
                    cfg = _fetch(src[1] + ".onnx.json")
                    base = src[1]
                except Exception:
                    base = src[1].replace("/resolve/v1.0.0/", "/resolve/main/")
                    cfg = _fetch(base + ".onnx.json")
                model = _fetch(base + ".onnx", timeout=600)
            else:
                log(f"Descarc {voice_id} (arhivă) ...")
                data = _fetch(src[1], timeout=600)
                with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                    model = tf.extractfile(src[2]).read()
                    cfg = tf.extractfile(src[2] + ".json").read()
            tmp = dst + ".part"
            with open(tmp, "wb") as f:
                f.write(model)
            with open(dst + ".json", "wb") as f:
                f.write(cfg)
            shutil.move(tmp, dst)
            log(f"OK: {voice_id}")
            return dst
        except Exception as e:  # try the next mirror
            errors.append(f"{src[1]}: {e}")
    raise RuntimeError("Nu am putut descărca vocea " + voice_id + ":\n" + "\n".join(errors))


def ensure_language(language: str, log=print):
    """Make sure at least one Piper voice exists for the language (downloads the default)."""
    p = find_voice(language)
    if p:
        return p
    vid = DEFAULT_VOICE.get(language)
    if not vid:
        return None
    return download_voice(vid, log)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "--download":
        langs = argv[1:] or ["en", "ro"]
        ok = True
        for lang in langs:
            try:
                ensure_language(lang)
            except Exception as e:
                ok = False
                print(f"[avertisment] {e}")
        return 0 if ok else 1
    for vid, lang, p in local_voices():
        print(f"{vid:28s} {lang}  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
