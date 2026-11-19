"""Audio utilities: WAV IO, resampling, lip-sync envelopes, procedural music
bed, synthesized sound effects and the final mix. Pure NumPy."""
from __future__ import annotations

import math
import os
import subprocess
import wave

import numpy as np

SR = 44100


# ------------------------------------------------------------------------ IO
def write_wav(path: str, samples: np.ndarray, sr: int = SR):
    x = np.asarray(samples, dtype=np.float32)
    if x.ndim == 1:
        x = x[:, None]
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(pcm.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def read_wav(path: str):
    """Returns (mono float32, sr). Falls back to ffmpeg for non-PCM formats."""
    try:
        with wave.open(path, "rb") as w:
            sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
            raw = w.readframes(n)
        if sw == 2:
            x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
        elif sw == 1:
            x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128.0
        elif sw == 4:
            x = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
        else:
            raise wave.Error("unsupported sample width")
        if ch > 1:
            x = x.reshape(-1, ch).mean(axis=1)
        return x, sr
    except (wave.Error, EOFError):
        return _read_with_ffmpeg(path)


def _read_with_ffmpeg(path: str, sr: int = 22050):
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"]
    out = subprocess.run(cmd, capture_output=True, check=True,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
    return np.frombuffer(out, dtype="<i2").astype(np.float32) / 32768.0, sr


def resample(x: np.ndarray, sr_in: int, sr_out: int = SR) -> np.ndarray:
    if sr_in == sr_out or len(x) == 0:
        return x.astype(np.float32)
    n_out = int(round(len(x) * sr_out / sr_in))
    xi = np.linspace(0, len(x) - 1, n_out)
    return np.interp(xi, np.arange(len(x)), x).astype(np.float32)


def trim_silence(x: np.ndarray, sr: int, thr: float = 0.02):
    """Returns (trimmed, offset_seconds)."""
    if len(x) == 0:
        return x, 0.0
    a = np.abs(x)
    peak = a.max() or 1.0
    idx = np.where(a > thr * peak)[0]
    if len(idx) == 0:
        return x, 0.0
    s = max(0, idx[0] - int(0.01 * sr))
    e = min(len(x), idx[-1] + int(0.03 * sr))
    return x[s:e], s / sr


def envelope(x: np.ndarray, sr: int, rate: float = 100.0) -> np.ndarray:
    """Normalized amplitude envelope (0..1) sampled at `rate` Hz for lip-sync."""
    hop = max(1, int(sr / rate))
    n = int(math.ceil(len(x) / hop))
    if n == 0:
        return np.zeros(1, dtype=np.float32)
    pad = np.zeros(n * hop, dtype=np.float32)
    pad[:len(x)] = x
    rms = np.sqrt((pad.reshape(n, hop) ** 2).mean(axis=1))
    ref = np.percentile(rms, 95) or 1.0
    env = np.clip(rms / ref, 0, 1)
    # light smoothing + gate so the mouth closes between syllables
    k = np.array([0.25, 0.5, 0.25])
    env = np.convolve(env, k, mode="same")
    env = np.where(env < 0.12, 0, env)
    return env.astype(np.float32)


# ----------------------------------------------------------------- SFX synth
def _t(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def _noise(n, seed=0):
    return np.random.default_rng(seed).uniform(-1, 1, n).astype(np.float32)


def _adsr(n, a=0.005, r=0.1, sr=SR):
    env = np.ones(n, dtype=np.float32)
    na, nr = max(1, int(a * sr)), max(1, int(r * sr))
    env[:na] = np.linspace(0, 1, na)
    if nr < n:
        env[-nr:] *= np.linspace(1, 0, nr)
    return env


def _lowpass(x, alpha):
    """Fast 1-pole low pass via exponential smoothing (vectorized through cumsum trick is
    unstable, so use scipy-free recursive filter in chunks)."""
    y = np.empty_like(x)
    acc = 0.0
    # chunked python loop is fine for short sfx (< 1 s)
    for i in range(len(x)):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


def sfx(name: str) -> np.ndarray:
    if name == "pop":
        t = _t(0.12)
        f = 900 * np.exp(-t * 25) + 300
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.6).astype(np.float32)
    if name == "boing":
        t = _t(0.45)
        f = 180 + 260 * t / 0.45 + 40 * np.sin(2 * np.pi * 18 * t)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.5).astype(np.float32)
    if name == "thud":
        t = _t(0.5)
        f = 90 * np.exp(-t * 6) + 40
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
        s += _noise(len(t), 3) * np.exp(-t * 40) * 0.4
        return (s * 0.8).astype(np.float32)
    if name == "whoosh":
        t = _t(0.4)
        n = _noise(len(t), 5)
        env = np.sin(np.pi * t / 0.4) ** 2
        lp = _lowpass(n, 0.15)
        return (lp * env * 1.2).astype(np.float32)
    if name == "sting":
        t = _t(0.9)
        s = sum(np.sin(2 * np.pi * f * t) for f in (220, 261.6, 311.1, 370))
        s = s / 4 * np.exp(-t * 3.5) * _adsr(len(t), 0.003, 0.2)
        return (s * 0.55).astype(np.float32)
    if name == "slap":
        t = _t(0.18)
        return (_noise(len(t), 9) * np.exp(-t * 35) * 0.6).astype(np.float32)
    if name == "rumble":
        t = _t(1.2)
        s = np.sin(2 * np.pi * 55 * t) * 0.6 + np.sin(2 * np.pi * 58 * t) * 0.4
        return (s * np.sin(np.pi * t / 1.2) * 0.45).astype(np.float32)
    if name == "tick":
        out = np.zeros(int(0.6 * SR), dtype=np.float32)
        for k in range(3):
            t = _t(0.03)
            st = int(k * 0.2 * SR)
            out[st:st + len(t)] += (np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 200) * 0.35).astype(np.float32)
        return out
    if name == "click":
        out = np.zeros(int(0.5 * SR), dtype=np.float32)
        rng = np.random.default_rng(1)
        for k in range(7):
            st = int(rng.uniform(0, 0.45) * SR)
            n = int(0.012 * SR)
            out[st:st + n] += _noise(n, k) * np.linspace(0.3, 0, n)
        return out
    if name == "ding":
        t = _t(1.0)
        s = (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t) +
             0.25 * np.sin(2 * np.pi * 3951 * t)) * np.exp(-t * 4)
        return (s * 0.3).astype(np.float32)
    if name == "cash":
        a = sfx("ding")[: int(0.35 * SR)]
        t = _t(0.35)
        b = np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 8) * 0.3
        out = np.zeros(int(0.55 * SR), dtype=np.float32)
        out[:len(a)] += a
        st = int(0.12 * SR)
        out[st:st + len(b)] += b.astype(np.float32)
        return out
    if name == "boop":
        t = _t(0.25)
        f = 500 + 400 * t / 0.25
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 0.4).astype(np.float32)
    return np.zeros(1, dtype=np.float32)


PROP_SFX = {"bulb": "ding", "money": "cash", "coins": "cash", "subscribe": "pop",
            "exclamation": "sting", "question": "boop", "chart_down": "whoosh", "chart_up": "ding",
            "like": "pop", "comment": "pop", "save": "pop", "bell": "ding", "clock": "tick",
            "fire": "whoosh", "phone": "boop", "calendar": "boop", "battery": "boop"}
CAMERA_SFX = {"punch_in": "whoosh", "dramatic_camera_shake": "sting", "zoom_in": "whoosh"}


# ---------------------------------------------------------------- music bed
_CHORDS = [
    (0, 4, 7), (7, 11, 14), (9, 12, 16), (5, 9, 12),   # I V vi IV
]


def music_bed(duration: float, energy: int = 3, seed: int = 0) -> np.ndarray:
    """Upbeat, unobtrusive procedural loop (bass + plucks + hats + kick)."""
    bpm = 92 + 8 * max(1, min(5, energy))
    beat = 60.0 / bpm
    n = int((duration + 0.5) * SR)
    out = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(seed)
    root = 261.63 * 2 ** (rng.integers(-3, 3) / 12)
    n_beats = int(duration / beat) + 2
    pluck_t = _t(beat * 0.9)
    pluck_env = np.exp(-pluck_t * 7).astype(np.float32)
    hat_n = int(0.04 * SR)
    hat = _noise(hat_n, 2) * np.exp(-np.arange(hat_n) / SR * 120)
    hat = (hat - np.concatenate([[0], hat[:-1]])) * 0.5            # crude high-pass
    kick_t = _t(0.22)
    kick = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-kick_t * 25) + 45) / SR) * np.exp(-kick_t * 14)
    pattern = [0, 2, 1, 2, 0, 1, 2, 1]
    for b in range(n_beats):
        st = int(b * beat * SR)
        if st >= n:
            break
        chord = _CHORDS[(b // 4) % 4]
        # bass on every beat
        f_b = root / 2 * 2 ** (chord[0] / 12)
        seg = min(len(pluck_t), n - st)
        bass = np.sin(2 * np.pi * f_b * pluck_t[:seg]) * np.exp(-pluck_t[:seg] * 3) * 0.35
        out[st:st + seg] += bass.astype(np.float32)
        # arpeggiated pluck (triangle-ish)
        for half in (0, 1):
            s2 = st + int(half * beat / 2 * SR)
            if s2 >= n:
                continue
            note = chord[pattern[(2 * b + half) % 8]]
            f = root * 2 ** (note / 12)
            seg2 = min(int(len(pluck_t) / 2), n - s2)
            ph = 2 * np.pi * f * pluck_t[:seg2]
            tri = (2 / np.pi) * np.arcsin(np.sin(ph))
            out[s2:s2 + seg2] += (tri * pluck_env[:seg2] * 0.16).astype(np.float32)
        # hats on off-beats
        s3 = st + int(beat / 2 * SR)
        if s3 + hat_n < n:
            out[s3:s3 + hat_n] += hat.astype(np.float32) * 0.6
        if energy >= 2 and b % 2 == 0 and st + len(kick) < n:
            out[st:st + len(kick)] += (kick * 0.5).astype(np.float32)
    # fade in/out
    fi, fo = int(0.5 * SR), int(1.2 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    if fo < n:
        out[-fo:] *= np.linspace(1, 0, fo)
    peak = np.abs(out).max() or 1.0
    return (out / peak)[: int(duration * SR)]


def mix_tracks(total: float, voice_events, sfx_events, music: np.ndarray | None,
               music_volume: float = 0.12) -> np.ndarray:
    """voice_events: [(start_s, samples@SR)], sfx_events: [(start_s, name, gain)]"""
    n = int(math.ceil(total * SR)) + 1
    voice = np.zeros(n, dtype=np.float32)
    for st, x in voice_events:
        i = int(st * SR)
        if i >= n:
            continue
        seg = x[: n - i]
        voice[i:i + len(seg)] += seg
    fx = np.zeros(n, dtype=np.float32)
    cache = {}
    for st, name, gain in sfx_events:
        if name not in cache:
            cache[name] = sfx(name)
        x = cache[name]
        i = int(st * SR)
        if i >= n or i < 0:
            continue
        seg = x[: n - i]
        fx[i:i + len(seg)] += seg * gain
    out = voice * 0.95 + fx * 0.55
    if music is not None and len(music):
        m = np.zeros(n, dtype=np.float32)
        m[: min(n, len(music))] = music[:n]
        # side-chain ducking driven by the voice envelope
        hop = int(SR * 0.02)
        nn = int(math.ceil(n / hop))
        pad = np.zeros(nn * hop, dtype=np.float32)
        pad[:n] = np.abs(voice)
        lev = pad.reshape(nn, hop).max(axis=1)
        lev = np.convolve(lev, np.ones(10) / 10, mode="same")
        duck = 1.0 - 0.55 * np.clip(lev / (lev.max() or 1) * 3, 0, 1)
        duck = np.repeat(duck, hop)[:n]
        out += m * music_volume * duck
    peak = np.abs(out).max()
    if peak > 0.98:
        out = out / peak * 0.98
    return out
