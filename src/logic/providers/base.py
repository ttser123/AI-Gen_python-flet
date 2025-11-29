# File: src/logic/providers/base.py
from abc import ABC, abstractmethod
from typing import List, Optional


class LLMProvider(ABC):
    """
    Abstract Base Class ที่ทุก Provider (Gemini, OpenAI) ต้องทำตาม
    """

    @abstractmethod
    def set_api_key(self, api_key: str):
        """ตั้งค่า API Key"""
        pass

    @abstractmethod
    async def generate_prompts_from_image(
        self,
        model_name: str,
        images: List[bytes],
        user_input: str,
        style: str,
        ratio: str,
        count: int,
    ) -> List[str]:
        """
        ฟังก์ชันหลัก: รับรูป+ข้อความ -> ส่งคืนรายการ Prompt
        """
        pass
