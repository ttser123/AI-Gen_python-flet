import flet as ft
from src.core.config import AI_MODELS_MAP, IMAGE_GEN_MODELS_MAP
from src.ui.components.toast import CustomToast
from src.core.key_manager import save_api_keys, get_api_keys
from src.core.styles import AppStyle


class SettingsTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.toast = CustomToast(page)

        # --- 1. API Configuration Section ---
        self.text_key_field = ft.TextField(
            label="Gemini Text API Key",
            password=True,
            can_reveal_password=True,
            icon=ft.Icons.KEY,
            border_color=AppStyle.BORDER_DIM,
            width=500,
            helper_text="สำหรับสร้าง Prompt (Step 1)",
        )

        self.image_key_field = ft.TextField(
            label="Gemini Image API Key",
            password=True,
            can_reveal_password=True,
            icon=ft.Icons.IMAGE,
            border_color=AppStyle.BORDER_DIM,
            width=500,
            helper_text="สำหรับสร้างรูปภาพ (Step 2) - ใช้ Key เดียวกับ Text ได้",
        )

        self.save_btn = ft.ElevatedButton(
            text="Save Settings",
            icon=AppStyle.ICON_SAVE,
            on_click=self.show_confirm_dialog,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_PRIMARY, color=AppStyle.BTN_ON_PRIMARY
            ),
        )

        # --- 2. Model Status Section (สร้างอัตโนมัติจาก Config) ---

        # ตารางสำหรับ Text Models
        self.text_model_table = self.create_model_table(
            AI_MODELS_MAP, "Text Generation Models"
        )

        # ตารางสำหรับ Image Models
        self.image_model_table = self.create_model_table(
            IMAGE_GEN_MODELS_MAP, "Image Generation Models"
        )

        # --- Layout ---
        self.controls = [
            ft.Container(height=20),
            ft.Text("API Configuration", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            self.text_key_field,
            ft.Container(height=10),
            self.image_key_field,
            ft.Container(height=20),
            self.save_btn,
            ft.Divider(height=40, thickness=1),
            ft.Text(
                "System Status & Supported Models", size=20, weight=ft.FontWeight.BOLD
            ),
            ft.Text(
                "รายชื่อโมเดลที่ระบบรองรับ",
                size=12,
                color=AppStyle.TEXT_SECONDARY,
            ),
            ft.Container(height=20),
            self.text_model_table,
            ft.Container(height=20),
            self.image_model_table,
            ft.Container(height=50),  # Padding ล่าง
        ]

        # Dialogs & Data Load
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ยืนยันการบันทึก"),
            content=ft.Text("ต้องการบันทึก API Keys ลงไฟล์ในเครื่องหรือไม่?"),
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

    # --- Helper: ฟังก์ชันสร้างตารางอัตโนมัติ ---
    def create_model_table(self, data_map, title):
        rows = []
        for provider, models in data_map.items():
            for m in models:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(provider, weight=ft.FontWeight.BOLD)
                            ),  # Provider
                            ft.DataCell(ft.Text(m["name"])),  # Model Name (Display)
                            ft.DataCell(
                                ft.Text(
                                    m["id"],
                                    font_family="monospace",
                                    size=12,
                                    color=AppStyle.TEXT_SECONDARY,
                                )
                            ),  # Model ID
                        ]
                    )
                )

        # สร้าง DataTable Container
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LIST_ALT, color=AppStyle.TEXT_SECONDARY),
                        ft.Text(
                            title,
                            weight=ft.FontWeight.BOLD,
                            size=16,
                            color=AppStyle.BTN_PRIMARY,
                        ),
                    ]
                ),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Provider")),
                        ft.DataColumn(ft.Text("Model Name")),
                        ft.DataColumn(ft.Text("Internal ID")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, AppStyle.BORDER_DIM),
                    vertical_lines=ft.border.BorderSide(1, AppStyle.BORDER_DIM),
                    horizontal_lines=ft.border.BorderSide(1, AppStyle.BORDER_DIM),
                    width=float("inf"),  # ขยายเต็มจอ
                ),
            ]
        )

    # --- Save/Load Logic ---
    def load_initial_data(self):
        keys = get_api_keys()
        self.text_key_field.value = keys.get("gemini_text_key", "")
        self.image_key_field.value = keys.get("gemini_image_key", "")

    def show_confirm_dialog(self, e):
        if not self.text_key_field.value:
            self.toast.show("กรุณากรอก Text API Key อย่างน้อย 1 ช่อง", is_error=True)
            return
        self.page.open(self.confirm_dialog)

    def close_dialog(self, e):
        self.page.close(self.confirm_dialog)

    def save_settings(self, e):
        self.page.close(self.confirm_dialog)

        txt_key = self.text_key_field.value
        # Auto-fill ถ้าช่อง Image ว่าง
        img_key = self.image_key_field.value if self.image_key_field.value else txt_key

        success = save_api_keys(txt_key, img_key)

        if success:
            self.toast.show("บันทึก API Keys เรียบร้อยแล้ว!")
            self.image_key_field.value = img_key
            self.update()
        else:
            self.toast.show("เกิดข้อผิดพลาดในการบันทึกไฟล์", is_error=True)
