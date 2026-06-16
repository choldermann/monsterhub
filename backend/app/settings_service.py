import json
from pathlib import Path

SETTINGS_PATH = Path("/app/data/settings.json")

_defaults = {
    "monstersuite_url": "https://monstersuite.de",
    "license_keys": {},
}


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return _defaults.copy()
    try:
        with open(SETTINGS_PATH) as f:
            data = json.load(f)
        return {**_defaults, **data}
    except Exception:
        return _defaults.copy()


def save_settings(settings: dict):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)
