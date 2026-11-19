"""Stickman Video Studio — interfață web Streamlit (100% offline).

Pornire:  streamlit run app.py
"""
from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime

import pandas as pd
import streamlit as st

from stickman_studio.camera import CAMERA_MOVES
from stickman_studio.config import (CTA_TYPES, FORMAT_LABELS, MAX_DURATION, MIN_DURATION, THEMES,
                                    RenderSettings)
from stickman_studio.figure import EXPRESSIONS
from stickman_studio.pipeline import build_video, render_preview_frame
from stickman_studio.props import PROP_NAMES
from stickman_studio.rig import ACTIONS
from stickman_studio.script_gen import (estimate_duration, generate_script, list_themes, target_words,
                                        desired_shots, validate_script)
from stickman_studio.script_model import Script, Shot

APP_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(APP_DIR, "output")
KINDS = ["hook", "setup", "beat", "interrupt", "climax", "cta"]

st.set_page_config(page_title="Stickman Video Studio", page_icon="🎬", layout="wide")

# ----------------------------------------------------------------- state
ss = st.session_state
ss.setdefault("duration", 60)
ss.setdefault("script", None)
ss.setdefault("editor_ver", 0)
ss.setdefault("last_video", None)
ss.setdefault("last_info", None)


def set_duration(v):
    ss["duration"] = v


@st.cache_resource(show_spinner=False)
def cached_voices():
    try:
        from stickman_studio.tts import list_voices
        return list_voices()
    except Exception:
        return []


# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("⚙️ Setări video")
    lang = st.radio("Limba scriptului / vocii", ["en", "ro"], horizontal=True,
                    format_func=lambda x: {"en": "🇬🇧 English", "ro": "🇷🇴 Română"}[x])
    fmt = st.radio("Format video", list(FORMAT_LABELS), format_func=lambda k: FORMAT_LABELS[k])

    st.markdown("**Durată țintă**")
    c1, c2, c3, c4 = st.columns(4)
    c1.button("30s", on_click=set_duration, args=(30,))
    c2.button("60s", on_click=set_duration, args=(60,))
    c3.button("90s", on_click=set_duration, args=(90,))
    c4.button("3 min", on_click=set_duration, args=(180,))
    duration = st.slider("Secunde", MIN_DURATION, MAX_DURATION, step=5, key="duration")
    st.caption(f"≈ {target_words(duration)} cuvinte · ≈ {desired_shots(duration)} shot-uri")

    energy = st.slider("Nivel energie / umor", 1, 5, 3,
                       help="1 = calm & explicativ · 5 = haos total (camera shake, personaj invitat, reacții exagerate)")
    cta_type = st.selectbox("Tip Call-to-Action", list(CTA_TYPES), format_func=lambda k: CTA_TYPES[k])
    cta_custom = ""
    if cta_type == "custom":
        cta_custom = st.text_input("Text CTA personalizat", "Follow pentru partea a doua!")

    fps = st.radio("FPS", [30, 24], horizontal=True)
    visual = st.selectbox("Temă vizuală", list(THEMES), format_func=lambda k: THEMES[k].label)
    voice_rate = st.slider("Viteză voce", 0.6, 1.6, 1.0, 0.05)

    with st.expander("🔊 Voce & audio"):
        tts_engine = st.selectbox("Motor TTS", ["auto", "pyttsx3", "procedural"],
                                  format_func=lambda k: {"auto": "Auto (SAPI5/pyttsx3 → fallback procedural)",
                                                         "pyttsx3": "pyttsx3 / Windows SAPI5",
                                                         "procedural": "Voce procedurală (cartoon, mereu offline)"}[k])
        voice_id = None
        if tts_engine != "procedural":
            voices = cached_voices()
            if voices:
                labels = ["(automat după limbă)"] + [v["name"] for v in voices]
                pick = st.selectbox("Voce", labels)
                if pick != labels[0]:
                    voice_id = voices[labels.index(pick) - 1]["id"]
            else:
                st.caption("pyttsx3 nu a găsit voci — se va folosi vocea procedurală.")
        voice_pitch = st.slider("Ton voce procedurală", 0.7, 1.5, 1.0, 0.05)
        music = st.checkbox("Muzică de fundal", True)
        music_volume = st.slider("Volum muzică", 0.0, 0.4, 0.12, 0.01)
        sfx = st.checkbox("Efecte sonore (SFX)", True)
        fit = st.checkbox("Potrivește automat durata la țintă", True)

    with st.expander("🖼️ Avansat"):
        subtitles = st.checkbox("Subtitrări dinamice", True)
        progress_bar = st.checkbox("Bară de progres în video", True)
        quality = st.selectbox("Rezoluție", [1.0, 0.75, 0.5],
                               format_func=lambda x: {1.0: "100% (Full HD)", 0.75: "75%", 0.5: "50% (draft rapid)"}[x])
        crf = st.slider("Calitate H.264 (CRF, mai mic = mai bun)", 16, 30, 21)

    with st.expander("🤖 AI opțional (Ollama local / API Key)"):
        provider = st.selectbox("Furnizor", ["none", "ollama", "openai"],
                                format_func=lambda k: {"none": "Niciunul (generator offline)",
                                                       "ollama": "Ollama local",
                                                       "openai": "API compatibil OpenAI"}[k])
        llm_model = st.text_input("Model", "llama3.1" if provider != "openai" else "gpt-4o-mini")
        llm_url = st.text_input("Base URL", "http://localhost:11434" if provider == "ollama" else "")
        llm_key = st.text_input("API Key", type="password") if provider == "openai" else ""
        st.caption("Opțional. Dacă AI-ul nu răspunde, se folosește automat generatorul offline.")


def current_settings() -> RenderSettings:
    return RenderSettings(format=fmt, fps=int(fps), theme=visual, scale=float(quality), language=lang,
                          voice_rate=float(voice_rate), voice_id=voice_id, tts_engine=tts_engine,
                          voice_pitch=float(voice_pitch), target_duration=float(duration),
                          fit_to_target=fit, energy=int(energy), music=music,
                          music_volume=float(music_volume), sfx=sfx, subtitles=subtitles,
                          progress_bar=progress_bar, crf=int(crf))


# ----------------------------------------------------------------- main
st.title("🎬 Stickman Video Studio")
st.caption("Videoclipuri animate cu stickmeni, 100% offline — Shorts · Reels · TikTok · YouTube")

st.subheader("1 · 💡 Idee & script")
themes = list_themes(lang)
theme_labels = {tid: f"{cat} — {title}" for tid, cat, title in themes}
col_a, col_b = st.columns([3, 2])
with col_a:
    theme_id = st.selectbox("Temă predefinită", list(theme_labels), format_func=lambda k: theme_labels[k])
with col_b:
    custom_topic = st.text_input("…sau subiect propriu (opțional)",
                                 placeholder="ex: pisicile care urăsc lunea")

b1, b2 = st.columns([3, 2])
gen_clicked = b1.button("✨ Generează idee & script entertaining automat", type="primary")
rnd_clicked = b2.button("🎲 Idee random")

if gen_clicked or rnd_clicked:
    seed = random.randrange(1 << 30)
    tid = random.choice([t[0] for t in themes]) if rnd_clicked else theme_id
    topic = "" if rnd_clicked else custom_topic
    with st.spinner("Scriu un script captivant..."):
        if provider != "none":
            from stickman_studio.llm import generate_with_llm
            subject = topic or dict((t[0], t[2]) for t in themes)[tid]
            script, used, msg = generate_with_llm(provider, subject, duration, lang, cta_type, cta_custom,
                                                  energy, model=llm_model, base_url=llm_url, api_key=llm_key)
            (st.success if used else st.warning)(msg)
        else:
            script = generate_script(tid, duration, lang, cta_type, cta_custom, energy, seed,
                                     custom_topic=topic)
    ss["script"] = script.to_dict()
    ss["editor_ver"] += 1

with st.expander("📂 Import / export script (JSON)"):
    up = st.file_uploader("Încarcă script JSON", type=["json"])
    if up is not None and st.button("Încarcă"):
        ss["script"] = Script.from_dict(json.load(up)).to_dict()
        ss["editor_ver"] += 1
    if ss["script"]:
        st.download_button("⬇️ Exportă scriptul curent", json.dumps(ss["script"], ensure_ascii=False, indent=2),
                           file_name="stickman_script.json", mime="application/json")

if not ss["script"]:
    st.info("Apasă **„Generează idee & script entertaining automat”** pentru a începe.")
    st.stop()

# ----------------------------------------------------------------- storyboard
st.subheader("2 · 🎞️ Storyboard — editor pe shot-uri")
sd = ss["script"]
t1, t2 = st.columns(2)
sd["title"] = t1.text_input("Titlu video", sd.get("title", ""), key=f"title_{ss['editor_ver']}")
sd["hook_text"] = t2.text_input("Text hook (banner sus)", sd.get("hook_text", ""), key=f"hook_{ss['editor_ver']}")

df = pd.DataFrame([{
    "kind": s.get("kind", "beat"), "text": s["text"], "action": s["action"],
    "expression": s["expression"], "props": ", ".join(s.get("props", [])),
    "camera": s["camera"], "guest": bool(s.get("guest", False)),
} for s in sd["shots"]])

edited = st.data_editor(
    df, num_rows="dynamic", key=f"editor_{ss['editor_ver']}", hide_index=False,
    column_config={
        "kind": st.column_config.SelectboxColumn("Tip", options=KINDS, width="small"),
        "text": st.column_config.TextColumn("Text (voiceover + subtitrare)", width="large", required=True),
        "action": st.column_config.SelectboxColumn("Acțiune stickman", options=list(ACTIONS), required=True),
        "expression": st.column_config.SelectboxColumn("Expresie", options=EXPRESSIONS),
        "props": st.column_config.TextColumn("Recuzită (virgulă)", help="Disponibile: " + ", ".join(PROP_NAMES)),
        "camera": st.column_config.SelectboxColumn("Cameră", options=CAMERA_MOVES),
        "guest": st.column_config.CheckboxColumn("Invitat"),
    },
)


def script_from_editor() -> Script:
    shots = []
    for _, row in edited.iterrows():
        text = str(row.get("text") or "").strip()
        if not text or text == "nan":
            continue
        shots.append(Shot.from_dict({
            "text": text, "action": row.get("action") or "talk",
            "expression": row.get("expression") or "neutral", "props": str(row.get("props") or ""),
            "camera": row.get("camera") or "static", "guest": bool(row.get("guest")),
            "kind": row.get("kind") or "beat"}))
    sc = Script.from_dict({**sd, "shots": []})
    sc.shots = shots
    sc.language = sd.get("language", lang)
    sc.target_duration = float(duration)
    return validate_script(sc)


cur = script_from_editor()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Cuvinte", cur.word_count, f"țintă {target_words(duration)}")
m2.metric("Shot-uri", len(cur.shots))
m3.metric("Durată estimată", f"{estimate_duration(cur):.0f}s", f"țintă {duration}s")
m4.metric("CTA", CTA_TYPES.get(sd.get("cta_type", cta_type), "-"))
st.caption("Acțiuni disponibile: " + ", ".join(ACTIONS))

pc1, pc2 = st.columns([1, 2])
with pc1:
    shot_no = st.number_input("Preview shot #", 1, max(1, len(cur.shots)), 1)
    t_in = st.slider("Moment în shot (s)", 0.0, 4.0, 1.2, 0.1)
    if st.button("👁️ Preview cadru"):
        prev_st = current_settings()
        prev_st.scale = 0.5
        ss["preview"] = render_preview_frame(cur, prev_st, int(shot_no) - 1, t_in)
with pc2:
    if ss.get("preview") is not None:
        st.image(ss["preview"], caption=f"Shot {shot_no}", width=320 if fmt == "vertical" else 560)

# ----------------------------------------------------------------- render
st.subheader("3 · 🚀 Generare video")
if st.button("🎥 Generează Video Complet (MP4)", type="primary"):
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(OUT_DIR, f"stickman_{fmt}_{int(duration)}s_{stamp}.mp4")
    bar = st.progress(0.0, text="Pornesc...")
    log_box = st.empty()
    logs = []

    def on_progress(frac, msg):
        bar.progress(min(1.0, max(0.0, frac)), text=msg)

    def on_log(msg):
        logs.append(msg)
        log_box.caption(" · ".join(logs[-3:]))

    t0 = time.time()
    try:
        res = build_video(cur, current_settings(), out, progress=on_progress, log=on_log)
        ss["last_video"] = res.path
        ss["last_info"] = (f"✅ Gata în {time.time() - t0:.0f}s — {res.duration:.1f}s video, "
                           f"{res.size[0]}x{res.size[1]} @ {res.fps}fps, {len(res.shot_durations)} shot-uri, "
                           f"voce: {res.tts_engine}")
        try:
            from stickman_studio.pipeline import verify_video
            v = verify_video(res.path)
            ss["last_info"] += f" · verificat MoviePy: audio {'✓' if v['has_audio'] else '✗'}"
        except Exception:
            pass
    except Exception as e:  # pragma: no cover - surfaced in UI
        st.error(f"Eroare la randare: {e}")

if ss.get("last_video") and os.path.exists(ss["last_video"]):
    st.success(ss.get("last_info") or "")
    vc1, vc2 = st.columns([1, 1]) if fmt == "vertical" else (st.container(), st.container())
    with vc1:
        with open(ss["last_video"], "rb") as f:
            data = f.read()
        st.video(data)
    with vc2:
        st.download_button("⬇️ Download MP4", data, file_name=os.path.basename(ss["last_video"]),
                           mime="video/mp4", type="primary")
        st.caption(f"Salvat și local în: `{ss['last_video']}`")
