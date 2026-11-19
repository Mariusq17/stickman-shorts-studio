import numpy as np

from stickman_studio.audio import SR, envelope, mix_tracks, music_bed, sfx
from stickman_studio.tts import ProceduralVoice, estimate_word_times, synthesize_all


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
    assert engine in ("pyttsx3", "procedural", "mixed")
    assert all(c.duration > 0.2 for c in clips)


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
    v = ProceduralVoice().synth("Testing the mix")
    out = mix_tracks(5.0, [(0.5, v.samples)], [(1.0, "pop", 0.8)], m, 0.12)
    assert out.shape[0] >= 5 * SR and np.abs(out).max() <= 1.0
    assert envelope(out, SR).max() <= 1.0
