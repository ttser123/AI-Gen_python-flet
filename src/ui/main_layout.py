import flet as ft
from src.ui.tabs.settings_tab import SettingsTab
from src.ui.tabs.create_tab import CreateTab
from src.ui.tabs.gallery_tab import GalleryTab
from src.ui.tabs.display_tab import DisplayTab


class PlaceholderTab(ft.Container):
    def __init__(self, text, icon):
        super().__init__()
        self.content = ft.Column(
            [
                ft.Icon(icon, size=64, color=ft.Colors.GREY),
                ft.Text(text, size=24, color=ft.Colors.GREY),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.alignment = ft.alignment.center
        self.expand = True


def get_main_layout(page: ft.Page):
    create_tab = CreateTab(page)
    gallery_tab = GalleryTab(page)
    settings_tab = SettingsTab(page)
    display_tab = DisplayTab(page)

    # ฟังก์ชันดักจับ event เมื่อมีการเปลี่ยน Tab
    def on_tab_change(e):
        # ถ้า Tab ที่เลือกคือ index 0 (Create Tab)
        if e.control.selected_index == 0:
            print("Switched to Create Tab: Refreshing models...")
            # เรียกฟังก์ชันอัปเดตใน CreateTab (ต้องไปสร้างไว้ใน class CreateTab ด้วยนะ)
            if hasattr(create_tab, "update_models"):
                create_tab.update_models()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        on_change=on_tab_change,  # <--- ใส่บรรทัดนี้เพิ่มเข้าไป
        tabs=[
            ft.Tab(text="Create", icon=ft.Icons.AUTO_AWESOME, content=create_tab),
            ft.Tab(text="Gallery", icon=ft.Icons.HISTORY, content=gallery_tab),
            ft.Tab(text="Settings", icon=ft.Icons.SETTINGS, content=settings_tab),
            ft.Tab(text="Display", icon=ft.Icons.MONITOR, content=display_tab),
        ],
        expand=1,
    )

    return tabs
