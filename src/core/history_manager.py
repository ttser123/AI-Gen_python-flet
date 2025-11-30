import json
import os
import time
import shutil
from datetime import datetime

HISTORY_FILE = "history.json"
HISTORY_IMG_DIR = "history_images"


def ensure_history_dir():
    if not os.path.exists(HISTORY_IMG_DIR):
        os.makedirs(HISTORY_IMG_DIR)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return []


# --- ฟังก์ชันที่ขาดหายไป (เพิ่มกลับมาแล้ว) ---
def get_latest_history_id():
    """ดึง ID ของประวัติรายการล่าสุด"""
    history = load_history()
    if history:
        return history[0]["id"]
    return None


# ----------------------------------------


def save_to_history(provider, model, input_text, image_paths, prompts):
    current_history = load_history()
    entry_id = int(time.time())
    new_entry = {
        "id": entry_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "provider": provider,
        "model": model,
        "image_model": None,  # รองรับการเก็บชื่อ Image Model
        "input_text": input_text,
        "image_paths": image_paths,
        "prompts": prompts,
        "generated_images": [],
    }
    current_history.insert(0, new_entry)
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(current_history, f, indent=4, ensure_ascii=False)
        return entry_id
    except Exception as e:
        print(f"Error saving history: {e}")
        return None


def update_history_images(entry_id, prompt_index, image_bytes, image_model=None):
    """บันทึกรูปภาพลง Disk และอัปเดตข้อมูล"""
    ensure_history_dir()
    current_history = load_history()

    target = next((item for item in current_history if item["id"] == entry_id), None)
    if not target:
        return

    filename = f"{entry_id}_{prompt_index}.png"
    file_path = os.path.join(HISTORY_IMG_DIR, filename)

    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        if "generated_images" not in target:
            target["generated_images"] = []

        existing_img = next(
            (img for img in target["generated_images"] if img["index"] == prompt_index),
            None,
        )
        if not existing_img:
            target["generated_images"].append(
                {"index": prompt_index, "path": file_path}
            )

        # อัปเดตชื่อโมเดลรูปภาพถ้ามีส่งมา
        if image_model:
            target["image_model"] = image_model

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(current_history, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Error updating image history: {e}")


def delete_history_item(timestamp_id):
    current_history = load_history()
    target = next(
        (item for item in current_history if item["id"] == timestamp_id), None
    )

    if target and "generated_images" in target:
        for img in target["generated_images"]:
            if os.path.exists(img["path"]):
                try:
                    os.remove(img["path"])
                except:
                    pass

    new_history = [item for item in current_history if item["id"] != timestamp_id]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(new_history, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False


def clear_all_history():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        if os.path.exists(HISTORY_IMG_DIR):
            shutil.rmtree(HISTORY_IMG_DIR)
        return True
    except:
        return False
