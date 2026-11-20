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
   - Prima dată creează automat un mediu virtual (`venv`), instalează `requirements.txt` și **descarcă o singură dată vocile naturale Piper** (engleză + română, ~60–120 MB fiecare) în `models/piper`.
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
| Voce & audio | motor voce (Piper / SAPI5 / eSpeak-NG / procedural) cu starea fiecăruia, alegerea vocii, buton „Descarcă vocea Piper”, stil muzică (Lo-fi / Chill-pop / Upbeat / fișierul tău mp3-wav / fără), volum, SFX, potrivire automată a duratei |
| Avansat | subtitrări, bară de progres, rezoluție (100% / 75% / 50% draft), calitate CRF, linii netede (antialiasing 2x) |
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

### Voce, sincronizare și subtitrări (`tts.py`, `voices.py`, `audio.py`, `subtitles.py`, `pipeline.py`)
- **Lanț automat de motoare TTS, toate offline:**
  1. **Piper** — voce neurală naturală (EN: Ryan / Lessac, RO: Mihai). Modelul se descarcă **o singură dată**, apoi rulează local, fără internet.
  2. **Windows SAPI5** (prin `pyttsx3`, într-un subproces izolat) — vocile instalate în Windows.
  3. **eSpeak-NG** — robotic, dar clar; suportă și româna.
  4. **Voce procedurală** — doar ca ultimă soluție (sunete, nu cuvinte); aplicația te avertizează dacă ajunge să o folosească.
- Inteligibilitatea vocii este verificată automat în teste cu un recunoscător vocal offline (pocketsphinx): Piper este transcris corect în proporție de peste 80%, chiar și cu muzica pe fundal.
- Durata fiecărui shot = durata exactă a vocii lui (+ un mic „beat” de reacție); viteza vocii se ajustează automat ca videoclipul să se apropie de durata țintă (maxim 180s).
- **Muzică de fundal** generată din cod, care se repetă fără întrerupere: acorduri reale (vi–IV–I–V), pian electric, pad, bas, tobe discrete și reverb, în 3 stiluri, cu **ducking** sub voce. Poți folosi și **propria muzică** (mp3/wav/ogg).
- Efecte sonore discrete (max. unul pe shot) și normalizarea volumului vocii.
- **Subtitrări mari**, câte 1–3 cuvinte, cu **cuvântul activ evidențiat** și efect „pop”, poziționate în zona sigură; camera nu împinge niciodată personajul peste subtitrări.

### Scenă
- Decor de cameră pentru fiecare temă vizuală (fereastră cu cer/lună, tablou, raft cu cărți, plantă, podea cu perspectivă), layout dedicat pentru 9:16 și 16:9, antialiasing 2x, contur fin în jurul personajului, tranziții line între poziții.

---

## ✅ Teste automate

```bash
python -m pytest -q tests
```

Testele verifică: scripturile de 60s și 180s (cuvinte, shot-uri, pattern interrupts, CTA pe ultimul shot) pentru toate temele și tipurile de CTA, în ambele limbi; toate acțiunile/expresiile/recuzitele (randare în ambele formate și toate temele); vocea procedurală și mixul audio; asamblarea unui **MP4 valid H.264 + AAC cu audio** (verificat cu MoviePy și ffmpeg); sincronizarea timeline-ului de 180s.

---

## 🔧 Depanare

- **Vocea sună ca niște sunete, nu ca vorbire** → s-a folosit vocea procedurală pentru că modelul Piper nu e descărcat. În „Voce & audio” apasă **„⬇️ Descarcă vocea Piper”** (o singură dată, e nevoie de internet doar atunci) sau rulează:
  ```bash
  python -m stickman_studio.voices --download en ro
  ```
  Poți pune manual orice model Piper (`.onnx` + `.onnx.json`) în `models/piper/`.
- **Randare lentă** → debifează „Linii netede (antialiasing 2x)”, alege rezoluția 50% pentru draft-uri sau 24 FPS. Cu antialiasing, un clip de 60s Full HD durează aproximativ 2 minute.
- **Ollama** → pornește `ollama serve` și descarcă un model (`ollama pull llama3.1`). Dacă AI-ul nu răspunde, aplicația folosește automat generatorul offline.
