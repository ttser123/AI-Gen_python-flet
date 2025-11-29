from abc import ABC, abstractmethod
from typing import List, Optional


class BaseImageProvider(ABC):
    @abstractmethod
    def set_api_key(self, api_key: str):
        pass

    @abstractmethod
    async def generate_image(
        self, prompt: str, model: str, ratio: str = "1:1"
    ) -> Optional[bytes]:
        """
        Input: Prompt, Model, Ratio
        Output: Image bytes
        """
        pass
