import json
import os

THEME_FILE = "theme.json"


def save_theme(mode: str):
    """บันทึก Theme (light/dark) ลงไฟล์"""
    try:
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({"theme_mode": mode}, f)
        return True
    except Exception as e:
        print(f"Error saving theme: {e}")
        return False


def load_theme():
    """โหลด Theme ล่าสุด (ถ้าไม่มีให้เป็น light)"""
    if not os.path.exists(THEME_FILE):
        return "light"
    try:
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("theme_mode", "light")
    except Exception:
        return "light"
