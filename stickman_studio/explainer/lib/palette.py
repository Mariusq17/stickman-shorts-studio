"""Harmonised palette (soft, saturated-but-not-neon, warm light / cool shadow)."""

INK = (28, 30, 40)
RED = (232, 64, 72)
BLUE = (48, 118, 240)
GREEN = (46, 170, 98)
YELLOW = (255, 200, 64)
ORANGE = (255, 150, 60)
PURPLE = (150, 110, 240)
WHITE = (255, 255, 255)
SKY_TOP, SKY_BOT = (196, 222, 250), (252, 244, 232)
SHADOW = (40, 46, 80)          # cool shadow tint

PEG_COLORS = [(255, 164, 56), (70, 160, 255), (110, 205, 125), (244, 104, 140), (165, 128, 255)]


def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def warm(c, k=0.08):
    """Lit surfaces lean warm."""
    return mix(c, (255, 236, 200), k)


def cool(c, k=0.18):
    """Shaded surfaces lean cool."""
    return mix(c, (70, 80, 130), k)
