from typing import Any, Dict

THEMES: Dict[str, Dict[str, Any]] = {
    "dark": {
        "appearance_mode": "dark",
        "color_theme": "blue",
        "bg_primary": "#141a26",
        "bg_secondary": "#1c2433",
        "bg_tertiary": "#243349",
        "accent": "#4f8cff",
        "text_primary": "#e8edf7",
        "text_secondary": "#9eabc0",
        "danger": "#d36b6b",
    },
    "light": {
        "appearance_mode": "light",
        "color_theme": "blue",
        "bg_primary": "#eef2f7",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#dde5f0",
        "accent": "#2b6df6",
        "text_primary": "#162033",
        "text_secondary": "#637188",
        "danger": "#bf4f4f",
    },
}


def get_theme(name: str) -> Dict[str, Any]:
    return THEMES.get(name, THEMES["dark"])
