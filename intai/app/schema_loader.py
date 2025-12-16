import json
import os

def load_output_schema() -> dict:
    """
    Loads the static output JSON schema from server-side file.
    """
    base_dir = os.path.dirname(__file__)
    schema_path = os.path.join(base_dir, "schemas", "output_schema.json")

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Output schema not found at {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)
