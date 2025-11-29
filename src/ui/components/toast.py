import flet as ft
from src.core.styles import AppStyle  # เรียกใช้ Style
import time
import threading


class CustomToast(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.visible = False
        self.right = 20
        self.top = 20
        self.opacity = 0
        self.padding = 15
        self.border_radius = 8

        # ใช้สี Inverse Surface (เช่น ถ้าธีมขาว Toast จะดำ, ถ้าธีมดำ Toast จะขาวเทา)
        self.bgcolor = "inverseSurface"

        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.3, "black"),  # เงา
            offset=ft.Offset(0, 4),
        )

        # เนื้อหาข้างใน
        self.icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=AppStyle.SUCCESS, size=24)
        self.message = ft.Text(
            "Action Successful",
            color="onInverseSurface",  # สีตัวหนังสือบน Inverse
            size=14,
            weight=ft.FontWeight.W_500,
        )

        self.content = ft.Row(
            controls=[
                self.icon,
                ft.Column(
                    [self.message], alignment=ft.MainAxisAlignment.CENTER, spacing=0
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color="onInverseSurface",  # ปุ่มปิด
                    icon_size=18,
                    on_click=self.hide_toast,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            width=300,
        )

    # ... (ส่วน Logic show/hide เหมือนเดิม ไม่ต้องแก้) ...
    def show(self, message: str, is_error=False):
        self.message.value = message
        if is_error:
            self.icon.name = ft.Icons.ERROR
            self.icon.color = "error"  # ใช้สี error ของระบบ
        else:
            self.icon.name = ft.Icons.CHECK_CIRCLE
            self.icon.color = AppStyle.SUCCESS

        if self not in self.page.overlay:
            self.page.overlay.append(self)

        self.visible = True
        self.opacity = 1
        self.page.update()

        def auto_hide():
            time.sleep(3)
            try:
                if self.opacity == 1:
                    self.hide_toast(None)
            except:
                pass

        threading.Thread(target=auto_hide, daemon=True).start()

    def hide_toast(self, e):
        self.opacity = 0
        self.update()
        time.sleep(0.3)
        self.visible = False
        self.update()
