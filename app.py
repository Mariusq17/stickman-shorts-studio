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

    with st.expander("🔊 Voce & audio", expanded=True):
        from stickman_studio.tts import ENGINE_LABELS, available_engines
        from stickman_studio.voices import CATALOG, DEFAULT_VOICE, local_voices, piper_installed
        engines = available_engines(lang)
        opts = ["auto", "piper", "sapi", "espeak", "procedural"]

        def _eng_label(k):
            if k == "auto":
                return "Auto (cea mai bună voce disponibilă)"
            ok, why = engines[k]
            return f"{'✅' if ok else '⛔'} {ENGINE_LABELS[k]}"

        tts_engine = st.selectbox("Motor voce (TTS)", opts, format_func=_eng_label)
        best = next((k for k in opts[1:] if engines[k][0]), "procedural")
        if tts_engine == "auto":
            st.caption(f"Se va folosi: **{ENGINE_LABELS[best]}**")
        if not engines["piper"][0]:
            st.warning("Vocea naturală **Piper** nu e pregătită pentru limba aleasă "
                       f"({engines['piper'][1]}). Descarc-o o singură dată (~60 MB), apoi merge offline.")
            if piper_installed() and st.button("⬇️ Descarcă vocea Piper pentru " + lang.upper()):
                from stickman_studio.voices import ensure_language
                with st.spinner("Descarc modelul de voce..."):
                    try:
                        ensure_language(lang, log=lambda m: None)
                        st.success("Vocea a fost descărcată. Gata de folosit offline!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Descărcarea a eșuat: {e}")
        piper_voice = None
        pv = [v for v in local_voices() if v[1] == lang]
        if pv and tts_engine in ("auto", "piper"):
            names = [v[0] for v in pv]
            default = names.index(DEFAULT_VOICE[lang]) if DEFAULT_VOICE.get(lang) in names else 0
            piper_voice = st.selectbox("Voce Piper", names, index=default,
                                       format_func=lambda k: CATALOG.get(k, (None, k))[1])
        voice_id = None
        if tts_engine == "sapi":
            voices = cached_voices()
            if voices:
                labels = ["(automat după limbă)"] + [v["name"] for v in voices]
                pick = st.selectbox("Voce de sistem", labels)
                if pick != labels[0]:
                    voice_id = voices[labels.index(pick) - 1]["id"]
        voice_pitch = 1.0
        if tts_engine in ("espeak", "procedural"):
            voice_pitch = st.slider("Ton voce", 0.7, 1.5, 1.0, 0.05)
        st.divider()
        from stickman_studio.audio import MUSIC_STYLES
        music_opts = ["auto", *MUSIC_STYLES, "file", "none"]
        music_style = st.selectbox("Muzică de fundal", music_opts, format_func=lambda k: {
            "auto": "Auto (după nivelul de energie)", "file": "🎵 Fișierul meu (mp3/wav)",
            "none": "Fără muzică"}.get(k, MUSIC_STYLES.get(k, k)))
        music_file = None
        if music_style == "file":
            up_m = st.file_uploader("Încarcă muzica (o folosești doar dacă ai drepturi asupra ei)",
                                    type=["mp3", "wav", "ogg", "m4a", "flac"])
            if up_m is not None:
                os.makedirs(os.path.join(OUT_DIR, "music"), exist_ok=True)
                music_file = os.path.join(OUT_DIR, "music", up_m.name)
                with open(music_file, "wb") as f:
                    f.write(up_m.getbuffer())
        music = music_style != "none"
        music_volume = st.slider("Volum muzică", 0.0, 0.4, 0.12, 0.01, disabled=not music)
        sfx = st.checkbox("Efecte sonore (SFX)", True)
        fit = st.checkbox("Potrivește automat durata la țintă", True)

    with st.expander("🖼️ Avansat"):
        subtitles = st.checkbox("Subtitrări dinamice", True)
        progress_bar = st.checkbox("Bară de progres în video", True)
        quality = st.selectbox("Rezoluție", [1.0, 0.75, 0.5],
                               format_func=lambda x: {1.0: "100% (Full HD)", 0.75: "75%", 0.5: "50% (draft rapid)"}[x])
        crf = st.slider("Calitate H.264 (CRF, mai mic = mai bun)", 16, 30, 21)
        antialias = st.checkbox("Linii netede (antialiasing 2x)", True,
                                help="Calitate vizuală mult mai bună; randarea durează ~2x mai mult.")

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
                          progress_bar=progress_bar, crf=int(crf), antialias=antialias,
                          music_style=music_style, music_file=music_file, piper_voice=piper_voice)


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
        if res.tts_engine == "procedural":
            st.warning("Video-ul a folosit vocea procedurală (doar sunete, fără cuvinte). "
                       "Descarcă vocea Piper din „Voce & audio” pentru o voce naturală.")
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
