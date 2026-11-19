"""Global configuration: video formats, visual themes and render settings."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

FORMATS = {
    "vertical": (1080, 1920),
    "horizontal": (1920, 1080),
}
FORMAT_LABELS = {
    "vertical": "9:16 Vertical (1080x1920) – Shorts / Reels / TikTok",
    "horizontal": "16:9 Horizontal (1920x1080) – YouTube",
}

MIN_DURATION = 15
MAX_DURATION = 180
WORDS_PER_SECOND = 2.45  # ~147 words / 60 s, ~440 words / 180 s


@dataclass(frozen=True)
class Theme:
    key: str
    label: str
    bg: tuple
    bg2: tuple
    ink: tuple
    accent: tuple        # warm highlight (yellow/orange)
    accent2: tuple       # secondary (blue/cyan)
    good: tuple
    bad: tuple
    floor: tuple
    grid: tuple | None
    face: tuple          # head fill
    prop_fill: tuple
    sub_fill: tuple
    sub_stroke: tuple
    sub_highlight: tuple
    guest_ink: tuple


THEMES = {
    "light": Theme(
        key="light", label="Light clasic",
        bg=(250, 248, 242), bg2=(236, 232, 222), ink=(22, 22, 28),
        accent=(255, 196, 0), accent2=(40, 120, 255), good=(30, 180, 90),
        bad=(230, 50, 60), floor=(60, 60, 70), grid=None,
        face=(255, 255, 255), prop_fill=(255, 255, 255),
        sub_fill=(255, 255, 255), sub_stroke=(10, 10, 14),
        sub_highlight=(255, 214, 0), guest_ink=(200, 40, 70),
    ),
    "dark": Theme(
        key="dark", label="Dark Mode",
        bg=(18, 19, 26), bg2=(32, 34, 46), ink=(240, 240, 245),
        accent=(255, 200, 40), accent2=(80, 170, 255), good=(60, 220, 120),
        bad=(255, 80, 90), floor=(150, 150, 170), grid=None,
        face=(18, 19, 26), prop_fill=(44, 47, 62),
        sub_fill=(255, 255, 255), sub_stroke=(0, 0, 0),
        sub_highlight=(255, 214, 0), guest_ink=(255, 110, 150),
    ),
    "blueprint": Theme(
        key="blueprint", label="Blueprint",
        bg=(18, 66, 140), bg2=(14, 52, 116), ink=(235, 245, 255),
        accent=(255, 220, 70), accent2=(140, 220, 255), good=(120, 255, 170),
        bad=(255, 110, 110), floor=(200, 225, 255), grid=(60, 110, 185),
        face=(18, 66, 140), prop_fill=(30, 85, 165),
        sub_fill=(255, 255, 255), sub_stroke=(6, 28, 70),
        sub_highlight=(255, 220, 70), guest_ink=(255, 190, 120),
    ),
}

CTA_TYPES = {
    "subscribe": "Subscribe / Follow",
    "comment": "Comment bait (dezbatere)",
    "save_share": "Save / Share",
    "custom": "Text CTA personalizat",
}


@dataclass
class RenderSettings:
    format: str = "vertical"
    fps: int = 30
    theme: str = "light"
    scale: float = 1.0            # resolution multiplier (<1 for fast previews/tests)
    language: str = "en"
    voice_rate: float = 1.0       # 0.6 .. 1.6
    voice_id: str | None = None
    tts_engine: str = "auto"      # auto | pyttsx3 | procedural
    voice_pitch: float = 1.0      # procedural voice pitch multiplier
    target_duration: float = 60.0
    fit_to_target: bool = True
    energy: int = 3               # 1..5 (energy / humor level)
    music: bool = True
    music_volume: float = 0.12
    sfx: bool = True
    subtitles: bool = True
    progress_bar: bool = True
    crf: int = 21
    preset: str = "veryfast"
    extra: dict = field(default_factory=dict)

    @property
    def size(self) -> tuple[int, int]:
        w, h = FORMATS.get(self.format, FORMATS["vertical"])
        w = int(round(w * self.scale / 2)) * 2
        h = int(round(h * self.scale / 2)) * 2
        return max(w, 64), max(h, 64)

    @property
    def theme_obj(self) -> Theme:
        return THEMES.get(self.theme, THEMES["light"])

    def to_dict(self) -> dict:
        return asdict(self)
