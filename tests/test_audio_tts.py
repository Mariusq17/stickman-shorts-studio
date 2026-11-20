import numpy as np

import re

import pytest

from stickman_studio.audio import MUSIC_STYLES, SR, envelope, mix_tracks, music_bed, sfx
from stickman_studio.tts import (EspeakEngine, ProceduralVoice, available_engines, espeak_exe,
                                 estimate_word_times, piper_ready, split_sentences, synthesize_all)


def test_procedural_voice_timings():
    clip = ProceduralVoice().synth("Hello there, this is a perfectly normal test!")
    assert clip.duration > 1.0
    assert len(clip.word_times) == len(clip.words) == 8
    for (s, e), (s2, _) in zip(clip.word_times, clip.word_times[1:]):
        assert s < e <= s2
    assert clip.word_times[-1][1] <= clip.duration + 0.05
    assert np.isfinite(clip.samples).all() and np.abs(clip.samples).max() <= 1.0
    assert 0 <= clip.env.min() and clip.env.max() <= 1.0 and clip.env.max() > 0.5


def test_romanian_diacritics():
    clip = ProceduralVoice().synth("Ședința asta putea fi un email, știi?")
    assert clip.duration > 0.8


def test_synthesize_all_auto_never_fails():
    clips, engine = synthesize_all(["One two three.", "Four five?"], engine="auto")
    assert engine in ("piper", "sapi", "espeak", "procedural")
    assert all(c.duration > 0.2 for c in clips)
    # the cartoon babble is only the last resort
    if piper_ready("en") or espeak_exe():
        assert engine != "procedural"


def test_engine_report():
    eng = available_engines("ro")
    assert set(eng) == {"piper", "sapi", "espeak", "procedural"}
    assert eng["procedural"][0]


def test_split_sentences():
    assert split_sentences("Hi there. How are you? Fine!") == ["Hi there.", "How are you?", "Fine!"]


def _transcribe(samples):
    pocketsphinx = pytest.importorskip("pocketsphinx")
    from stickman_studio.audio import resample
    pcm = (np.clip(resample(samples, SR, 16000), -1, 1) * 32767).astype("<i2").tobytes()
    d = pocketsphinx.Decoder(samprate=16000)
    d.start_utt()
    d.process_raw(pcm, full_utt=True)
    d.end_utt()
    return d.hyp().hypstr if d.hyp() else ""


TEXT = "Your seven dollar coffee is quietly stealing your future house. Let me show you the math!"


def _hit_rate(hyp):
    ref = set(re.findall(r"[a-z']+", TEXT.lower()))
    hw = re.findall(r"[a-z']+", hyp.lower())
    return sum(w in ref for w in hw) / max(1, len(hw)), len(hw)


@pytest.mark.skipif(not piper_ready("en"), reason="no local Piper English voice")
def test_piper_voice_is_intelligible():
    """Speech recognition must understand the generated voice (real words, not babble)."""
    clips, engine = synthesize_all([TEXT], engine="piper", language="en")
    assert engine == "piper"
    rate, n = _hit_rate(_transcribe(clips[0].samples))
    assert n >= 8 and rate >= 0.7


def test_procedural_voice_is_not_speech():
    """Documents why the procedural engine is only a last-resort fallback."""
    rate, n = _hit_rate(_transcribe(ProceduralVoice().synth(TEXT).samples))
    assert rate < 0.7 or n < 5


@pytest.mark.skipif(espeak_exe() is None, reason="espeak-ng not installed")
def test_espeak_romanian():
    clip = EspeakEngine("ro").synth("Ședința asta putea fi un email. Am cronometrat!")
    assert clip.duration > 1.0 and len(clip.word_times) == 8


def test_voice_rate_changes_duration():
    slow = ProceduralVoice(rate=0.8, seed=1).synth("a b c d e f g h")
    fast = ProceduralVoice(rate=1.3, seed=1).synth("a b c d e f g h")
    assert slow.duration > fast.duration * 1.3


def test_estimate_word_times():
    wt = estimate_word_times(["Hi,", "there", "friend."], 2.0)
    assert len(wt) == 3 and wt[0][0] == 0.0 and wt[-1][1] <= 2.0 + 1e-6


def test_sfx_music_and_mix():
    for name in ["pop", "boing", "thud", "whoosh", "sting", "slap", "rumble", "tick", "click", "ding",
                 "cash", "boop"]:
        x = sfx(name)
        assert len(x) > 100 and np.isfinite(x).all()
    m = music_bed(5.0, energy=4)
    assert abs(len(m) - 5 * SR) < SR * 0.05
    for style in MUSIC_STYLES:
        mm = music_bed(12.0, style=style)
        assert np.isfinite(mm).all() and np.abs(mm).max() <= 1.0 and mm.std() > 0.02
    v = ProceduralVoice().synth("Testing the mix")
    out = mix_tracks(5.0, [(0.5, v.samples)], [(1.0, "pop", 0.8)], m, 0.12)
    assert out.shape[0] >= 5 * SR and np.abs(out).max() <= 1.0
    assert envelope(out, SR).max() <= 1.0
