import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_profile(path_or_json=None):
    if path_or_json is None:
        return json.loads((DATA_DIR / "sample_profile.json").read_text())

    if isinstance(path_or_json, dict):
        return path_or_json

    # File path
    p = Path(path_or_json)
    if p.exists():
        return json.loads(p.read_text())

    # Raw JSON string
    return json.loads(path_or_json)
