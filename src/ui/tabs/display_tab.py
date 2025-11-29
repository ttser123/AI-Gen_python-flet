import flet as ft
from src.core.theme_manager import save_theme
from src.ui.components.toast import CustomToast
from src.core.styles import AppStyle


class DisplayTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.toast = CustomToast(page)

        self.theme_selector = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="light", label="Light Mode (สว่าง)"),
                    ft.Radio(value="dark", label="Dark Mode (มืด)"),
                ]
            ),
            value=self.page.theme_mode,
            on_change=self.on_theme_change,
        )

        self.preview_card = ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Text(
                            "UI Preview Element", size=20, weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "ตัวอย่างข้อความทั่วไป เพื่อดูความชัดเจนของสี",
                            size=14,
                            color=AppStyle.TEXT_SECONDARY,
                        ),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Primary",
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
                            label="Example Input",
                            hint_text="ลองพิมพ์ดูสิ...",
                            border_color=AppStyle.BORDER_DIM,
                        ),
                    ]
                ),
            )
        )

        self.controls = [
            ft.Container(height=10),
            ft.Text("Display Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Theme Mode", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.theme_selector,
                padding=10,
                bgcolor="surfaceVariant",  # ใช้สีระบบ
                border_radius=8,
            ),
            ft.Container(height=30),
            ft.Text("Live Preview", weight=ft.FontWeight.BOLD),
            self.preview_card,
        ]

    def on_theme_change(self, e):
        selected_mode = e.control.value
        self.page.theme_mode = selected_mode
        save_theme(selected_mode)
        self.page.update()
        mode_text = "โหมดสว่าง" if selected_mode == "light" else "โหมดมืด"
        self.toast.show(f"เปลี่ยนเป็น {mode_text} เรียบร้อย")
