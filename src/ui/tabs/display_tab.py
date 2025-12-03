import flet as ft
from src.core.theme_manager import save_theme, apply_theme, load_theme_key
from src.core.app_themes import THEME_PRESETS
from src.ui.components.toast import CustomToast
from src.core.styles import AppStyle


class DisplayTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.toast = CustomToast(page)

        # เตรียม Options สำหรับ Dropdown
        theme_options = [
            ft.dropdown.Option(key=k, text=v["label"]) for k, v in THEME_PRESETS.items()
        ]

        # หาค่าปัจจุบัน
        current_key = load_theme_key()

        self.theme_dropdown = ft.Dropdown(
            label="Select Application Theme",
            options=theme_options,
            value=current_key,
            on_change=self.on_theme_change,
            width=400,
            border_color=AppStyle.BORDER_DIM,
        )

        self.preview_card = ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Text("Theme Preview", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "สีของปุ่มและตัวหนังสือจะเปลี่ยนไปตาม Theme ที่เลือก",
                            size=14,
                            color=AppStyle.TEXT_SECONDARY,
                        ),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Primary Button",
                                    icon=ft.Icons.CHECK,
                                    style=ft.ButtonStyle(
                                        bgcolor=AppStyle.BTN_PRIMARY,
                                        color=AppStyle.BTN_ON_PRIMARY,
                                    ),
                                ),
                                ft.OutlinedButton("Secondary", icon=ft.Icons.INFO),
                                ft.IconButton(
                                    icon=ft.Icons.FAVORITE,
                                    icon_color=AppStyle.BTN_DANGER,
                                ),
                            ]
                        ),
                        ft.Container(height=10),
                        ft.TextField(
                            label="Input Field",
                            hint_text="Focus color changes too...",
                            border_color=AppStyle.BORDER_DIM,
                        ),
                        ft.ProgressBar(value=0.5, color=AppStyle.BTN_PRIMARY),
                    ]
                ),
            )
        )

        self.controls = [
            ft.Container(height=10),
            ft.Text("Display Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Color Theme", weight=ft.FontWeight.BOLD),
            self.theme_dropdown,
            ft.Container(height=30),
            ft.Text("Live Preview", weight=ft.FontWeight.BOLD),
            self.preview_card,
        ]

    def on_theme_change(self, e):
        selected_key = self.theme_dropdown.value

        # เรียกใช้ฟังก์ชัน apply_theme (ตอนนี้ Import มาแล้ว จะไม่ Error)
        theme_label = apply_theme(self.page, selected_key)

        # บันทึก
        save_theme(selected_key)

        self.toast.show(f"เปลี่ยน Theme เป็น: {theme_label}")
