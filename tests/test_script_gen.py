import pytest

from stickman_studio.camera import CAMERA_MOVES
from stickman_studio.figure import EXPRESSIONS
from stickman_studio.props import PROPS
from stickman_studio.rig import ACTIONS
from stickman_studio.script_gen import generate_script, list_themes, target_words
from stickman_studio.script_model import Script


@pytest.mark.parametrize("lang", ["en", "ro"])
def test_at_least_12_themes(lang):
    themes = list_themes(lang)
    assert len(themes) >= 12
    cats = {c for _, c, _ in themes}
    assert len(cats) >= 5  # tech, money, productivity, psychology, everyday, curiosities


def _check_valid(s: Script):
    for sh in s.shots:
        assert sh.text.strip()
        assert sh.action in ACTIONS
        assert sh.expression in EXPRESSIONS
        assert sh.camera in CAMERA_MOVES
        assert all(p in PROPS for p in sh.props)


@pytest.mark.parametrize("lang", ["en", "ro"])
@pytest.mark.parametrize("cta", ["subscribe", "comment", "save_share", "custom"])
def test_60s_script_with_cta(lang, cta):
    for tid, _, _ in list_themes(lang):
        s = generate_script(tid, 60, lang, cta, cta_custom="Follow for part 2!", seed=7)
        _check_valid(s)
        assert 125 <= s.word_count <= 165, (tid, s.word_count)
        assert 10 <= len(s.shots) <= 12, (tid, len(s.shots))
        last = s.shots[-1]
        assert last.kind == "cta" and last.action == "cta_point"
        assert last.props and last.props[0] in ("subscribe", "comment", "save", "like")
        if cta == "custom":
            assert "Follow for part 2!" in last.text
        assert s.shots[0].kind == "hook"
        assert any(x.kind == "interrupt" for x in s.shots)


@pytest.mark.parametrize("lang", ["en", "ro"])
def test_180s_script_long_form(lang):
    for tid, _, _ in list_themes(lang):
        s = generate_script(tid, 180, lang, "comment", seed=3)
        _check_valid(s)
        assert 400 <= s.word_count <= 480, (tid, s.word_count)
        assert 25 <= len(s.shots) <= 35, (tid, len(s.shots))
        assert s.shots[-1].kind == "cta"
        # pattern interrupt roughly every 15-20 seconds
        assert sum(x.kind == "interrupt" for x in s.shots) >= 5


@pytest.mark.parametrize("dur", [15, 20, 30, 45, 90, 120, 150])
def test_word_calibration_all_durations(dur):
    s = generate_script(None, dur, "en", "subscribe", seed=dur)
    tw = target_words(dur)
    assert 0.85 * tw <= s.word_count <= 1.12 * tw
    assert len(s.shots) >= 3
    if dur >= 25:
        assert any(x.kind == "interrupt" for x in s.shots)


def test_custom_topic_and_roundtrip():
    s = generate_script(None, 60, "ro", "comment", custom_topic="pisicile de birou", seed=1)
    assert s.theme_id == "custom"
    assert "pisicile de birou" in s.full_text
    s2 = Script.from_dict(s.to_dict())
    assert s2.full_text == s.full_text and len(s2.shots) == len(s.shots)


def test_duration_clamped():
    assert generate_script(None, 5, "en").target_duration == 15
    assert generate_script(None, 999, "en").target_duration == 180


def test_llm_fallback_offline():
    from stickman_studio.llm import generate_with_llm
    s, used, msg = generate_with_llm("ollama", "coffee", 30, "en", base_url="http://127.0.0.1:9",
                                     timeout=1)
    assert not used
    assert s.shots[-1].kind == "cta"
