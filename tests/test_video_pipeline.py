import os
import subprocess

import imageio_ffmpeg
import pytest

from stickman_studio.config import RenderSettings
from stickman_studio.pipeline import build_audio, build_video, synthesize_timeline, verify_video
from stickman_studio.script_gen import generate_script


def _probe(path):
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([exe, "-hide_banner", "-i", path], capture_output=True, text=True)
    return r.stderr


@pytest.mark.parametrize("fmt", ["vertical", "horizontal"])
def test_build_short_mp4_with_audio(tmp_path, fmt):
    script = generate_script("latte_money", 15, "en", "subscribe", seed=1)
    st = RenderSettings(format=fmt, fps=24, scale=0.3, target_duration=15, tts_engine="auto")
    out = str(tmp_path / f"clip_{fmt}.mp4")
    calls = []
    res = build_video(script, st, out, progress=lambda f, m: calls.append(f))
    assert os.path.exists(out) and os.path.getsize(out) > 10_000
    assert calls and calls[-1] == 1.0
    assert 14.0 <= res.duration <= 20.0
    info = verify_video(out)
    assert info["has_audio"]
    assert info["audio_peak"] > 0.05
    assert abs(info["duration"] - res.duration) < 0.6
    assert info["size"] == list(st.size) or tuple(info["size"]) == st.size
    assert info["frame_std"] > 5
    probe = _probe(out)
    assert "Video: h264" in probe and "Audio: aac" in probe


def test_60s_romanian_render_draft(tmp_path):
    script = generate_script("meeting_email", 60, "ro", "comment", seed=2, energy=5)
    st = RenderSettings(format="vertical", fps=24, scale=0.2, target_duration=60, language="ro")
    out = str(tmp_path / "ro60.mp4")
    res = build_video(script, st, out)
    assert 54 <= res.duration <= 70
    info = verify_video(out)
    assert info["has_audio"]


def test_180s_timeline_and_audio_sync(tmp_path):
    script = generate_script("octopus", 180, "en", "save_share", seed=4)
    st = RenderSettings(target_duration=180)
    timeline, clips, engine = synthesize_timeline(script, st)
    total = timeline[-1].start + timeline[-1].duration
    assert 160 <= total <= 180.0 + 1e-6
    # each shot lasts at least as long as its voiceover
    for tm, c in zip(timeline, clips):
        assert tm.duration >= c.duration
        assert tm.word_times[-1][1] <= tm.duration
    wav = str(tmp_path / "mix.wav")
    dur = build_audio(script, timeline, clips, st, wav)
    assert abs(dur - total) < 1e-6 and os.path.getsize(wav) > 1_000_000
