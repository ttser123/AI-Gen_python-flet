import httpx
import random
import urllib.parse
from .base_image import BaseImageProvider


class PollinationsProvider(BaseImageProvider):
    def set_api_key(self, api_key: str):
        pass  # ไม่ต้องใช้ Key

    # --- แก้ไขบรรทัดนี้: เพิ่ม ref_image_paths เข้าไปรับค่า ---
    async def generate_image(
        self, prompt: str, model: str, ref_image_paths: list = [], ratio: str = "1:1"
    ):

        # 1. จัดการขนาดภาพ
        width, height = 1024, 1024
        if ratio == "16:9":
            width, height = 1280, 720
        elif ratio == "9:16":
            width, height = 720, 1280

        # 2. สุ่ม Seed
        seed = random.randint(0, 999999)

        # 3. URL Encode
        safe_prompt = urllib.parse.quote(prompt)

        # 4. สร้าง URL (ใช้แบบใหม่ตาม Cheatsheet)
        url = (
            f"https://image.pollinations.ai/prompt/{safe_prompt}"
            f"?width={width}"
            f"&height={height}"
            f"&seed={seed}"
            f"&model={model}"
            f"&nologo=true"
        )

        print(f"Requesting Pollinations: {url}")

        # 5. ยิง Request
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url, timeout=60.0)

                if response.status_code == 200:
                    return response.content
                else:
                    return f"Error {response.status_code}: {response.text}"
            except Exception as e:
                print(f"Pollinations Error: {e}")
                return f"Connection Error: {str(e)}"
