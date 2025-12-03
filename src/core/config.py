# File: src/core/config.py

APP_TITLE = "AI Prompt Studio"
DEFAULT_THEME_MODE = "light"

# === Text Generation Models ===
AI_MODELS_MAP = {
    "Google (Gemini)": [
        {"id": "gemini-3-pro-preview", "name": "Gemini 3 Pro Preview"},
        {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
        {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
        {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite"},
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
        {"id": "gemini-2.0-flash-lite", "name": "Gemini 2.0 Flash Lite"},
    ],
    "OpenAI": [
        {"id": "gpt-4o", "name": "ยังไม่เปิดให้ใช้"},
    ],
    "Claude": [
        {"id": "claude-3-5-sonnet", "name": "ยังไม่เปิดให้ใช้"},
    ],
}

# === Image Generation Models ===
IMAGE_GEN_MODELS_MAP = {
    "Google (Imagen 3)": [
        {"id": "gemini-2.5-flash-image", "name": "Nano Banana"},
        {"id": "gemini-3-pro-image-preview", "name": "Nano Banana Pro"},
        {"id": "imagen-3.0-generate-002", "name": "Imagen 3.0"},
        {"id": "imagen-4.0-generate-001", "name": "Imagen 4.0"},
        {"id": "imagen-4.0-ultra-generate-001", "name": "Imagen 4.0 Ultra"},
        {"id": "imagen-4.0-fast-generate-001", "name": "Imagen 4.0 Fast"},
    ],
    "Pollinations": [
        {"id": "flux", "name": "Flux (Free-version)"},
        {"id": "turbo", "name": "Turbo"},
        {"id": "gptimage", "name": "GPT Image"},
    ],
}

# === Image Edit Models ===
IMAGE_EDIT_MODELS_MAP = {
    "Google (Gemini/Imagen)": [
        {"id": "gemini-2.5-flash-image", "name": "Nano Banana"},
        {"id": "gemini-3-pro-image-preview", "name": "Nano Banana Pro"},
    ]
}

# === Helper for Settings Tab (Flat list of display names) ===
SUPPORTED_MODELS = []
for category in [AI_MODELS_MAP, IMAGE_GEN_MODELS_MAP]:
    for provider, models in category.items():
        for m in models:
            SUPPORTED_MODELS.append(f"{provider}: {m['name']} ({m['id']})")
