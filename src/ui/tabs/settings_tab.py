import flet as ft
import httpx
from src.core.config import AI_MODELS_MAP, IMAGE_GEN_MODELS_MAP
from src.ui.components.toast import CustomToast
from src.core.key_manager import save_api_keys, get_api_keys
from src.core.styles import AppStyle
from src.core.ollama_manager import load_ollama_settings, save_ollama_settings


class SettingsTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.toast = CustomToast(page)

        # --- 1. Gemini API Configuration ---
        self.text_key_field = ft.TextField(
            label="Gemini Text API Key",
            password=True,
            can_reveal_password=True,
            icon=ft.Icons.KEY,
            border_color=AppStyle.BORDER_DIM,
            expand=True,
            helper_text="สำหรับสร้าง Prompt (Step 1)",
        )

        self.image_key_field = ft.TextField(
            label="Gemini Image API Key",
            password=True,
            can_reveal_password=True,
            icon=ft.Icons.IMAGE,
            border_color=AppStyle.BORDER_DIM,
            expand=True,
            helper_text="สำหรับสร้างรูปภาพ (Step 2) - ใช้ Key เดียวกับ Text ได้",
        )

        # --- 2. Ollama Configuration ---
        self.ollama_settings = load_ollama_settings()
        # ดึงค่าเดิมมาเก็บไว้
        self.saved_base_url = self.ollama_settings.get(
            "base_url", "http://localhost:11434"
        )
        self.saved_models = self.ollama_settings.get("selected_models", [])

        self.ollama_url_field = ft.TextField(
            label="Ollama Base URL",
            value=self.saved_base_url,
            icon=ft.Icons.LINK,
            expand=True,
        )

        self.scan_btn = ft.ElevatedButton(
            "Scan Local Models", icon=ft.Icons.SEARCH, on_click=self.scan_ollama_models
        )

        # Container สำหรับ Checkbox list (ใส่กรอบ + Scroll)
        self.ollama_models_list = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)

        # 2. เอา scroll ออกจาก Container
        self.ollama_list_container = ft.Container(
            content=self.ollama_models_list,
            height=200,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
            visible=False,
            # scroll=ft.ScrollMode.AUTO  <--- ลบบรรทัดนี้ทิ้ง! Container scroll ไม่ได้
        )

        # --- 3. Main Action Buttons ---
        self.save_btn = ft.ElevatedButton(
            text="Save All Settings",
            icon=ft.Icons.SAVE,
            on_click=self.show_confirm_dialog,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, padding=15
            ),
        )

        # --- 4. Tables (Read-only info) ---
        self.text_model_table = self.create_model_table(
            AI_MODELS_MAP, "Supported Cloud Models (Text)"
        )
        self.image_model_table = self.create_model_table(
            IMAGE_GEN_MODELS_MAP, "Supported Cloud Models (Image)"
        )

        # --- Layout Assembly ---
        self.controls = [
            ft.Container(height=10),
            ft.Text("API & Model Configuration", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Text("Gemini Cloud API", size=18, weight="bold"),
                            self.text_key_field,
                            ft.Container(height=10),
                            self.image_key_field,
                        ]
                    ),
                )
            ),
            ft.Container(height=10),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Text("Ollama Local API", size=18, weight="bold"),
                            ft.Row([self.ollama_url_field, self.scan_btn]),
                            ft.Text(
                                "Select models to use in Create Tab:",
                                size=14,
                                color=ft.Colors.GREY_400,
                            ),
                            self.ollama_list_container,
                        ]
                    ),
                )
            ),
            ft.Container(height=20),
            ft.Row([self.save_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=40),
            ft.Text("System Reference", size=20, weight=ft.FontWeight.BOLD),
            self.text_model_table,
            ft.Container(height=20),
            self.image_model_table,
            ft.Container(height=50),
        ]

        # Dialogs
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Save"),
            content=ft.Text("บันทึกการตั้งค่าทั้งหมดลงในเครื่อง?"),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Save", on_click=self.save_settings),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def did_mount(self):
        # โหลดข้อมูลเมื่อหน้าจอแสดงผล
        self.load_initial_data()
        # Render Checkbox เดิมที่เคย Save ไว้ (ถ้ามี)
        if self.saved_models:
            self.render_checkboxes(self.saved_models, pre_check=True)

    # --- Methods ---

    def load_initial_data(self):
        keys = get_api_keys()
        self.text_key_field.value = keys.get("gemini_text_key", "")
        self.image_key_field.value = keys.get("gemini_image_key", "")

    def render_checkboxes(self, model_names, pre_check=False):
        """
        model_names: list ของชื่อโมเดลที่เจอ
        pre_check: ถ้า True คือติ๊กถูกทั้งหมด (ใช้ตอนโหลดจากไฟล์ Save)
        """
        self.ollama_models_list.controls.clear()

        if not model_names:
            self.ollama_list_container.visible = False
            return

        self.ollama_list_container.visible = True

        for name in model_names:
            # Logic:
            # ถ้า pre_check=True (โหลดจาก Save) -> ติ๊กเลย
            # ถ้า pre_check=False (Scan ใหม่) -> ติ๊กเฉพาะตัวที่เคย Save ไว้ใน self.saved_models
            is_checked = True if pre_check else (name in self.saved_models)

            self.ollama_models_list.controls.append(
                ft.Checkbox(label=name, value=is_checked)
            )
        self.update()

    async def scan_ollama_models(self, e):
        base_url = self.ollama_url_field.value
        url = f"{base_url}/api/tags"

        self.scan_btn.disabled = True
        self.scan_btn.text = "Scanning..."
        self.update()

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                models_data = data.get("models", [])
                # ดึงเฉพาะชื่อโมเดล
                model_names = [m["name"] for m in models_data]

                # Render โดยเช็คเทียบกับของเก่า
                self.render_checkboxes(model_names, pre_check=False)

                self.toast.show(f"พบ {len(model_names)} โมเดล")
            else:
                self.toast.show("เชื่อมต่อได้ แต่ไม่พบข้อมูล", is_error=True)

        except Exception as err:
            self.toast.show(f"เชื่อมต่อไม่สำเร็จ: {err}", is_error=True)

        finally:
            self.scan_btn.disabled = False
            self.scan_btn.text = "Scan Local Models"
            self.update()

    def show_confirm_dialog(self, e):
        self.page.open(self.confirm_dialog)

    def close_dialog(self, e):
        self.page.close(self.confirm_dialog)

    def save_settings(self, e):
        self.page.close(self.confirm_dialog)

        # 1. Save Gemini Keys
        txt_key = self.text_key_field.value
        img_key = self.image_key_field.value if self.image_key_field.value else txt_key
        keys_success = save_api_keys(txt_key, img_key)

        # 2. Save Ollama Config
        ollama_url = self.ollama_url_field.value
        # วนลูปเก็บเฉพาะตัวที่ติ๊ก
        selected_models = []
        for ctrl in self.ollama_models_list.controls:
            if isinstance(ctrl, ft.Checkbox) and ctrl.value:
                selected_models.append(ctrl.label)

        try:
            save_ollama_settings(ollama_url, selected_models)
            ollama_success = True
            # อัปเดตตัวแปรใน memory ด้วย
            self.saved_models = selected_models
        except Exception as ex:
            ollama_success = False
            print(ex)

        # 3. Feedback
        if keys_success and ollama_success:
            self.toast.show("บันทึกการตั้งค่าทั้งหมดเรียบร้อย!")
            # อัปเดต UI field เผื่อ auto-fill
            self.image_key_field.value = img_key
            self.update()
        else:
            self.toast.show("เกิดข้อผิดพลาดในการบันทึก", is_error=True)

    def create_model_table(self, data_map, title):
        rows = []
        for provider, models in data_map.items():
            for m in models:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(provider, weight="bold")),
                            ft.DataCell(ft.Text(m["name"])),
                            ft.DataCell(
                                ft.Text(
                                    m["id"],
                                    font_family="monospace",
                                    size=12,
                                    color="grey",
                                )
                            ),
                        ]
                    )
                )

        return ft.Column(
            [
                ft.Text(title, weight="bold", color=ft.Colors.BLUE_GREY),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Provider")),
                        ft.DataColumn(ft.Text("Model Name")),
                        ft.DataColumn(ft.Text("ID")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    width=float("inf"),
                ),
            ]
        )
