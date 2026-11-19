"""Offline text-to-speech.

* Pyttsx3Engine  - real voices via pyttsx3 (Windows SAPI5 / macOS NSSS / Linux eSpeak),
                   run in an isolated subprocess.
* ProceduralVoice - pure-NumPy formant "cartoon voice" synthesizer. Always available
                   (headless Linux, CI, no sound card), returns exact word timings.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from .audio import read_wav, resample, trim_silence, envelope, SR


@dataclass
class SpeechClip:
    samples: np.ndarray          # mono float32 @ SR
    word_times: list             # [(start, end)] seconds, relative to clip start
    words: list
    engine: str = "procedural"
    env: np.ndarray = field(default=None)

    @property
    def duration(self) -> float:
        return len(self.samples) / SR


def tokenize(text: str) -> list:
    return [w for w in text.split() if w.strip()]


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-zăâîșşțţéèáíóúA-ZĂÂÎȘŞȚŢ0-9]", "", word.lower())
    if not w:
        return 1
    if w.isdigit():
        return max(1, min(6, len(w)))
    groups = re.findall(r"[aeiouyăâîéèáíóú]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith("le"):
        n -= 1
    return max(1, min(6, n))


def _pause_after(word: str) -> float:
    if re.search(r"[.!?…]$", word):
        return 0.30
    if re.search(r"[,;:—-]$", word):
        return 0.16
    return 0.035


def estimate_word_times(words: list, speech_dur: float, offset: float = 0.0):
    """Distribute a known speech duration across words (for engines without timing info)."""
    weights = [_syllables(w) * 1.0 + 0.25 for w in words]
    pauses = [_pause_after(w) for w in words]
    pauses[-1:] = [0.0]
    total_w = sum(weights) or 1.0
    avail = max(0.1, speech_dur - sum(pauses))
    out, t = [], offset
    for w, pz in zip(weights, pauses):
        d = avail * w / total_w
        out.append((t, t + d))
        t += d + pz
    return out


# --------------------------------------------------------------- procedural
_VOWEL_FORMANTS = {
    "a": (800, 1250), "e": (520, 1850), "i": (320, 2300), "o": (520, 900), "u": (360, 800),
    "y": (330, 2100), "ă": (600, 1400), "â": (420, 1500), "î": (420, 1500),
}


class ProceduralVoice:
    name = "procedural"

    def __init__(self, rate: float = 1.0, pitch: float = 1.0, seed: int = 0):
        self.rate = max(0.5, min(2.0, rate))
        self.pitch = pitch
        self.sr = 22050
        self.seed = seed

    def synth(self, text: str, idx: int = 0) -> SpeechClip:
        sr = self.sr
        words = tokenize(text) or ["..."]
        rng = np.random.default_rng(self.seed * 1000 + idx)
        syl_d = 0.165 / self.rate
        f_base = 165.0 * self.pitch
        is_q = text.strip().endswith("?")
        is_ex = text.strip().endswith("!")
        segments, times, t = [], [], 0.0
        n_words = len(words)
        harmonics = np.arange(1, 22)[:, None]
        for wi, w in enumerate(words):
            ns = _syllables(w)
            letters = re.sub(r"[^a-zăâî]", "", w.lower()) or "a"
            vowels = [c for c in letters if c in _VOWEL_FORMANTS] or ["a"]
            w_start = t
            for si in range(ns):
                d = syl_d * rng.uniform(0.8, 1.25) * (1.25 if si == ns - 1 and wi == n_words - 1 else 1.0)
                n = int(d * sr)
                tt = np.arange(n) / sr
                prog = (wi + si / ns) / max(1, n_words)
                f0 = f_base * (1.08 - 0.16 * prog) * rng.uniform(0.93, 1.1)
                if is_ex:
                    f0 *= 1.12
                if is_q and wi == n_words - 1:
                    f0 *= 1.0 + 0.35 * (si + 1) / ns
                contour = f0 * (1 + 0.06 * np.sin(np.pi * tt / d)) * (1 + 0.01 * np.sin(2 * np.pi * 5.5 * tt))
                phase = 2 * np.pi * np.cumsum(contour) / sr
                F1, F2 = _VOWEL_FORMANTS.get(vowels[si % len(vowels)], (700, 1200))
                hf = harmonics * f0
                amp = (np.exp(-((hf - F1) / 130) ** 2) + 0.7 * np.exp(-((hf - F2) / 200) ** 2)
                       + 0.25 / harmonics)
                sig = (amp * np.sin(harmonics * phase[None, :])).sum(axis=0)
                env = np.minimum(1, tt / 0.018) * np.minimum(1, (d - tt) / 0.045)
                sig = sig * env
                # consonant burst
                cn = int(min(n, 0.03 * sr))
                if letters[0] not in _VOWEL_FORMANTS or si > 0:
                    noise = rng.uniform(-1, 1, cn)
                    noise = np.diff(np.concatenate([[0], noise]))
                    sig[:cn] += noise * np.linspace(0.5, 0, cn) * (np.abs(sig).max() or 1) * 0.6
                segments.append(sig.astype(np.float32))
                t += d
            times.append((w_start, t))
            gap = (_pause_after(w) + 0.04) / self.rate if wi < n_words - 1 else 0.0
            if gap > 0:
                segments.append(np.zeros(int(gap * sr), dtype=np.float32))
                t += gap
        x = np.concatenate(segments) if segments else np.zeros(sr // 4, dtype=np.float32)
        # gentle low-pass (moving average) + normalize
        x = np.convolve(x, np.ones(3) / 3, mode="same")
        x = x / (np.abs(x).max() or 1.0) * 0.8
        y = resample(x, sr, SR)
        return SpeechClip(y, times, words, "procedural", envelope(y, SR))


# ------------------------------------------------------------------ pyttsx3
def _worker_cmd(*args):
    return [sys.executable, "-m", "stickman_studio.tts_worker", *args]


def _pkg_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(cmd, timeout):
    env = dict(os.environ)
    env["PYTHONPATH"] = _pkg_root() + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env,
                          cwd=_pkg_root(), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


@lru_cache(maxsize=1)
def list_voices() -> list:
    try:
        r = _run(_worker_cmd("--list-voices"), timeout=25)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        pass
    return []


@lru_cache(maxsize=1)
def pyttsx3_available() -> bool:
    try:
        import pyttsx3  # noqa: F401
    except Exception:
        return False
    return len(list_voices()) > 0


def pick_voice_for_language(lang: str):
    lang = (lang or "en").lower()
    keys = {"ro": ["ro", "roman", "andrei"], "en": ["en", "english", "zira", "david", "mark"]}.get(lang, [lang])
    for v in list_voices():
        hay = (v.get("name", "") + " " + v.get("id", "") + " " + " ".join(v.get("languages", []))).lower()
        if any(k in hay for k in keys):
            return v["id"]
    return None


class Pyttsx3Engine:
    name = "pyttsx3"

    def __init__(self, rate: float = 1.0, voice_id: str | None = None, language: str = "en"):
        self.rate = rate
        self.voice_id = voice_id or pick_voice_for_language(language)

    def synth_many(self, texts: list, workdir: str) -> list:
        items = [{"text": t, "path": os.path.join(workdir, f"tts_{i:03d}.wav")} for i, t in enumerate(texts)]
        job = os.path.join(workdir, "tts_job.json")
        with open(job, "w", encoding="utf-8") as f:
            json.dump({"items": items, "rate": self.rate, "voice_id": self.voice_id}, f)
        r = _run(_worker_cmd(job), timeout=60 + 6 * len(texts))
        if r.returncode != 0:
            raise RuntimeError("pyttsx3 worker failed: " + (r.stderr or "")[-400:])
        clips = []
        for it in items:
            if not os.path.exists(it["path"]) or os.path.getsize(it["path"]) < 1000:
                clips.append(None)
                continue
            try:
                x, sr = read_wav(it["path"])
                x, _ = trim_silence(x, sr)
                y = resample(x, sr, SR)
                peak = np.abs(y).max() or 1.0
                y = y / peak * 0.85
                words = tokenize(it["text"])
                wt = estimate_word_times(words, len(y) / SR)
                clips.append(SpeechClip(y.astype(np.float32), wt, words, "pyttsx3", envelope(y, SR)))
            except Exception:
                clips.append(None)
        return clips


def synthesize_all(texts: list, engine: str = "auto", rate: float = 1.0, voice_id=None,
                   language: str = "en", pitch: float = 1.0, workdir: str | None = None, seed: int = 0):
    """Synthesize every shot. Returns (clips, engine_used). Never raises because of TTS:
    any failure transparently falls back to the procedural voice."""
    proc = ProceduralVoice(rate=rate, pitch=pitch, seed=seed)
    used = "procedural"
    clips = [None] * len(texts)
    if engine in ("auto", "pyttsx3") and pyttsx3_available():
        tmp = workdir or tempfile.mkdtemp(prefix="stickman_tts_")
        try:
            clips = Pyttsx3Engine(rate, voice_id, language).synth_many(texts, tmp)
            used = "pyttsx3"
        except Exception:
            clips = [None] * len(texts)
    for i, c in enumerate(clips):
        if c is None:
            clips[i] = proc.synth(texts[i], i)
    if used == "pyttsx3" and any(c.engine == "procedural" for c in clips):
        used = "mixed"
    return clips, used
