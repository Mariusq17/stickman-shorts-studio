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
MUSIC_STYLES = {
    "lofi": "Lo-fi chill (calm, cald)",
    "pop": "Chill-pop (vesel, discret)",
    "upbeat": "Upbeat (energic)",
}
# progression vi - IV - I - V (A minor / C major), 4-note voicings (semitones from C4)
_PROGRESSION = [
    (-3, [0, 4, 7, 11]),     # Am7   : A  C  E  G   (root A2)
    (-7, [-3, 0, 4, 7]),     # Fmaj7 : F  A  C  E   (root F2)
    (0, [-1, 4, 7, 12]),     # Cmaj7 : B  E  G  C   (root C3)
    (-5, [-1, 2, 7, 11]),    # G6    : B  D  G  B   (root G2)
]
_MSR = 22050  # music is synthesized at a lower rate, then upsampled


def _note(semi: float) -> float:
    return 261.63 * 2 ** (semi / 12.0)


def _ep(freq, dur, sr=_MSR):
    """Soft electric-piano tone."""
    t = np.arange(int(dur * sr)) / sr
    env = np.exp(-t * 2.2) * np.minimum(1, t / 0.006)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    x = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 4)
         + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 7))
    return (x * env * trem).astype(np.float32)


def _pad(freqs, dur, sr=_MSR):
    t = np.arange(int(dur * sr)) / sr
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.6)
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.004, 0.004):
            for k in range(1, 7):
                x += np.sin(2 * np.pi * f * (1 + det) * k * t + k) / k ** 1.6
    return (x * env / (len(freqs) * 4)).astype(np.float32)


def _place(buf, x, start):
    i = int(start)
    if i >= len(buf):
        return
    seg = x[: len(buf) - i]
    buf[i:i + len(seg)] += seg


def _fft_lowpass(x, cutoff, sr=_MSR):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, n=len(x)).astype(np.float32)


def _reverb_circular(x, seconds=1.8, mix=0.28, sr=_MSR, seed=3):
    """Seamless (circular) reverb for a loop via FFT convolution."""
    n = len(x)
    m = int(seconds * sr)
    rng = np.random.default_rng(seed)
    ir = np.zeros(n, dtype=np.float32)
    tt = np.arange(min(m, n)) / sr
    ir[: len(tt)] = rng.standard_normal(len(tt)) * np.exp(-tt * 3.8 / seconds)
    ir = _fft_lowpass(ir, 3500, sr)
    wet = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(ir), n=n)
    wet = wet / (np.abs(wet).max() or 1) * (np.abs(x).max() or 1)
    return ((1 - mix) * x + mix * wet).astype(np.float32)


def _music_loop(style: str, seed: int = 0) -> np.ndarray:
    bpm = {"lofi": 82, "pop": 100, "upbeat": 116}.get(style, 100)
    beat = 60.0 / bpm
    bars = 8
    n = int(bars * 4 * beat * _MSR)
    sr = _MSR
    rng = np.random.default_rng(seed)
    transpose = int(rng.integers(-2, 3))
    keys = np.zeros(n, dtype=np.float32)
    pad = np.zeros(n, dtype=np.float32)
    bass = np.zeros(n, dtype=np.float32)
    drums = np.zeros(n, dtype=np.float32)
    swing = 0.08 if style == "lofi" else 0.0
    for bar in range(bars):
        root, chord = _PROGRESSION[bar % 4]
        b0 = bar * 4 * beat * sr
        freqs = [_note(c + transpose) for c in chord]
        pad_x = _pad([f / 2 for f in freqs[:3]], 4 * beat)
        _place(pad, pad_x, b0)
        # electric piano rhythm
        hits = [0, 1.5, 2.5] if style != "upbeat" else [0, 1, 1.5, 2.5, 3]
        for h in hits:
            for j, f in enumerate(freqs):
                strum = j * 0.012 * sr
                _place(keys, _ep(f, 2.2) * (0.9 if h == 0 else 0.55), b0 + h * beat * sr + strum)
        # bass
        fb = _note(root + transpose - 12)
        for h, ln in ((0, 1.5), (2, 1.0), (3, 0.5)) if style != "lofi" else ((0, 2.0), (2.5, 1.0)):
            t = np.arange(int(ln * beat * sr)) / sr
            env = np.minimum(1, t / 0.01) * np.exp(-t * 1.5) * np.minimum(1, (ln * beat - t) / 0.05)
            x = (np.sin(2 * np.pi * fb * t) + 0.25 * np.sin(4 * np.pi * fb * t)) * env
            _place(bass, x.astype(np.float32), b0 + h * beat * sr)
        # drums
        for q in range(8):
            pos = b0 + (q * 0.5 + (swing if q % 2 else 0)) * beat * sr
            if q in (0, 4) or (style == "upbeat" and q in (3, 6)):
                t = np.arange(int(0.25 * sr)) / sr
                k = np.sin(2 * np.pi * np.cumsum(110 * np.exp(-t * 30) + 42) / sr) * np.exp(-t * 11)
                _place(drums, (k * 0.9).astype(np.float32), pos)
            if q in (2, 6):
                t = np.arange(int(0.18 * sr)) / sr
                sn = rng.standard_normal(len(t)) * np.exp(-t * 22) * 0.35 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.3
                _place(drums, sn.astype(np.float32) * (0.6 if style == "lofi" else 0.8), pos)
            t = np.arange(int(0.05 * sr)) / sr
            hh = rng.standard_normal(len(t)) * np.exp(-t * 90)
            hh = np.diff(np.concatenate([[0], hh]))
            _place(drums, (hh * (0.10 if q % 2 else 0.16)).astype(np.float32), pos)
    keys = _fft_lowpass(keys, 2600 if style == "lofi" else 4200)
    mix = keys * 0.42 + pad * 0.55 + bass * 0.55 + drums * (0.45 if style == "lofi" else 0.6)
    mix = _reverb_circular(mix, 1.6, 0.25 if style != "upbeat" else 0.18, seed=seed)
    if style == "lofi":
        mix = _fft_lowpass(mix, 3800)
        mix += rng.standard_normal(n).astype(np.float32) * 0.004   # vinyl air
    return mix / (np.abs(mix).max() or 1.0)


def music_bed(duration: float, energy: int = 3, seed: int = 0, style: str | None = None) -> np.ndarray:
    """Pleasant procedural background loop (seamless), matched to the energy level."""
    if style not in MUSIC_STYLES:
        style = "lofi" if energy <= 2 else "pop" if energy <= 3 else "upbeat"
    loop = _music_loop(style, seed)
    reps = int(np.ceil((duration + 1) * _MSR / len(loop)))
    x = np.tile(loop, reps)[: int((duration + 0.5) * _MSR)]
    y = resample(x, _MSR, SR)
    fi, fo = int(1.0 * SR), int(1.5 * SR)
    y[:fi] *= np.linspace(0, 1, fi)
    if fo < len(y):
        y[-fo:] *= np.linspace(1, 0, fo)
    return y[: int(duration * SR)].astype(np.float32)


def load_music_file(path: str, duration: float) -> np.ndarray:
    """User-supplied background track (mp3/wav/ogg/m4a...) decoded with ffmpeg, looped."""
    x, sr = _read_with_ffmpeg(path, SR)
    if len(x) == 0:
        return np.zeros(int(duration * SR), dtype=np.float32)
    reps = int(np.ceil(duration * SR / len(x)))
    y = np.tile(x, max(1, reps))[: int(duration * SR)].copy()
    y = y / (np.abs(y).max() or 1.0)
    fo = int(1.5 * SR)
    if fo < len(y):
        y[-fo:] *= np.linspace(1, 0, fo)
    return y.astype(np.float32)


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
    out = voice + fx * 0.35
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
        duck = 1.0 - 0.6 * np.clip(lev / (lev.max() or 1) * 3, 0, 1)
        duck = np.repeat(duck, hop)[:n]
        out += m * music_volume * duck
    # loudness: speech around -16 dBFS RMS, soft limiter on peaks
    active = np.abs(voice) > 0.01
    rms = float(np.sqrt(np.mean(out[active] ** 2))) if active.any() else float(np.sqrt(np.mean(out ** 2)))
    if rms > 0:
        out = out * (0.16 / rms)
    out = np.tanh(out / 0.95) * 0.95
    return out.astype(np.float32)
