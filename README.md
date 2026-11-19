# 🎬 Stickman Video Studio

Generator **100% offline** de videoclipuri animate 2D cu stickmeni: scripturi amuzante, voiceover, lip-sync, subtitrări dinamice, muzică, efecte sonore și export MP4 gata de urcat pe **YouTube Shorts, Instagram Reels, TikTok** (9:16) sau **YouTube** (16:9).

- Durată configurabilă **15 secunde – 3 minute (180s)**
- Nu ai nevoie de internet, cont sau chei API (doar la prima instalare a pachetelor Python)
- Totul e desenat din cod: Pillow + NumPy, iar exportul MP4 se face cu `imageio-ffmpeg` (ffmpeg vine inclus). MoviePy verifică fișierul exportat.

---

## 🚀 Pornire rapidă pe Windows (dublu-click)

1. Instalează **Python 3.10 – 3.13** de pe [python.org](https://www.python.org/downloads/) și bifează **„Add python.exe to PATH”** la instalare.
2. Descarcă / clonează acest folder.
3. Dă **dublu-click pe `START_STUDIO.bat`**.
   - Prima dată creează automat un mediu virtual (`venv`) și instalează `requirements.txt` (câteva minute).
   - La pornirile următoare deschide direct aplicația.
4. Se deschide browserul la **http://localhost:8501**. Ca să oprești aplicația, închide fereastra neagră.

> Dacă modifici `requirements.txt`, scriptul `.bat` detectează schimbarea și reinstalează automat.

### Pornire manuală (Windows / macOS / Linux)

```bash
python -m venv venv
```

```bash
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

---

## 🖥️ Cum folosești aplicația

**Sidebar (setări):**
| Setare | Opțiuni |
|---|---|
| Limbă script/voce | English, Română |
| Format video | 9:16 Vertical 1080×1920 (Shorts/Reels/TikTok) · 16:9 Horizontal 1920×1080 (YouTube) |
| Durată țintă | slider 15–180s + presetări rapide 30s / 60s / 90s / 3 min |
| Nivel energie / umor | 1 (calm) … 5 (haos: camera shake, personaj invitat, reacții exagerate) |
| Tip Call-to-Action | Subscribe/Follow · Comment bait (dezbatere) · Save/Share · Text personalizat |
| FPS | 24 / 30 |
| Temă vizuală | Light clasic · Dark Mode · Blueprint |
| Viteză voce | 0.6× – 1.6× |
| Voce & audio | motor TTS, voce SAPI5, ton, muzică, volum, SFX, potrivire automată a duratei |
| Avansat | subtitrări, bară de progres, rezoluție (100% / 75% / 50% draft), calitate CRF |
| AI opțional | Ollama local sau orice API compatibil OpenAI (cu API key) — complet opțional |

**Zona principală:**
1. **💡 Idee & script** — alegi una din cele 13 teme (sau scrii un subiect propriu) și apeși **„✨ Generează idee & script entertaining automat”** (sau **🎲 Idee random**).
2. **🎞️ Storyboard** — editezi fiecare shot: text (voiceover + subtitrare), acțiunea stickman-ului, expresia, recuzita, mișcarea camerei, personaj invitat. Vezi live numărul de cuvinte, shot-uri și durata estimată. Poți face **👁️ Preview cadru** și **import/export JSON**.
3. **🚀 Generare** — **„🎥 Generează Video Complet (MP4)”** cu bară de progres pe fiecare shot, apoi player integrat + **⬇️ Download MP4**. Videoclipurile se salvează și în folderul `output/`.

### Linie de comandă (fără interfață)

```bash
python -m stickman_studio.cli --list
```

```bash
python -m stickman_studio.cli --theme latte_money --duration 60 --format vertical --lang ro --cta comment -o output/video.mp4
```

Opțiuni utile: `--topic "subiect propriu"`, `--visual dark|light|blueprint`, `--fps 24|30`, `--energy 1-5`, `--scale 0.5` (draft rapid), `--save-script s.json`, `--script s.json`.

---

## 🧠 Ce conține

### Motor de animație procedurală (`stickman_studio/rig.py`, `figure.py`, `props.py`, `camera.py`)
- **StickmanRig**: schelet articulat (trunchi, cap, brațe și picioare cu 2 segmente), cinematică directă + **IK** pentru mâini (facepalm, cafea la gură, tastat), aterizare automată pe podea, squash & stretch, tranziții line cu **easing** (cubic, back, elastic, bounce).
- **22 de acțiuni**: `idle_breathing, walk, run_panic, explain_gestures, point_at, panic_hands_up, facepalm, type_on_laptop, celebrate_jump, think_chin, argue_wildly, fall_down_dramatic, nod_yes, shake_head_no, shock_freeze, mic_drop, sip_coffee, plot_evil` + bonus `talk, cta_point, wave, shrug`.
- **Expresii faciale**: neutral, happy, shocked, angry, sad, smug, deadpan, mind_blown (+ evil, dizzy) cu clipit automat și **lip-sync după amplitudinea audio**.
- **Efecte pe personaj**: transpirație, venă de furie, stele de amețeală, linii de șoc/viteză, bule de gândire, confetti, vignetă „evil”, flash de impact.
- **24 de recuzite vectoriale**: laptop, birou, grafic ascendent/descendent, ceas, semn de întrebare/exclamare, bec idee, ploaie de bani, monede, buton **Subscribe animat** (cursor + click + clopoțel), Like, Comment, Save/Share, cafea, perete/ușă, telefon, foc, microfon, baterie, calendar, ganteră, coș de cumpărături.
- **Camera**: `zoom_in, zoom_out, pan_left, pan_right, dramatic_camera_shake, punch_in` + Ken-Burns subtil pe cadrele statice.

### Generator de scripturi (`script_gen.py`, `content_en.py`, `content_ro.py`)
- Structură virală: **hook → setup → beat-uri → pattern interrupt la ~15–20s → climax → CTA**.
- **13 teme** în 6 categorii (Tech, Bani, Productivitate, Psihologie, Viața de zi cu zi, Curiozități) + subiect liber.
- Calibrare automată: ~2.45 cuvinte/secundă → **~147 cuvinte / 11 shot-uri la 60s**, **~440–460 cuvinte / ~33 shot-uri la 180s**. Shot-urile lungi sunt tăiate pe propoziții (jump-cut pe punchline).
- CTA integrat în poveste + animație dedicată (`cta_point` spre butonul Subscribe/Like/Comment/Save).

### Voce, sincronizare și subtitrări (`tts.py`, `audio.py`, `subtitles.py`, `pipeline.py`)
- **TTS offline** prin `pyttsx3` (Windows SAPI5; rulează într-un subproces izolat ca să nu blocheze aplicația). Dacă nu există voci (ex. Linux headless fără placă de sunet), se trece **automat** pe un **sintetizator vocal procedural** (formanți, NumPy pur), cu timpi exacți pe cuvânt.
- Durata fiecărui shot = durata exactă a vocii lui (+ un mic „beat” de reacție); viteza vocii se ajustează automat ca videoclipul să se apropie de durata țintă.
- Muzică de fundal procedurală cu **ducking** sub voce + efecte sonore sintetizate (pop, boing, thud, whoosh, sting, ding, cash...).
- **Subtitrări mari**, câte 1–3 cuvinte, cu **cuvântul activ evidențiat** și efect „pop”, poziționate în zona sigură (deasupra UI-ului TikTok/Reels, departe de butoanele din dreapta).

---

## ✅ Teste automate

```bash
python -m pytest -q tests
```

Testele verifică: scripturile de 60s și 180s (cuvinte, shot-uri, pattern interrupts, CTA pe ultimul shot) pentru toate temele și tipurile de CTA, în ambele limbi; toate acțiunile/expresiile/recuzitele (randare în ambele formate și toate temele); vocea procedurală și mixul audio; asamblarea unui **MP4 valid H.264 + AAC cu audio** (verificat cu MoviePy și ffmpeg); sincronizarea timeline-ului de 180s.

---

## 🔧 Depanare

- **Nu se aude voce reală pe Windows** → în „Voce & audio” alege `pyttsx3 / Windows SAPI5` și o voce din listă. Pentru voce în română, instalează pachetul de limbă română din *Setări Windows → Timp și limbă → Vorbire*.
- **Randare lentă** → alege rezoluția 50% pentru draft-uri sau 24 FPS. Un clip de 60s Full HD durează de obicei 1–2 minute pe un laptop obișnuit.
- **Ollama** → pornește `ollama serve` și descarcă un model (`ollama pull llama3.1`). Dacă AI-ul nu răspunde, aplicația folosește automat generatorul offline.
