import json
import os

OLLAMA_SETTINGS_FILE = "ollama_settings.json"

DEFAULT_SETTINGS = {
    "base_url": "http://localhost:11434",
    "selected_models": [],  # ใช้ชื่อนี้ให้ตรงกับ SettingsTab
}


def load_ollama_settings():
    """โหลดค่า Setting"""
    if not os.path.exists(OLLAMA_SETTINGS_FILE):
        return DEFAULT_SETTINGS
    try:
        with open(OLLAMA_SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge กับ Default เผื่อ key หาย
            return {**DEFAULT_SETTINGS, **data}
    except:
        return DEFAULT_SETTINGS


# ปรับแก้ให้รับ arguments 2 ตัว ตามที่ SettingsTab เรียกใช้
def save_ollama_settings(base_url, selected_models):
    """บันทึกค่าลงไฟล์ JSON"""
    data = {"base_url": base_url, "selected_models": selected_models}
    try:
        with open(OLLAMA_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving ollama settings: {e}")
        return False
