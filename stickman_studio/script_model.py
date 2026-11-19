"""Data model for scripts / storyboards."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import re


@dataclass
class Shot:
    text: str
    action: str = "talk"
    expression: str = "neutral"
    props: list = field(default_factory=list)
    camera: str = "static"
    guest: bool = False
    kind: str = "beat"           # hook | setup | beat | interrupt | climax | cta

    @property
    def words(self) -> int:
        return len(self.text.split())

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Shot":
        props = d.get("props") or []
        if isinstance(props, str):
            props = [x.strip() for x in re.split(r"[,;]", props) if x.strip()]
        return Shot(text=str(d.get("text", "")).strip(), action=d.get("action") or "talk",
                    expression=d.get("expression") or "neutral", props=list(props),
                    camera=d.get("camera") or "static", guest=bool(d.get("guest", False)),
                    kind=d.get("kind") or "beat")


@dataclass
class Script:
    title: str
    topic: str
    theme_id: str
    language: str
    target_duration: float
    cta_type: str
    shots: list
    hook_text: str = ""
    cta_text: str = ""
    seed: int = 0

    @property
    def word_count(self) -> int:
        return sum(s.words for s in self.shots)

    @property
    def full_text(self) -> str:
        return " ".join(s.text for s in self.shots)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["shots"] = [s.to_dict() for s in self.shots]
        return d

    @staticmethod
    def from_dict(d: dict) -> "Script":
        return Script(title=d.get("title", "Untitled"), topic=d.get("topic", ""),
                      theme_id=d.get("theme_id", "custom"), language=d.get("language", "en"),
                      target_duration=float(d.get("target_duration", 60)),
                      cta_type=d.get("cta_type", "subscribe"),
                      shots=[Shot.from_dict(s) for s in d.get("shots", [])],
                      hook_text=d.get("hook_text", ""), cta_text=d.get("cta_text", ""),
                      seed=int(d.get("seed", 0)))
