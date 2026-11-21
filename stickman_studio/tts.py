"""Offline text-to-speech with an automatic engine chain:

1. Piper        - neural, natural-sounding voices (EN + RO), runs locally via onnxruntime.
                  The voice model is downloaded once (models/piper), then fully offline.
2. SAPI5        - Windows / macOS system voices through pyttsx3 (isolated subprocess).
3. eSpeak-NG    - classic offline synthesizer (robotic but intelligible, supports Romanian).
4. Procedural   - last-resort pure-NumPy "cartoon babble" so rendering never fails.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
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


# ------------------------------------------------------------------ helpers
def split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p for p in parts if p.strip()] or [text]


def _pauses(x: np.ndarray, min_gap: float = 0.05):
    """Silent gaps inside a phrase: [(start_s, end_s)] sorted by time."""
    hop = int(0.01 * SR)
    n = len(x) // hop
    if n < 3:
        return []
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    thr = max(1e-4, np.percentile(rms, 90) * 0.06)
    quiet = rms < thr
    gaps, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= min_gap and i > 0 and j < n:
                gaps.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return gaps


def align_words(x: np.ndarray, words: list, offset: float = 0.0):
    """Word timings for one sentence: split at the real pauses that correspond to
    commas/colons, then distribute words by syllables inside each chunk."""
    dur = len(x) / SR
    breaks = [i for i, w in enumerate(words[:-1]) if re.search(r"[,;:—]$", w)]
    gaps = _pauses(x)
    if breaks and len(gaps) >= len(breaks):
        chosen = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[: len(breaks)])
        bounds = [0.0] + [g for gap in chosen for g in gap] + [dur]
        out, start = [], 0
        for k, b in enumerate(breaks + [len(words) - 1]):
            seg = words[start:b + 1]
            s0, s1 = bounds[2 * k], bounds[2 * k + 1]
            out += estimate_word_times(seg, max(0.05, s1 - s0), offset=offset + s0)
            start = b + 1
        return out
    return estimate_word_times(words, dur, offset=offset)


def normalize_voice(x: np.ndarray, target_rms: float = 0.12, peak: float = 0.92) -> np.ndarray:
    """Consistent loudness between shots/engines + soft limiting."""
    if len(x) == 0:
        return x
    rms = float(np.sqrt(np.mean(x ** 2))) or 1e-6
    y = x * (target_rms / rms)
    y = np.tanh(y / peak) * peak          # soft clip instead of harsh distortion
    return y.astype(np.float32)


def _clip_from_sentences(pieces, words_per_piece, engine, gap=0.16):
    """pieces: list of float32 arrays @SR (one per sentence)."""
    out, times, t = [], [], 0.0
    for k, (x, words) in enumerate(zip(pieces, words_per_piece)):
        dur = len(x) / SR
        times += align_words(x, words, offset=t) if words else []
        out.append(x)
        t += dur
        if k < len(pieces) - 1:
            out.append(np.zeros(int(gap * SR), dtype=np.float32))
            t += gap
    y = normalize_voice(np.concatenate(out) if out else np.zeros(SR // 4, dtype=np.float32))
    words = [w for ws in words_per_piece for w in ws]
    return SpeechClip(y, times, words, engine, envelope(y, SR))


# -------------------------------------------------------------------- Piper
_PIPER_CACHE = {}


class PiperEngine:
    name = "piper"

    def __init__(self, language="en", voice_id=None, rate=1.0):
        from .voices import find_voice
        self.path = find_voice(language, voice_id)
        if not self.path:
            raise RuntimeError(f"Nu există model Piper local pentru limba '{language}'")
        self.rate = max(0.5, min(2.0, rate))
        if self.path not in _PIPER_CACHE:
            from piper import PiperVoice
            _PIPER_CACHE[self.path] = PiperVoice.load(self.path)
        self.voice = _PIPER_CACHE[self.path]

    def _sentence(self, text):
        from piper import SynthesisConfig
        cfg = SynthesisConfig(length_scale=1.0 / self.rate, noise_scale=0.6, noise_w_scale=0.75)
        arrs, sr = [], 22050
        for ch in self.voice.synthesize(text, cfg):
            arrs.append(np.asarray(ch.audio_float_array, dtype=np.float32))
            sr = ch.sample_rate
        x = np.concatenate(arrs) if arrs else np.zeros(1000, dtype=np.float32)
        x, _ = trim_silence(x, sr, 0.008, pre=0.05)
        return resample(x, sr, SR)

    def synth(self, text, idx=0):
        # very short sentences ("Let's fix it.") are often garbled by Piper on their own -> glue them to a neighbour
        sents = []
        for sn in split_sentences(text):
            if sents and (len(sn.split()) < 4 or len(sents[-1].split()) < 4):
                sents[-1] = sents[-1] + " " + sn
            else:
                sents.append(sn)
        return _clip_from_sentences([self._sentence(s) for s in sents], [tokenize(s) for s in sents],
                                    "piper")


def piper_ready(language: str, voice_id=None) -> bool:
    from .voices import find_voice, piper_installed
    return piper_installed() and find_voice(language, voice_id) is not None


# ------------------------------------------------------------------- eSpeak
@lru_cache(maxsize=1)
def espeak_exe():
    for name in ("espeak-ng", "espeak"):
        p = shutil.which(name)
        if p:
            return p
    for p in (r"C:\Program Files\eSpeak NG\espeak-ng.exe", r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe",
              r"C:\Program Files (x86)\eSpeak\command_line\espeak.exe"):
        if os.path.exists(p):
            return p
    return None


class EspeakEngine:
    name = "espeak"

    def __init__(self, language="en", rate=1.0, pitch=1.0):
        self.exe = espeak_exe()
        if not self.exe:
            raise RuntimeError("espeak-ng nu este instalat")
        self.voice = {"ro": "ro", "en": "en-us"}.get(language, language)
        self.wpm = int(165 * rate)
        self.pitch = int(max(0, min(99, 50 * pitch)))

    def _sentence(self, text):
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            subprocess.run([self.exe, "-v", self.voice, "-s", str(self.wpm), "-p", str(self.pitch),
                            "-w", path, text], check=True, capture_output=True, timeout=60,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            x, sr = read_wav(path)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
        x, _ = trim_silence(x, sr)
        return resample(x, sr, SR)

    def synth(self, text, idx=0):
        sents = split_sentences(text)
        return _clip_from_sentences([self._sentence(s) for s in sents], [tokenize(s) for s in sents],
                                    "espeak")


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
    """System (SAPI5/NSSS) voices via pyttsx3. Empty on Linux to prefer espeak-ng directly."""
    if not (sys.platform.startswith("win") or sys.platform == "darwin"):
        return []
    try:
        r = _run(_worker_cmd("--list-voices"), timeout=25)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        pass
    return []


def pick_voice_for_language(lang: str):
    lang = (lang or "en").lower()
    keys = {"ro": ["romanian", "română", "andrei", "ro-ro", "ro_ro"],
            "en": ["english", "en-us", "en_us", "en-gb", "zira", "david", "mark", "hazel"]}.get(lang, [lang])
    for v in list_voices():
        hay = (v.get("name", "") + " " + v.get("id", "") + " " + " ".join(v.get("languages", []))).lower()
        if any(k in hay for k in keys):
            return v["id"]
    return None


class SapiEngine:
    name = "sapi"

    def __init__(self, rate=1.0, voice_id=None, language="en"):
        self.rate = rate
        self.voice_id = voice_id or pick_voice_for_language(language)
        if not self.voice_id:
            raise RuntimeError(f"Nicio voce de sistem pentru limba '{language}'")

    def synth_many(self, texts, workdir):
        items = [{"text": t, "path": os.path.join(workdir, f"tts_{i:03d}.wav")} for i, t in enumerate(texts)]
        job = os.path.join(workdir, "tts_job.json")
        with open(job, "w", encoding="utf-8") as f:
            json.dump({"items": items, "rate": self.rate * 0.9, "voice_id": self.voice_id}, f)
        r = _run(_worker_cmd(job), timeout=60 + 6 * len(texts))
        if r.returncode != 0:
            raise RuntimeError("SAPI worker failed: " + (r.stderr or "")[-400:])
        clips = []
        for it in items:
            try:
                x, sr = read_wav(it["path"])
                x, _ = trim_silence(x, sr)
                y = normalize_voice(resample(x, sr, SR))
                words = tokenize(it["text"])
                clips.append(SpeechClip(y, estimate_word_times(words, len(y) / SR), words, "sapi",
                                        envelope(y, SR)))
            except Exception:
                clips.append(None)
        return clips


# --------------------------------------------------------------- dispatcher
ENGINE_LABELS = {
    "piper": "Piper (voce neurală naturală)",
    "sapi": "Windows SAPI5 / voce de sistem",
    "espeak": "eSpeak-NG (robotic, dar clar)",
    "procedural": "Voce procedurală (doar sunete, fără cuvinte reale)",
}


def available_engines(language: str = "en") -> dict:
    """{engine: (available, reason)}"""
    from .voices import piper_installed, find_voice
    res = {}
    if not piper_installed():
        res["piper"] = (False, "pachetul piper-tts nu e instalat")
    elif not find_voice(language):
        res["piper"] = (False, "modelul de voce nu e descărcat încă")
    else:
        res["piper"] = (True, os.path.basename(find_voice(language)))
    res["sapi"] = (pick_voice_for_language(language) is not None,
                   "voce de sistem găsită" if pick_voice_for_language(language) else "nicio voce de sistem pentru limbă")
    res["espeak"] = (espeak_exe() is not None, espeak_exe() or "espeak-ng nu e instalat")
    res["procedural"] = (True, "mereu disponibilă")
    return res


def synthesize_all(texts: list, engine: str = "auto", rate: float = 1.0, voice_id=None,
                   language: str = "en", pitch: float = 1.0, workdir: str | None = None, seed: int = 0,
                   piper_voice=None, log=None):
    """Synthesize every shot. Returns (clips, engine_used). Never raises: each engine
    failure falls through to the next one in the chain."""
    say = log or (lambda m: None)
    order = ["piper", "sapi", "espeak", "procedural"] if engine in ("auto", None, "") else \
        [engine] + [e for e in ("piper", "sapi", "espeak", "procedural") if e != engine]
    if engine == "pyttsx3":
        order = ["sapi", "piper", "espeak", "procedural"]
    for name in order:
        try:
            if name == "piper":
                if not piper_ready(language, piper_voice):
                    continue
                eng = PiperEngine(language, piper_voice, rate)
                return [eng.synth(t, i) for i, t in enumerate(texts)], "piper"
            if name == "sapi":
                if not list_voices():
                    continue
                eng = SapiEngine(rate, voice_id, language)
                clips = eng.synth_many(texts, workdir or tempfile.mkdtemp(prefix="stickman_tts_"))
                if any(c is None for c in clips):
                    raise RuntimeError("SAPI a ratat unele fraze")
                return clips, "sapi"
            if name == "espeak":
                if not espeak_exe():
                    continue
                eng = EspeakEngine(language, rate, pitch)
                return [eng.synth(t, i) for i, t in enumerate(texts)], "espeak"
            if name == "procedural":
                proc = ProceduralVoice(rate=rate, pitch=pitch, seed=seed)
                return [proc.synth(t, i) for i, t in enumerate(texts)], "procedural"
        except Exception as e:
            say(f"Motorul TTS '{name}' a eșuat ({e}); încerc următorul.")
    proc = ProceduralVoice(rate=rate, pitch=pitch, seed=seed)
    return [proc.synth(t, i) for i, t in enumerate(texts)], "procedural"
