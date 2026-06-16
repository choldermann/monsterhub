import json
from pathlib import Path

REGISTRY_PATH = Path("/app/registry.json")


def load_registry() -> dict:
    with open(REGISTRY_PATH) as f:
        return json.load(f)
