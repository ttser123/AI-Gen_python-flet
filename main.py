import flet as ft
from src.ui.main_layout import get_main_layout
from src.core.config import APP_TITLE
from src.core.theme_manager import load_theme_key, apply_theme  # Import ตัวใหม่


def main(page: ft.Page):
    page.title = APP_TITLE
    page.window_width = 1000
    page.window_height = 800
    page.padding = 20

    # --- โหลดและ Apply Theme ตั้งแต่เริ่ม ---
    saved_key = load_theme_key()
    apply_theme(page, saved_key)
    # ------------------------------------

    app_layout = get_main_layout(page)
    page.add(app_layout)


if __name__ == "__main__":
    ft.app(target=main)
