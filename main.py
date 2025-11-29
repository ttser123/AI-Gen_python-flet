import flet as ft
from src.ui.main_layout import get_main_layout
from src.core.config import APP_TITLE
from src.core.theme_manager import load_theme  # Import


def main(page: ft.Page):
    # 1. ตั้งค่าหน้าต่างโปรแกรม
    page.title = APP_TITLE

    # --- โหลด Theme จากไฟล์ ---
    saved_theme = load_theme()
    page.theme_mode = saved_theme
    # -----------------------

    page.window_width = 1000
    page.window_height = 800
    page.padding = 20

    # 2. โหลด Layout หลัก
    app_layout = get_main_layout(page)

    # 3. เพิ่มลงหน้าจอ
    page.add(app_layout)


if __name__ == "__main__":
    ft.app(target=main)
