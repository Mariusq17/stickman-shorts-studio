"""OPTIONAL script generation with a local Ollama model or any OpenAI-compatible
API key. Uses only the standard library. Every failure falls back to the
offline generator, so the app never depends on the network."""
from __future__ import annotations

import json
import re
import urllib.request

from .camera import CAMERA_MOVES
from .config import WORDS_PER_SECOND
from .figure import EXPRESSIONS
from .props import PROP_NAMES
from .rig import ACTIONS
from .script_gen import build_cta, clamp_duration, desired_shots, generate_script, validate_script
from .script_model import Script, Shot

LANG_NAMES = {"en": "English", "ro": "Romanian"}


def build_prompt(topic: str, duration: float, language: str, cta_type: str, cta_custom: str,
                 energy: int) -> str:
    words = int(clamp_duration(duration) * WORDS_PER_SECOND)
    shots = desired_shots(duration)
    return f"""You are a viral short-form video writer. Write an EXTREMELY entertaining stickman
storytime script about: "{topic}".
Language: {LANG_NAMES.get(language, language)}. Total length: about {words} words, {shots} shots
(each shot 1-2 short sentences). Tone: alert, conversational, funny, unexpected comparisons,
a mini plot twist / pattern interrupt every 15-20 seconds. Energy level {energy}/5.
Shot 1 is a scroll-stopping HOOK. The last shot is a natural Call To Action of type "{cta_type}"
{('with this text: ' + cta_custom) if cta_custom else ''} woven into the story.
Return ONLY JSON: {{"title": str, "shots": [{{"text": str, "action": str, "expression": str,
"props": [str], "camera": str}}]}}
Allowed actions: {', '.join(ACTIONS)}
Allowed expressions: {', '.join(EXPRESSIONS)}
Allowed props (0-2 per shot): {', '.join(PROP_NAMES)}
Allowed camera: {', '.join(CAMERA_MOVES)}
The final shot must use action "cta_point"."""


def _post(url: str, payload: dict, headers: dict, timeout: float) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in model output")
    return json.loads(m.group(0))


def ollama_models(base_url: str = "http://localhost:11434", timeout: float = 2.0) -> list:
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/api/tags", timeout=timeout) as r:
            return [m["name"] for m in json.loads(r.read().decode()).get("models", [])]
    except Exception:
        return []


def generate_with_llm(provider: str, topic: str, duration: float, language: str = "en",
                      cta_type: str = "subscribe", cta_custom: str = "", energy: int = 3,
                      model: str = "llama3.1", base_url: str = "", api_key: str = "",
                      timeout: float = 120.0):
    """Returns (Script, used_llm: bool, message)."""
    prompt = build_prompt(topic, duration, language, cta_type, cta_custom, energy)
    try:
        if provider == "ollama":
            url = (base_url or "http://localhost:11434").rstrip("/") + "/api/generate"
            out = _post(url, {"model": model, "prompt": prompt, "stream": False, "format": "json"}, {},
                        timeout)
            data = _extract_json(out.get("response", ""))
        elif provider == "openai":
            url = (base_url or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
            out = _post(url, {"model": model, "messages": [{"role": "user", "content": prompt}],
                              "temperature": 0.9}, {"Authorization": f"Bearer {api_key}"}, timeout)
            data = _extract_json(out["choices"][0]["message"]["content"])
        else:
            raise ValueError("unknown provider")
        shots = [Shot.from_dict(s) for s in data.get("shots", []) if str(s.get("text", "")).strip()]
        if len(shots) < 2:
            raise ValueError("model returned too few shots")
        for s in shots:
            s.kind = "beat"
        shots[0].kind = "hook"
        if shots[-1].action != "cta_point":
            import random
            shots.append(build_cta(language, cta_type, cta_custom,
                                   "What do you think? Tell me in the comments." if language == "en"
                                   else "Tu ce crezi? Spune-mi în comentarii.", random.Random(0)))
        shots[-1].kind = "cta"
        title = str(data.get("title") or topic)
        sc = Script(title=title, topic=topic, theme_id="llm", language=language,
                    target_duration=clamp_duration(duration), cta_type=cta_type, shots=shots,
                    hook_text=title, cta_text=shots[-1].text)
        return validate_script(sc), True, f"Script generat cu {provider}:{model}"
    except Exception as e:  # graceful offline fallback
        sc = generate_script(None, duration, language, cta_type, cta_custom, energy, custom_topic=topic)
        return sc, False, f"LLM indisponibil ({type(e).__name__}: {e}). Am folosit generatorul offline."
