import google.generativeai as genai
from typing import List
import PIL.Image  # ต้องใช้ PIL ในการจัดการรูปภาพ
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = None

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    async def generate_prompts_from_image(
        self,
        model_name: str,
        image_paths: List[str],  # เปลี่ยนจาก bytes เป็น paths เพื่อให้จัดการง่ายขึ้น
        user_input: str,
        style: str,
        ratio: str,
        count: int,
    ) -> List[str]:

        if not self.api_key:
            raise ValueError("API Key missing. Please set it in Settings tab.")

        system_instruction = f"""
        Role: You are an expert Image Prompt Generator.
        Task: Analyze the provided image(s) and user input: "{user_input}".
        Context:
        - Target Style: {style}
        - Aspect Ratio: {ratio}
        - Quantity: Generate exactly {count} distinct prompts.
        
        Output Requirements:
        - Return ONLY the raw prompts.
        - Separate each prompt with a specific delimiter "|||".
        - Do not use numbering (1., 2.) or bullet points.
        - Do not add introduction or conclusion text.
        """

        try:
            # เตรียม Contents
            contents = [system_instruction]

            # โหลดรูปภาพจาก Path
            for path in image_paths:
                try:
                    img = PIL.Image.open(path)
                    contents.append(img)
                except Exception as e:
                    print(f"Error loading image {path}: {e}")

            # เลือกโมเดล
            model = genai.GenerativeModel(model_name)

            # ส่งคำสั่ง (Async)
            response = await model.generate_content_async(contents)

            # แยกผลลัพธ์ด้วย Delimiter ที่เรากำหนด (|||)
            text_response = response.text.replace(
                "\n", " "
            )  # ลบ Newline ทิ้งก่อนเพื่อให้ prompt เป็นบรรทัดเดียว
            prompts = [p.strip() for p in text_response.split("|||") if p.strip()]

            return prompts[:count]

        except Exception as e:
            return [f"Error: {str(e)}"]
