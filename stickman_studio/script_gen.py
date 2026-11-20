"""Entertaining script & storyboard generator (100% offline).

Builds a story with: hook -> setup -> beats with a pattern interrupt every
~15-20 s -> climax -> lead-in -> Call To Action. Word count and shot count are
calibrated to the requested duration (15 s .. 180 s)."""
from __future__ import annotations

import random

from . import content_en, content_ro
from .camera import CAMERA_MOVES
from .config import MAX_DURATION, MIN_DURATION, WORDS_PER_SECOND
from .figure import EXPRESSIONS
from .props import PROPS
from .rig import ACTIONS, DEFAULT_EXPRESSION
from .script_model import Script, Shot

CONTENT = {"en": content_en, "ro": content_ro}
CUSTOM_ID = "custom"
SECONDS_PER_INTERRUPT = 15.5

CUSTOM_SLOTS = {
    "en": {"villain": "Murphy's law", "item": "my phone", "place": "home"},
    "ro": {"villain": "legea lui Murphy", "item": "telefonul", "place": "acasă"},
}


def content(lang: str):
    return CONTENT.get(lang, content_en)


def list_themes(lang: str = "en") -> list:
    """[(theme_id, category, title)]"""
    c = content(lang)
    return [(k, v["category"], v["title"]) for k, v in c.THEMES.items()]


def target_words(duration: float) -> int:
    return int(round(clamp_duration(duration) * WORDS_PER_SECOND))


def clamp_duration(d: float) -> float:
    return float(max(MIN_DURATION, min(MAX_DURATION, d)))


def _fmt(text: str, slots: dict) -> str:
    try:
        return text.format(**slots)
    except (KeyError, IndexError, ValueError):
        return text


def _shot(beat, slots, kind="beat") -> Shot:
    text, action, expr, props, cam = beat
    props_l = [p.strip() for p in props.split(",") if p.strip()] if isinstance(props, str) else list(props)
    return Shot(text=_fmt(text, slots), action=action,
                expression=expr or DEFAULT_EXPRESSION.get(action, "neutral"),
                props=props_l, camera=cam, kind=kind)


def generate_script(theme_id: str | None = None, duration: float = 60, language: str = "en",
                    cta_type: str = "subscribe", cta_custom: str = "", energy: int = 3,
                    seed: int | None = None, custom_topic: str = "") -> Script:
    duration = clamp_duration(duration)
    rng = random.Random(seed if seed is not None else random.randrange(1 << 30))
    seed_v = seed if seed is not None else 0
    c = content(language)
    themes = c.THEMES
    if custom_topic.strip():
        theme_id = CUSTOM_ID
    if theme_id != CUSTOM_ID and theme_id not in themes:
        theme_id = rng.choice(list(themes))

    if theme_id == CUSTOM_ID:
        topic = custom_topic.strip() or "life"
        slots = dict(CUSTOM_SLOTS.get(language, CUSTOM_SLOTS["en"]))
        slots.update(subject=topic, topic=topic)
        th = {
            "title": topic[:1].upper() + topic[1:],
            "hooks": [(h, "point_at", "smug", "question", "punch_in") for h in c.CUSTOM_HOOKS],
            "setup": [(c.CUSTOM_SETUP, "shrug", "deadpan", "", "static")],
            "beats": [],
            "twists": [],
            "climax": [(c.CUSTOM_CLIMAX, "mic_drop", "smug", "", "zoom_in")],
            "debate": c.CUSTOM_DEBATE,
        }
    else:
        th = themes[theme_id]
        slots = dict(th["slots"])
        slots["topic"] = th["topic"]
    slots["villain_cap"] = slots.get("villain", "")[:1].upper() + slots.get("villain", "")[1:]

    tw = target_words(duration)

    # ---- fixed parts
    hook = _shot(rng.choice(th["hooks"]), slots, "hook")
    ending = []
    if duration >= 30:
        ending.append(_shot(th["climax"][0], slots, "climax"))
    if duration >= 75:
        ending.append(Shot(text=rng.choice(c.LEAD_INS), action="nod_yes", expression="happy",
                           camera="zoom_out", kind="beat"))
    cta = build_cta(language, cta_type, cta_custom, _fmt(th["debate"], slots), rng)
    ending.append(cta)

    # ---- body pools
    beats = [_shot(b, slots) for b in th["beats"]]
    generic = [_shot(b, slots) for b in c.GENERIC_BEATS]
    rng.shuffle(generic)
    body_pool = beats + generic
    twists = [_fmt(t, slots) for t in th["twists"]]
    gtw = [_fmt(t, slots) for t in c.GENERIC_TWISTS]
    rng.shuffle(gtw)
    twist_pool = twists + gtw
    prefixes = list(c.INTERRUPTS)
    rng.shuffle(prefixes)

    setup = [_shot(s, slots, "setup") for s in th["setup"]] if duration >= 25 else []
    body = list(setup)
    words = hook.words + sum(s.words for s in ending) + sum(s.words for s in body)
    max_shots = 35
    since_interrupt_s = (hook.words + sum(s.words for s in body)) / WORDS_PER_SECOND
    interrupts = 0
    while len(body) + 1 + len(ending) < max_shots:
        make_interrupt = since_interrupt_s >= SECONDS_PER_INTERRUPT and twist_pool and len(body) >= 1
        if make_interrupt:
            cand = _interrupt(prefixes, twist_pool, interrupts)
        else:
            if not body_pool:
                break
            cand = body_pool[0]
        if words + cand.words > tw * 1.06:
            # try a shorter candidate before giving up
            if not make_interrupt:
                shorter = [b for b in body_pool if words + b.words <= tw * 1.06]
                if shorter:
                    cand = shorter[0]
                    body_pool.remove(cand)
                    body.append(cand)
                    words += cand.words
                    since_interrupt_s += cand.words / WORDS_PER_SECOND
                    continue
            break
        if make_interrupt:
            interrupts += 1
            since_interrupt_s = 0.0
        else:
            body_pool.pop(0)
            since_interrupt_s += cand.words / WORDS_PER_SECOND
        body.append(cand)
        words += cand.words

    if duration >= 25 and interrupts == 0 and twist_pool:
        twist_pool.sort(key=lambda x: len(x.split()))
        ins = _interrupt(prefixes, twist_pool, 0)
        if body and body[-1].kind == "beat":
            body[-1] = ins
        else:
            body.append(ins)
        fixed = hook.words + sum(x.words for x in ending)
        while fixed + sum(x.words for x in body) > tw * 1.08 and len(body) > 1:
            removable = [x for x in body if x.kind != "interrupt"]
            if not removable:
                break
            body.remove(min(removable, key=lambda x: abs(fixed + sum(b.words for b in body) - x.words - tw)))
    shots = [hook] + body + ending
    _pad_words(shots, tw, c.TAGS, rng)
    _split_for_pacing(shots, desired_shots(duration))
    _apply_energy(shots, energy, rng)
    _vary_cameras(shots, rng)
    title = th["title"]
    script = Script(title=title, topic=slots.get("topic", ""), theme_id=theme_id, language=language,
                    target_duration=duration, cta_type=cta_type, shots=shots, hook_text=title,
                    cta_text=cta.text, seed=seed_v)
    return validate_script(script)


def _interrupt(prefixes, twist_pool, n) -> Shot:
    pref = prefixes[n % len(prefixes)]
    tw_text = twist_pool.pop(0)
    act = ["shock_freeze", "point_at", "panic_hands_up", "shock_freeze"][n % 4]
    expr = "mind_blown" if n % 3 == 2 else DEFAULT_EXPRESSION[act]
    return Shot(text=f"{pref} {tw_text}", action=act, expression=expr, props=["exclamation"],
                camera="punch_in" if n % 2 == 0 else "dramatic_camera_shake", kind="interrupt")


def build_cta(language, cta_type, cta_custom, debate, rng) -> Shot:
    c = content(language)
    if cta_type == "custom" and not cta_custom.strip():
        cta_type = "subscribe"
    templates = c.CTA.get(cta_type) or c.CTA["subscribe"]
    text = rng.choice(templates).format(debate=debate, custom=cta_custom.strip())
    props = {"subscribe": ["subscribe"], "comment": ["comment"], "save_share": ["save"],
             "custom": ["like"]}.get(cta_type, ["subscribe"])
    return Shot(text=text, action="cta_point", expression="happy", props=props, camera="zoom_in",
                kind="cta")


def _pad_words(shots, tw, tags, rng):
    words = sum(s.words for s in shots)
    guard = 0
    while words < tw * 0.93 and guard < 40:
        guard += 1
        cands = [s for s in shots if s.kind not in ("cta",) and s.words < 24]
        if not cands:
            break
        s = min(cands, key=lambda x: x.words)
        tag = rng.choice(tags)
        s.text = s.text.rstrip() + " " + tag
        words += len(tag.split())


def desired_shots(duration: float) -> int:
    return int(max(3, min(35, round(clamp_duration(duration) / 5.5))))


def _split_for_pacing(shots, desired):
    """Split long multi-sentence shots into two cuts; the punchline gets a punch-in."""
    import re
    guard = 0
    while len(shots) < desired and guard < 40:
        guard += 1
        best, best_i, best_cut = None, -1, None
        for i, s in enumerate(shots):
            if s.kind not in ("beat", "setup", "climax", "hook") or s.words < 13:
                continue
            cuts = [m.end() for m in re.finditer(r"[.!?…]\s+", s.text)]
            cuts = [c for c in cuts if 4 <= len(s.text[:c].split()) and len(s.text[c:].split()) >= 2]
            if not cuts:
                continue
            mid = len(s.text) / 2
            cut = min(cuts, key=lambda c: abs(c - mid))
            if best is None or s.words > best.words:
                best, best_i, best_cut = s, i, cut
        if best is None:
            break
        first, second = best.text[:best_cut].strip(), best.text[best_cut:].strip()
        best.text = first
        cam = "punch_in" if best.camera != "punch_in" else "zoom_out"
        shots.insert(best_i + 1, Shot(text=second, action=best.action, expression=best.expression,
                                      props=list(best.props), camera=cam, guest=best.guest,
                                      kind=best.kind if best.kind not in ("setup", "hook") else "beat"))


def _apply_energy(shots, energy, rng):
    energy = max(1, min(5, int(energy)))
    for i, s in enumerate(shots):
        if energy <= 2:
            if s.camera == "dramatic_camera_shake":
                s.camera = "zoom_in"
            if s.camera == "punch_in" and s.kind != "hook":
                s.camera = "zoom_in"
            if s.action == "run_panic":
                s.action = "panic_hands_up"
        if energy >= 4:
            if s.kind == "interrupt":
                s.camera = "dramatic_camera_shake" if i % 2 else "punch_in"
            if s.action == "argue_wildly":
                s.guest = True
            if energy == 5 and s.kind == "beat" and s.action in ("celebrate_jump", "explain_gestures",
                                                                  "panic_hands_up") and not s.props:
                s.guest = rng.random() < 0.6
        if s.action == "argue_wildly" and energy >= 3 and not any(
                PROPS.get(p, (None, ""))[1] in ("side", "side_floor", "cta") for p in s.props):
            s.guest = True


def _vary_cameras(shots, rng):
    """Avoid two identical consecutive camera moves (visual pattern interrupt)."""
    cycle = ["zoom_in", "static", "pan_right", "zoom_out", "pan_left", "static"]
    for i in range(1, len(shots)):
        if shots[i].camera == shots[i - 1].camera and shots[i].kind not in ("cta", "interrupt"):
            options = [c for c in cycle if c != shots[i - 1].camera]
            shots[i].camera = rng.choice(options)


def validate_script(script: Script) -> Script:
    """Repairs unknown actions/expressions/props/cameras (e.g. after manual edits or LLM output)."""
    for s in script.shots:
        s.text = " ".join(str(s.text).split())
        if s.action not in ACTIONS:
            s.action = "talk"
        if s.expression not in EXPRESSIONS:
            s.expression = DEFAULT_EXPRESSION.get(s.action, "neutral")
        s.props = [p for p in s.props if p in PROPS][:3]
        if s.camera not in CAMERA_MOVES:
            s.camera = "static"
    script.shots = [s for s in script.shots if s.text]
    if not script.shots:
        script.shots = [Shot(text="...", action="idle_breathing")]
    return script


def random_idea(language: str = "en", seed: int | None = None):
    rng = random.Random(seed)
    tid, cat, title = rng.choice(list_themes(language))
    return tid, cat, title


def estimate_duration(script: Script) -> float:
    return sum(max(1.4, s.words / WORDS_PER_SECOND + 0.35) for s in script.shots)
