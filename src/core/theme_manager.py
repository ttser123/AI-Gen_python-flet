import json
import os
import flet as ft
from src.core.app_themes import THEME_PRESETS

THEME_FILE = "theme.json"


def save_theme(theme_key: str):
    """บันทึก Key ของ Theme (เช่น 'ocean_blue')"""
    try:
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({"theme_key": theme_key}, f)
        return True
    except Exception as e:
        print(f"Error saving theme: {e}")
        return False


def load_theme_key():
    """โหลด Key ล่าสุด ถ้าไม่มีให้ใช้ 'system_light'"""
    if not os.path.exists(THEME_FILE):
        return "system_light"
    try:
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("theme_key", "system_light")
    except Exception:
        return "system_light"


def apply_theme(page: ft.Page, theme_key: str):
    """ฟังก์ชันหลักสำหรับเปลี่ยน Theme ของ Page"""
    # 1. ดึง Config จาก Preset
    preset = THEME_PRESETS.get(theme_key)

    # กันเหนียวเผื่อหา Key ไม่เจอ
    if not preset:
        preset = THEME_PRESETS["system_light"]
        theme_key = "system_light"

    # 2. ตั้งค่า Mode (Light/Dark)
    page.theme_mode = preset["mode"]

    # 3. ตั้งค่า Seed Color (ชุดสี)
    if preset["seed"]:
        # สร้าง Theme ใหม่จากสี Seed
        page.theme = ft.Theme(color_scheme_seed=preset["seed"])
        page.dark_theme = ft.Theme(color_scheme_seed=preset["seed"])
    else:
        # ใช้ Default ของ Flet
        page.theme = None
        page.dark_theme = None

    # 4. สั่ง Update
    page.update()
    return preset["label"]
