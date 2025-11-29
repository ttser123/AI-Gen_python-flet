import flet as ft
from src.core.styles import AppStyle
from src.ui.components.toast import CustomToast
import time
import threading


class PromptBox(ft.Container):
    def __init__(self, page: ft.Page, prompt_text: str, index: int = None):
        super().__init__()
        self.page = page
        self.prompt_text = prompt_text
        self.index = index
        self.toast = CustomToast(page)

        # 1. ตั้งค่า Container หลัก
        self.border_radius = 8
        # ใช้ BORDER_COLOR ที่เราเพิ่งเพิ่มกลับไป
        self.border = ft.border.all(1, AppStyle.BORDER_COLOR)
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.margin = ft.margin.only(bottom=10)

        # 2. ส่วน Header
        self.header = ft.Container(
            bgcolor=AppStyle.PROMPT_HEADER_BG,
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            content=ft.Row(
                controls=[
                    ft.Text(
                        f"Prompt #{index}" if index else "Generated Prompt",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=AppStyle.TEXT_SECONDARY,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    AppStyle.ICON_COPY,
                                    size=14,
                                    color=AppStyle.TEXT_SECONDARY,
                                ),
                                ft.Text("Copy", size=12, color=AppStyle.TEXT_SECONDARY),
                            ],
                            spacing=5,
                        ),
                        on_click=self.copy_to_clipboard,
                        padding=5,
                        border_radius=4,
                        ink=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # 3. ส่วน Body
        self.body = ft.Container(
            bgcolor=AppStyle.PROMPT_BODY_BG,
            padding=15,
            width=float("inf"),
            content=ft.Text(
                prompt_text,
                size=14,
                selectable=True,
                font_family="Consolas, monospace",
                color=AppStyle.TEXT_PRIMARY,
            ),
        )

        # 4. ประกอบร่าง
        self.content = ft.Column(spacing=0, controls=[self.header, self.body])

    def copy_to_clipboard(self, e):
        self.page.set_clipboard(self.prompt_text)
        self.toast.show("คัดลอก Prompt เรียบร้อย")

        # เปลี่ยนไอคอนชั่วคราว
        icon_row = e.control.content
        icon_row.controls[0].name = ft.Icons.CHECK
        icon_row.controls[1].value = "Copied!"
        icon_row.controls[0].color = ft.Colors.GREEN_400
        icon_row.controls[1].color = ft.Colors.GREEN_400
        e.control.update()

        def reset_icon():
            time.sleep(2)
            try:
                icon_row.controls[0].name = AppStyle.ICON_COPY
                icon_row.controls[1].value = "Copy"
                icon_row.controls[0].color = AppStyle.TEXT_SECONDARY
                icon_row.controls[1].color = AppStyle.TEXT_SECONDARY
                e.control.update()
            except:
                pass

        threading.Thread(target=reset_icon, daemon=True).start()
