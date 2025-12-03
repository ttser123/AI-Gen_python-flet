import io
import requests
from rembg import remove
from PIL import Image


# 1. ฟังก์ชันลบพื้นหลัง (Local - ฟรี)
def remove_background(image_bytes: bytes) -> bytes:
    try:
        # input ต้องเป็น bytes -> output เป็น bytes (PNG)
        result = remove(image_bytes)
        return result
    except Exception as e:
        print(f"Error removing background: {e}")
        return None


HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def generate_background_hf(prompt: str) -> bytes:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, low quality, ugly, watermark, text",
            "num_inference_steps": 25,
            "width": 1024,
            "height": 1024,
        },
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.content
        else:
            print(f"HF Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error generating image: {e}")
        return None


# 3. ฟังก์ชันซ้อนภาพ (Composite) - เอาสินค้าวางบนพื้นหลัง
def composite_images(product_bytes: bytes, bg_bytes: bytes, scale=0.8) -> bytes:
    try:
        # แปลง bytes เป็น PIL Image
        product = Image.open(io.BytesIO(product_bytes)).convert("RGBA")
        background = Image.open(io.BytesIO(bg_bytes)).convert("RGBA")

        # ปรับขนาดสินค้า
        target_w = int(background.width * scale)
        aspect_ratio = product.height / product.width
        target_h = int(target_w * aspect_ratio)
        product = product.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # จัดวางตรงกลาง (หรือปรับตำแหน่งตาม logic ที่เราเคยคุยกัน)
        bg_w, bg_h = background.size
        offset = ((bg_w - target_w) // 2, (bg_h - target_h) // 2)

        # แปะภาพ (Paste)
        final_image = background.copy()
        final_image.paste(product, offset, product)  # ใช้ product เป็น mask ในตัว

        # แปลงกลับเป็น bytes
        output = io.BytesIO()
        final_image.save(output, format="PNG")
        return output.getvalue()

    except Exception as e:
        print(f"Error compositing: {e}")
        return None
