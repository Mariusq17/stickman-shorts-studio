import math

import numpy as np
import pytest

from stickman_studio.config import RenderSettings, THEMES
from stickman_studio.figure import EXPRESSIONS
from stickman_studio.props import PROPS
from stickman_studio.renderer import SceneRenderer, uniform_timeline
from stickman_studio.rig import ACTIONS, POSE_KEYS, StickmanRig, action_pose, ik_arm
from stickman_studio.script_model import Script, Shot

REQUIRED_ACTIONS = ["idle_breathing", "walk", "run_panic", "explain_gestures", "point_at",
                    "panic_hands_up", "facepalm", "type_on_laptop", "celebrate_jump", "think_chin",
                    "argue_wildly", "fall_down_dramatic", "nod_yes", "shake_head_no", "shock_freeze",
                    "mic_drop", "sip_coffee", "plot_evil"]
REQUIRED_EXPR = ["neutral", "happy", "shocked", "angry", "sad", "smug", "deadpan", "mind_blown"]
REQUIRED_PROPS = ["laptop", "desk", "chart_up", "chart_down", "clock", "question", "exclamation", "bulb",
                  "money", "subscribe", "like", "comment", "coffee", "wall_door"]


def test_required_library_present():
    assert all(a in ACTIONS for a in REQUIRED_ACTIONS)
    assert all(e in EXPRESSIONS for e in REQUIRED_EXPR)
    assert all(p in PROPS for p in REQUIRED_PROPS)


@pytest.mark.parametrize("action", list(ACTIONS))
def test_action_poses_are_finite_and_grounded(action):
    rig = StickmanRig(500, 300, 900)
    for t in np.linspace(0, 4, 25):
        pose, fx = action_pose(action, float(t), 4.0, 1.0)
        assert set(POSE_KEYS) <= set(pose)
        sk = rig.solve(pose)
        for x, y in sk.pts.values():
            assert math.isfinite(x) and math.isfinite(y)
        lowest = max(sk.pts["l_foot"][1], sk.pts["r_foot"][1], sk.head_c[1] + sk.head_r, sk.pts["hip"][1])
        assert lowest <= 900 + 1e-6 + 60   # never sinks below the floor (squash tolerance)


def test_ik_reaches_target():
    up, lo = ik_arm((0.2, 0.1), 0.0, 1.0)
    rig = StickmanRig(1.0, 0.0, 0.0)
    from stickman_studio.rig import P
    sk = rig.solve(P(r_up=up, r_lo=lo))
    hand = np.array(sk.pts["r_hand"]) - np.array(sk.pts["neck"])
    assert np.allclose(hand, [0.2, 0.1], atol=1e-3)


def _script():
    shots = []
    props = list(PROPS)
    exprs = REQUIRED_EXPR + ["evil"]
    for i, a in enumerate(ACTIONS):
        shots.append(Shot(text="Testing frame number %d now" % i, action=a, expression=exprs[i % len(exprs)],
                          props=[props[i % len(props)]], camera=["static", "zoom_in", "punch_in",
                                                                  "dramatic_camera_shake", "pan_left"][i % 5],
                          guest=(a == "argue_wildly")))
    return Script("Test", "t", "x", "en", 60, "subscribe", shots, hook_text="Test hook")


@pytest.mark.parametrize("fmt", ["vertical", "horizontal"])
@pytest.mark.parametrize("theme", list(THEMES))
def test_render_frames_every_action(fmt, theme):
    sc = _script()
    st = RenderSettings(format=fmt, theme=theme, scale=0.25)
    tl = uniform_timeline(sc)
    r = SceneRenderer(sc, tl, st)
    bg = np.asarray(r.bg).astype(np.float32)
    for tm in tl:
        img = r.render(tm.start + min(1.3, tm.duration - 0.05))
        arr = np.asarray(img)
        assert arr.shape == (st.size[1], st.size[0], 3)
        assert arr.std() > 8          # something was actually drawn
        ink = np.array(THEMES[theme].ink)
        near_ink = (np.abs(arr.astype(int) - ink).sum(axis=2) < 60).mean()
        assert near_ink > 0.002       # the stickman (ink colored) is visible


def test_full_resolution_sizes():
    assert RenderSettings(format="vertical").size == (1080, 1920)
    assert RenderSettings(format="horizontal").size == (1920, 1080)
