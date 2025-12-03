import json
import os

TEMPLATE_FILE = "ad_templates.json"

DEFAULT_TEMPLATES = {
    "Minimalist Podium": "placed on a white cylindrical podium, soft studio lighting, minimalist style, high key photography",
    "Nature Stone": "placed on a dark textured rock, moss and small plants around, cinematic lighting, forest bokeh background",
    "Luxury Marble": "standing on a black marble surface with gold veins, dramatic rim lighting, dark luxury atmosphere",
    "Sunlight Window": "on a wooden table, warm sunlight casting shadows through a window blind, cozy home atmosphere",
}


def load_templates():
    if not os.path.exists(TEMPLATE_FILE):
        save_templates(DEFAULT_TEMPLATES)
        return DEFAULT_TEMPLATES
    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_TEMPLATES


def save_templates(templates):
    try:
        with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
            json.dump(templates, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving templates: {e}")
        return False
