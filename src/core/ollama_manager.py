import json
import os

CONFIG_FILE = "ollama_config.json"


def load_ollama_settings():
    if not os.path.exists(CONFIG_FILE):
        return {"base_url": "http://localhost:11434", "selected_models": []}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {"base_url": "http://localhost:11434", "selected_models": []}


def save_ollama_settings(base_url, selected_models=None):
    # ถ้าไม่ได้ส่ง list มา ให้ไปอ่านของเก่ามาใช้ (กันพลาด)
    if selected_models is None:
        current = load_ollama_settings()
        selected_models = current.get("selected_models", [])

    config = {"base_url": base_url, "selected_models": selected_models}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
