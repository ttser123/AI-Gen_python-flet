# File: src/core/config.py

APP_TITLE = "AI Prompt Studio"
DEFAULT_THEME_MODE = "light"

# จัดกลุ่ม Model แยกตาม Provider
AI_MODELS_MAP = {
    "Google (Gemini)": [
        "gemini-3-pro-preview",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-lite-preview-09-2025",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ],
    "OpenAI (Coming Soon)": ["gpt-4o", "gpt-4-turbo"],
}

# สำหรับใช้แสดงผลใน Settings (เอามาต่อกันหมด)
SUPPORTED_MODELS = [m for models in AI_MODELS_MAP.values() for m in models]
