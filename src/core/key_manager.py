import json
import os

KEY_FILE = "api_key.json"


def save_api_keys(text_key: str, image_key: str):
    """บันทึก API Key แยกกันระหว่าง Text และ Image"""
    data = {"gemini_text_key": text_key, "gemini_image_key": image_key}
    try:
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Error saving keys: {e}")
        return False


def get_api_keys():
    """อ่าน API Keys ทั้งหมด (คืนค่าเป็น Dict)"""
    if not os.path.exists(KEY_FILE):
        return {}
    try:
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            # --- Migration Logic ---
            # ถ้าเป็นไฟล์เวอร์ชันเก่าที่มีแค่ 'gemini_api_key'
            # ให้ถือว่าใช้ Key เดียวกันทั้งคู่ไปก่อน
            if "gemini_api_key" in data and "gemini_text_key" not in data:
                old_key = data["gemini_api_key"]
                return {"gemini_text_key": old_key, "gemini_image_key": old_key}

            return data
    except Exception as e:
        print(f"Error reading keys: {e}")
        return {}
