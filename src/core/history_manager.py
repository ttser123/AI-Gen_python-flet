import json
import os
import time
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history():
    """โหลดประวัติทั้งหมดจากไฟล์"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return []


def save_to_history(provider, model, input_text, image_paths, prompts):
    """บันทึก Batch ใหม่ลงไฟล์"""
    current_history = load_history()

    new_entry = {
        "id": int(time.time()),  # ใช้ Timestamp เป็น ID
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "provider": provider,
        "model": model,
        "input_text": input_text,
        "prompts": prompts,
    }

    # แทรกข้อมูลใหม่ไว้บนสุด (Index 0)
    current_history.insert(0, new_entry)

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(current_history, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False


def delete_history_item(timestamp_id):
    """ลบรายการตาม ID"""
    current_history = load_history()
    # คัดกรองเอาเฉพาะตัวที่ไม่ใช่ ID ที่จะลบ
    new_history = [item for item in current_history if item["id"] != timestamp_id]

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(new_history, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def clear_all_history():
    """ลบทั้งหมด"""
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        return True
    except Exception:
        return False
