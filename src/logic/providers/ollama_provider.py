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

        # 2. ฟังก์ชันย่อย: สร้าง 1 Prompt (เราจะเรียกใช้ฟังก์ชันนี้วนลูป)
        async def generate_single_prompt(index):
            # Prompt ที่กำชับให้ตอบแค่เนื้อหา
            full_prompt = (
                f"You are an expert creative writer. "
                f"Analyze the image and user request: '{user_input}'. "
                f"Style: {style}. Aspect Ratio: {ratio}. "
                f"Write ONE highly detailed, descriptive image generation prompt (Variation {index+1}). "
                f"CRITICAL RULES: Do not use conversational filler (e.g., 'Here is a prompt', 'Sure'). "
                f"Do not number the output. Return ONLY the prompt text."
            )

            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "images": images_b64 if images_b64 else None,
                "options": {
                    "temperature": 0.8,  # เพิ่มความหลากหลายในแต่ละรอบ
                    "num_predict": 512,
                },
            }

            url = f"{self.base_url}/api/generate"

            # ใช้ Timeout นานหน่อยเผื่อเครื่องช้า
            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        text = result.get("response", "").strip()

                        # --- Cleaning Logic (ทำความสะอาดข้อความ) ---
                        # ลบเครื่องหมายคำพูดหัวท้าย
                        if text.startswith(('"', "'")):
                            text = text[1:-1]
                        # ลบคำนำหน้าเช่น "Here is a prompt:"
                        if ":" in text and len(text.split(":")[0]) < 20:
                            text = text.split(":", 1)[-1].strip()
                        # ลบ Markdown Bold (**...**)
                        text = text.replace("**", "")

                        return text
                    else:
                        return f"Error {response.status_code}"
                except Exception as e:
                    return f"Error: {str(e)}"

        # 3. วนลูปสร้างตามจำนวน Count (Parallel Requests)
        print(f"Ollama generating {count} prompts (Parallel Loop)...")

        # สร้าง Task ตามจำนวนที่ขอ (เช่น 5 tasks)
        tasks = [generate_single_prompt(i) for i in range(count)]

        # รันทุก Task พร้อมกัน (หรือเกือบพร้อมกัน)
        results = await asyncio.gather(*tasks)

        # กรองผลลัพธ์ที่ Error หรือว่างเปล่าทิ้ง
        final_prompts = [r for r in results if r and "Error" not in r]

        return final_prompts if final_prompts else ["No prompts generated."]
