"""Scene QA (stickman_studio/explainer/qa.py) + strategy tools (tools/rotation.py, tools/yt)."""
import importlib.util
import os
import subprocess
import sys

import pytest

from stickman_studio.explainer import qa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _has_rev(rev):
    r = subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"], cwd=ROOT, capture_output=True)
    return r.returncode == 0


def _errors(res, kind=None):
    return [i for i in res["issues"] if i["level"] == "ERROR" and (kind is None or i["kind"] == kind)]


# ------------------------------------------------------------------ unit checks
def test_parse_steps():
    assert qa.parse_steps("1-3,7", 10) == {1, 2, 3, 7}
    assert qa.parse_steps(None, 3) == {0, 1, 2}


def test_connected_chain_gap_and_bridge():
    a = (0, 0, 0, 1, 1, 1)
    b = (5, 0, 0, 6, 1, 1)
    full = [[(1.0, 0.5, 0.5), (3.0, 0.5, 0.5)], [(3.0, 0.5, 0.5), (5.0, 0.5, 0.5)]]
    assert qa._connected(full, a, b)
    gap = [[(1.0, 0.5, 0.5), (2.5, 0.5, 0.5)], [(3.0, 0.5, 0.5), (5.0, 0.5, 0.5)]]
    assert not qa._connected(gap, a, b)
    assert qa._connected(gap, a, b, bridges=[(2.4, 0, 0, 3.1, 1, 1)])     # buried part counts as connected
    assert not qa._connected([], a, b)


def test_estimate_timing_is_calibrated():
    clip = qa.EstClip("If you put a box on a rope and hang it from a motor at the top of a shaft, you've got the "
                      "world's simplest elevator.")
    assert 4.5 < clip.duration < 8.0
    assert len(clip.word_times) == len(clip.words)


class _MovingBoxesScene:
    """Two boxes; B drives through A in step 1, A stays on screen in step 2 (not its step)."""

    def __init__(self, W, H):
        pass

    def draw(self, img, cam, tr, t, step_i, step_t):
        cam.box(-0.5, -0.5, 0, 1, 1, 0.5, (200, 0, 0))
        x = tr.get("bx", t)
        cam.box(x - 0.5, -0.5, 0, 1, 1, 0.5, (0, 0, 200))


def _synthetic_video():
    cam = ((0, 0, 0), 150)
    steps = [dict(text="Here is a red box standing in the middle of the road today.", cam=cam),
             dict(text="Then a blue box drives straight through it from left to right.", cam=cam,
                  do=[("bx", "w:drives", 6.0, 2.0, "lin")]),
             dict(text="Now we talk about something else entirely for quite a few seconds more.", cam=cam)]
    spec = dict(objects={"red box": dict(color=(200, 0, 0), steps="0-1", grace=0.5),
                         "blue box": dict(color=(0, 0, 200), steps="1", grace=10)})
    return dict(slug="synthetic", steps=steps, scene=_MovingBoxesScene, initial=dict(bx=-6.0)), spec


def test_synthetic_linger_and_pass_through():
    video, spec = _synthetic_video()
    res = qa.run_qa(video, spec, timing="est", dt=0.1)
    assert _errors(res, "pass-through"), res["issues"]
    lingers = _errors(res, "linger")
    assert lingers and all("red box" in i["msg"] for i in lingers)


def test_static_screen_warning():
    video, spec = _synthetic_video()
    res = qa.run_qa(video, spec, timing="est", dt=0.25)
    assert any(i["kind"] == "static" and i["step"] == 2 for i in res["issues"])


# ------------------------------------------------------------------ known bugs: v1 must fail, v2 must pass
@pytest.mark.parametrize("slug,old,fixed,kinds", [
    ("traffic_light", "cc47131", "bcf4216", {"linger", "pass-through"}),  # red car stayed; cars drove through it
    ("undersea_cable", "876fb6a", "7322c98", {"link"}),                    # cable ends not connected to stations
])
def test_known_bugs_caught_and_fixed_versions_pass(slug, old, fixed, kinds):
    if not (_has_rev(old) and _has_rev(fixed)):
        pytest.skip(f"commits {old}/{fixed} not in this clone (shallow?)")
    import importlib
    spec = importlib.import_module(f"stickman_studio.explainer.videos.{slug}").QA   # original step indices
    bad = qa.run_qa(qa.load_video(slug, old), spec, timing="est")
    assert kinds <= {i["kind"] for i in _errors(bad)}, bad["issues"]
    good = qa.run_qa(qa.load_video(slug, fixed), spec, timing="est")
    assert not _errors(good), _errors(good)


def test_every_current_video_has_no_qa_errors():
    from stickman_studio.explainer.videos import load, modules
    for slug in sorted(modules()):
        res = qa.run_qa(load(slug), timing="est", dt=0.5)
        assert not _errors(res), (slug, _errors(res))


def test_srt_export():
    from stickman_studio.explainer.videos import load
    v = load("streaming")
    res = qa.run_qa(v, timing="est", dt=1.0)
    srt = qa.to_srt(v, res)
    assert srt.startswith("1\n00:00:00,000 --> ") and "[step 0]" in srt


# ------------------------------------------------------------------ strategy tools
def _load_tool(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rotation_detects_repeats():
    rot = _load_tool("tools/rotation.py", "rotation")
    md = ("## A. DNA\n| # | Slug | Opening | Ending |\n|---|---|---|---|\n| 1 | a | O1 | E1 |\n"
          "## C. Queue\n| Order | Slug | Opening | Ending | Proposed opening | Proposed ending |\n|---|---|---|---|---|---|\n"
          "| 1 | b | O1 | E2 | O2 | E2 |\n| 2 | c | O3 | E3 | O3 | E3 |\n")
    assert rot.repeats(rot.sequence(md)) == ["opening O1 twice in a row: a -> b"]
    assert rot.repeats(rot.sequence(md, proposed=True)) == []
    o, e = rot.allowed_next(rot.sequence(md))
    assert "O3" not in o and "E3" not in e


def test_proposed_queue_respects_rotation():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "rotation.py"), "--proposed"], capture_output=True)
    assert r.returncode == 0, r.stdout.decode()


def test_vendored_tools_run_without_dependencies():
    hs = _load_tool("tools/yt/hookscore.py", "hookscore")
    parts, verdict, name, _ = hs.score("Your card has no battery. So how does it pay in one second?")
    assert 0 <= verdict <= 100 and name == "The Question"
    ti = _load_tool("tools/yt/title.py", "title")
    r = ti.check("Why Elevators Almost Never Fall", "WHY ELEVATORS NEVER FALL")
    assert any(k == "duplicate" for k, _ in r["issues"])
    for tool in ("retention.py", "swipe.py"):
        out = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "yt", tool)], capture_output=True)
        assert b"python3" in out.stdout          # prints its usage, no import errors


def test_shift_spec_and_open_loop():
    from stickman_studio.explainer.lib.story import open_loop
    sp = qa.shift_spec(dict(objects={"a": dict(color=(1, 2, 3), steps="1-4,7")}, links=[dict(steps="10-")]), 1)
    assert sp["objects"]["a"]["steps"] == "2-5,8" and sp["links"][0]["steps"] == "11-"
    steps = [dict(text="Build it.", cam=((0, 0, 0), 100)), dict(text="The answer is here.", cam=((1, 0, 0), 100)),
             dict(text="Congratulations, you built it. Follow for more.", cam=((0, 0, 0), 100), min=8.4,
                  sfx=[("w:built", "ding"), ("w:follow", "pop")])]
    out = open_loop(steps, "Why is it so?", answer_step=1, ending_text="Follow for more. Because remember,",
                    reminder=(0, "Hold that thought."), reveal="Here's the answer.")
    assert len(out) == 4 and out[0]["teaser"]["step"] == 2 and out[1]["cam_dur"] == 0.01
    assert out[1]["text"].endswith("Hold that thought.") and out[2]["text"].startswith("Here's the answer.")
    assert out[-1]["sfx"] == [("w:follow", "pop")] and out[-1]["min"] == 6.0
