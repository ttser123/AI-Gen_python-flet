import flet as ft
from src.core.config import SUPPORTED_MODELS
from src.ui.components.toast import CustomToast
from src.core.key_manager import save_api_key, get_api_key
from src.core.styles import AppStyle  # Import


class SettingsTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.toast = CustomToast(page)

        # UI Components
        self.gemini_key_field = ft.TextField(
            label="Gemini API Key",
            password=True,
            can_reveal_password=True,
            icon=ft.Icons.KEY,
            helper_text="Key จะถูกบันทึกไว้ในไฟล์ api_key.json ที่โฟลเดอร์โปรเจกต์",
        )

        self.openai_key_field = ft.TextField(
            label="OpenAI API Key (Coming Soon)",
            password=True,
            disabled=True,
            icon=ft.Icons.LOCK_CLOCK,
        )

        self.save_btn = ft.ElevatedButton(
            text="Save Settings",
            icon=AppStyle.ICON_SAVE,
            on_click=self.show_confirm_dialog,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_PRIMARY, color=AppStyle.BTN_ON_PRIMARY  # สีปุ่มหลัก
            ),
        )

        model_rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(model))])
            for model in SUPPORTED_MODELS
        ]

        self.model_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Supported AI Models"))],
            rows=model_rows,
            border=ft.border.all(1, AppStyle.BORDER_DIM),
            vertical_lines=ft.border.BorderSide(1, AppStyle.BORDER_DIM),
            horizontal_lines=ft.border.BorderSide(1, AppStyle.BORDER_DIM),
        )

        self.controls = [
            ft.Container(height=20),
            ft.Text("API Configuration", size=20, weight=ft.FontWeight.BOLD),
            self.gemini_key_field,
            self.openai_key_field,
            ft.Container(height=10),
            self.save_btn,
            ft.Divider(height=40, thickness=2),
            ft.Text("Model Status", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("รายชื่อโมเดลที่รองรับ:", size=12, color=AppStyle.TEXT_SECONDARY),
            self.model_table,
        ]

        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ยืนยันการบันทึก"),
            content=ft.Text("ต้องการบันทึก API Key ลงไฟล์ api_key.json หรือไม่?"),
            actions=[
                ft.TextButton("ยกเลิก", on_click=self.close_dialog),
                ft.TextButton(
                    "บันทึก",
                    on_click=self.save_settings,
                    style=ft.ButtonStyle(color=AppStyle.BTN_PRIMARY),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.load_initial_data()

    # ... (Logic เหมือนเดิม Copy ได้เลย) ...
    def load_initial_data(self):
        key = get_api_key()
        if key:
            self.gemini_key_field.value = key

    def show_confirm_dialog(self, e):
        if not self.gemini_key_field.value:
            self.toast.show("กรุณากรอก Gemini API Key ก่อนครับ", is_error=True)
            return
        self.page.open(self.confirm_dialog)

    def close_dialog(self, e):
        self.page.close(self.confirm_dialog)

    def save_settings(self, e):
        self.page.close(self.confirm_dialog)
        success = save_api_key(self.gemini_key_field.value)
        if success:
            self.toast.show("บันทึก API Key ลงไฟล์เรียบร้อยแล้ว!")
        else:
            self.toast.show("เกิดข้อผิดพลาดในการบันทึกไฟล์", is_error=True)
