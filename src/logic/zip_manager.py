import zipfile
import os


def ensure_zip_extension(path: str) -> str:
    """Ensure output file always ends with .zip"""
    if not path.lower().endswith(".zip"):
        return path + ".zip"
    return path


def create_images_zip(path, prompt_boxes):
    """สร้าง ZIP เฉพาะรูปภาพที่ Gen ได้จากหน้า Create"""
    path = ensure_zip_extension(path)
    images_found = 0
    try:
        with zipfile.ZipFile(path, "w") as zipf:
            for i, box in enumerate(prompt_boxes):
                if box.current_image_bytes:
                    filename = f"image_{i+1}.png"
                    zipf.writestr(filename, box.current_image_bytes)
                    images_found += 1

        if images_found == 0:
            return False, "ไม่พบรูปภาพให้บันทึก"

        return True, f"บันทึก {images_found} รูปภาพลง ZIP เรียบร้อย"
    except Exception as err:
        return False, f"ZIP Error: {err}"


def create_project_zip(path, prompt_boxes, input_files):
    """สร้าง ZIP ทั้งโปรเจกต์จากหน้า Create (Input + Output)"""
    path = ensure_zip_extension(path)
    try:
        with zipfile.ZipFile(path, "w") as zipf:
            # 1. Save Input Images
            for i, file_path in enumerate(input_files):
                if os.path.exists(file_path):
                    ext = os.path.splitext(file_path)[1]
                    zipf.write(file_path, arcname=f"input_reference/ref_{i+1}{ext}")

            # 2. Save Prompts & Generated Images
            for i, box in enumerate(prompt_boxes):
                # Save Prompt Text
                zipf.writestr(f"outputs/prompt_{i+1}.txt", box.prompt_text)

                # Save Generated Image
                if box.current_image_bytes:
                    zipf.writestr(f"outputs/image_{i+1}.png", box.current_image_bytes)

        return True, "บันทึก Full Project เรียบร้อย"
    except Exception as err:
        return False, f"Project ZIP Error: {err}"


def create_zip_from_history_item(zip_path, item):
    """สร้าง ZIP จากข้อมูลใน History (หน้า Gallery)"""
    zip_path = ensure_zip_extension(zip_path)  # ใช้ Helper ตัวเดียวกัน
    try:
        with zipfile.ZipFile(zip_path, "w") as zipf:
            # 1. Input Images
            if "image_paths" in item:
                for i, path in enumerate(item["image_paths"]):
                    if os.path.exists(path):
                        ext = os.path.splitext(path)[1]
                        zipf.write(path, arcname=f"input_reference/ref_{i+1}{ext}")

            # 2. Prompts & Generated Images
            # สร้าง Map ของรูปภาพตาม Index เพื่อจับคู่กับ Prompt
            img_map = {}
            if "generated_images" in item:
                for img in item["generated_images"]:
                    img_map[img["index"]] = img["path"]

            for i, prompt in enumerate(item["prompts"]):
                idx = i + 1
                # Save Text
                zipf.writestr(f"outputs/prompt_{idx}.txt", prompt)

                # Save Image (ถ้ามีใน History)
                if idx in img_map and os.path.exists(img_map[idx]):
                    zipf.write(img_map[idx], arcname=f"outputs/image_{idx}.png")

        return True, "Export Project สำเร็จ"
    except Exception as e:
        return False, f"Export Error: {e}"
