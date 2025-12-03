import httpx
import base64
import json
import asyncio


class OllamaProvider:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

    async def generate_prompts_from_image(
        self, model, image_paths, user_input, style, ratio, count
    ):
        # 1. เตรียมรูปภาพ (Encode Base64)
        images_b64 = []
        for path in image_paths:
            img_str = self.encode_image(path)
            if img_str:
                images_b64.append(img_str)

        # 2. ฟังก์ชันย่อย: สร้าง 1 Prompt
        async def generate_single_prompt(index):
            # สั่งให้ AI โฟกัสแค่ "เนื้อหา" ไม่ต้องสน Format มาก เดี๋ยวเราจัดเอง
            full_prompt = (
                f"Act as a professional prompt engineer. "
                f"Analyze the input and write a CONCISE visual description for image generation. "
                f"User Request: '{user_input}'. "
                f"Variation: {index + 1}. "
                f"REQUIREMENTS: "
                f"- Describe ONLY the key visual elements (subject, lighting, mood). "
                f"- Keep it under 40 words. "  # <-- จำกัดจำนวนคำ
                f"- Be direct and specific. No flowery language. "
                f"- Do NOT mention aspect ratio or style keywords (I will add them). "
                f"- Start directly with the description."
            )

            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "images": images_b64 if images_b64 else None,
                "options": {
                    "temperature": 0.9,
                    "num_predict": 100,  # <-- ลด Max Tokens ลงเพื่อให้ตอบสั้นลง (เดิม 512)
                },
            }

            url = f"{self.base_url}/api/generate"

            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        text = result.get("response", "").strip()

                        # --- Cleaning Logic ---
                        # ลบเครื่องหมายคำพูด
                        if text.startswith(('"', "'")):
                            text = text[1:-1]
                        # ลบคำนำหน้าขยะ
                        if ":" in text and len(text.split(":")[0]) < 20:
                            text = text.split(":", 1)[-1].strip()
                        # ลบ Markdown Bold
                        text = text.replace("**", "").replace("*", "")

                        # ลบจุด fullstop ท้ายประโยค (เพื่อความสวยงามตอนต่อ string)
                        if text.endswith("."):
                            text = text[:-1]

                        # --- FORMATTING (หัวใจสำคัญ) ---
                        # จัดรูปแบบมาตรฐาน: Style + เนื้อหา + Aspect Ratio
                        # ตัวอย่าง: "Cinematic, [Detailed Description], 16:9 aspect ratio"
                        final_prompt = f"{style}, {text}, {ratio} aspect ratio"

                        return final_prompt
                    else:
                        return f"Error {response.status_code}"
                except Exception as e:
                    return f"Error: {str(e)}"

        # 3. วนลูปสร้างตามจำนวน Count (Parallel Requests)
        print(f"Ollama generating {count} prompts (Parallel Loop)...")

        tasks = [generate_single_prompt(i) for i in range(count)]
        results = await asyncio.gather(*tasks)

        # กรองผลลัพธ์ที่ Error หรือว่างเปล่าทิ้ง
        final_prompts = [r for r in results if r and "Error" not in r]

        return final_prompts if final_prompts else ["No prompts generated."]
