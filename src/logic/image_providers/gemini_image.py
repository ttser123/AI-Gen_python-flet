from google import genai
from google.genai import types
import PIL.Image
import io
from .base_image import BaseImageProvider


class GeminiImageProvider(BaseImageProvider):
    def __init__(self):
        self.api_key = None
        self.client = None

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        # Init Client แบบใหม่
        self.client = genai.Client(api_key=self.api_key)

    async def generate_image(
        self, prompt: str, model: str, ref_image_paths: list = [], ratio: str = "1:1"
    ):
        if not self.client:
            return "Error: API Key is missing."

        try:
            print(f"Generating image with {model} (Multimodal)...")

            # 1. เตรียม Contents (Prompt + Images)
            contents = [prompt]

            # โหลดรูปภาพ Reference ทั้งหมดใส่เข้าไปใน List
            for path in ref_image_paths:
                try:
                    img = PIL.Image.open(path)
                    contents.append(img)
                    print(f"Added reference image: {path}")
                except Exception as e:
                    print(f"Error loading ref image {path}: {e}")

            # 2. เรียก API (generate_content)
            # ใช้ Logic ตามตัวอย่างที่คุณให้มา
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                # config=types.GenerateContentConfig(...) # ใส่ Config เพิ่มได้ถ้าต้องการ
            )

            # 3. วนลูปหา Part ที่เป็นรูปภาพ
            # ตามตัวอย่าง: part.inline_data หรือ part.as_image()
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:

                    # กรณี SDK ตัวใหม่ที่รองรับ .as_image()
                    try:
                        # ลองเช็คว่าเป็นรูปไหม
                        if hasattr(part, "inline_data") and part.inline_data:
                            print("Image detected in response.")

                            # แปลงเป็น BytesIO
                            generated_img = part.as_image()
                            # หมายเหตุ: .as_image() คืนค่าเป็น PIL.Image

                            img_byte_arr = io.BytesIO()
                            generated_img.save(img_byte_arr, format="PNG")
                            return img_byte_arr.getvalue()

                    except Exception as img_err:
                        print(f"Error extracting image part: {img_err}")

            return "Error: Model returned text only (No image generated)."

        except Exception as e:
            error_msg = str(e)
            print(f"Gemini Error: {error_msg}")

            if "404" in error_msg:
                return f"Error 404: Model '{model}' not found. (ลองใช้ gemini-2.5-flash-image หรือเช็คชื่อโมเดล)"
            elif "429" in error_msg:
                return "Error 429: Quota exceeded."
            else:
                return f"Provider Error: {error_msg}"
