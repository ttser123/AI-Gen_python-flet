import flet as ft
from src.core.styles import AppStyle
from src.ui.components.toast import CustomToast
import base64


class PromptBox(ft.Container):
    def __init__(self, page: ft.Page, prompt_text: str, index: int = None):
        super().__init__()
        self.page = page
        self.prompt_text = prompt_text
        self.index = index
        self.toast = CustomToast(page)

        self.current_image_bytes = None

        # ... (ส่วน Setup UI: header, body, controls... เหมือนเดิมทุกอย่าง) ...
        # (ขอข้ามโค้ดส่วน UI Setup เพื่อความกระชับ ให้คงโค้ดเดิมไว้)

        # --- ก๊อปปี้ส่วน __init__ ทั้งหมดของเดิมมาวาง หรือแก้แค่ด้านล่างนี้ ---

        self.save_file_picker = ft.FilePicker(on_result=self.on_save_file_result)
        # Note: การ add overlay ใน init อาจ error ในบางจังหวะถ้า page ยังไม่พร้อม
        # แต่ถ้าโค้ดเดิมทำงานได้ก็โอเคครับ หรือย้ายไป did_mount ของ Tab หลักจะชัวร์กว่า
        # เบื้องต้นปล่อยไว้ก่อน
        if self.page:
            self.page.overlay.append(self.save_file_picker)

        # ... (ส่วน UI Setup เหมือนเดิม) ...
        self.border_radius = 8
        self.border = ft.border.all(1, AppStyle.BORDER_COLOR)
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.margin = ft.margin.only(bottom=10)

        # (Header UI ... เหมือนเดิม)
        self.header = ft.Container(
            bgcolor=AppStyle.PROMPT_HEADER_BG,
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            content=ft.Row(
                controls=[
                    ft.Text(
                        f"Prompt #{index}",
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

        # (Body UI ... เหมือนเดิม)
        self.text_content = ft.Text(
            prompt_text,
            size=14,
            selectable=True,
            font_family="Consolas, monospace",
            color=AppStyle.TEXT_PRIMARY,
        )
        self.image_control = ft.Image(
            src_base64=None,
            visible=False,
            width=512,
            height=512,
            fit=ft.ImageFit.CONTAIN,
            border_radius=8,
        )
        self.save_img_btn = ft.ElevatedButton(
            "Download Image",
            icon=AppStyle.ICON_SAVE,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_SECONDARY, color="onSecondaryContainer"
            ),
            visible=False,
            on_click=self.open_save_dialog,
        )
        self.error_text = ft.Text(
            "",
            color=AppStyle.BTN_DANGER,
            size=12,
            visible=False,
            selectable=True,
            font_family="Consolas, monospace",
        )

        self.body = ft.Container(
            bgcolor=AppStyle.PROMPT_BODY_BG,
            padding=15,
            width=float("inf"),
            content=ft.Column(
                [
                    self.text_content,
                    ft.Container(height=10),
                    ft.Column(
                        [
                            self.image_control,
                            self.error_text,
                            ft.Container(height=5),
                            self.save_img_btn,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ]
            ),
        )
        self.content = ft.Column(spacing=0, controls=[self.header, self.body])

    def copy_to_clipboard(self, e):
        self.page.set_clipboard(self.prompt_text)
        self.toast.show("คัดลอก Prompt เรียบร้อย")

    # --- แก้ไขฟังก์ชันนี้: เพิ่ม run_update ---
    def set_image(self, image_bytes, run_update=True):
        if image_bytes:
            self.current_image_bytes = image_bytes
            b64_img = base64.b64encode(image_bytes).decode("utf-8")
            self.image_control.src_base64 = b64_img
            self.image_control.visible = True
            self.save_img_btn.visible = True
            self.error_text.visible = False

            # สั่ง update เฉพาะตอนที่จำเป็น (เช่น ตอน Gen เสร็จใหม่ๆ)
            if run_update:
                self.update()

    # --- แก้ไขฟังก์ชันนี้: เพิ่ม run_update ---
    def set_error(self, error_message, run_update=True):
        self.current_image_bytes = None
        self.image_control.visible = False
        self.save_img_btn.visible = False
        self.error_text.value = f"⚠️ {error_message}"
        self.error_text.visible = True

        if run_update:
            self.update()

    # ... (Save Logic เหมือนเดิม) ...
    def open_save_dialog(self, e):
        if self.current_image_bytes:
            # 1. เช็คความชัวร์ว่า Picker อยู่ใน Overlay ไหม
            if self.save_file_picker not in self.page.overlay:
                self.page.overlay.append(self.save_file_picker)

            # 2. *** สำคัญมาก ***: สั่ง update page เพื่อลงทะเบียน Picker ก่อนเรียกใช้
            self.page.update()

            # 3. เปิด Dialog
            filename = f"prompt_{self.index if self.index else 'gen'}.png"
            self.save_file_picker.save_file(
                dialog_title="Save Image",
                file_name=filename,
                allowed_extensions=["png"],
            )

    def on_save_file_result(self, e: ft.FilePickerResultEvent):
        if e.path and self.current_image_bytes:
            try:
                with open(e.path, "wb") as f:
                    f.write(self.current_image_bytes)
                self.toast.show(f"บันทึกรูปภาพเรียบร้อย")
            except Exception as err:
                self.toast.show(f"บันทึกไม่สำเร็จ: {err}", is_error=True)
