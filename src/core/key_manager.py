import json
import os

# ชื่อไฟล์ที่จะเก็บไว้หน้าบ้าน (Root Folder)
KEY_FILE = "api_key.json"


def save_api_key(api_key: str):
    """บันทึก API Key ลงไฟล์ JSON"""
    data = {"gemini_api_key": api_key}
    try:
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Error saving key: {e}")
        return False


def get_api_key():
    """อ่าน API Key จากไฟล์ JSON"""
    if not os.path.exists(KEY_FILE):
        return None
    try:
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("gemini_api_key")
    except Exception as e:
        print(f"Error reading key: {e}")
        return None
