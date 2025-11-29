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
    # ใช้ CreateTab ของจริงแล้ว
    create_tab = CreateTab(page)
    gallery_tab = GalleryTab(page)
    settings_tab = SettingsTab(page)
    display_tab = DisplayTab(page)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Create", icon=ft.Icons.AUTO_AWESOME, content=create_tab),
            ft.Tab(text="Gallery", icon=ft.Icons.HISTORY, content=gallery_tab),
            ft.Tab(text="Settings", icon=ft.Icons.SETTINGS, content=settings_tab),
            ft.Tab(text="Display", icon=ft.Icons.MONITOR, content=display_tab),
        ],
        expand=1,
    )

    return tabs
