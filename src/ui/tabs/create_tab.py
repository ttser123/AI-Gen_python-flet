import flet as ft
from src.core.config import AI_MODELS_MAP
from src.logic.providers.gemini_provider import GeminiProvider
from src.ui.components.toast import CustomToast
from src.core.key_manager import get_api_key
from src.core.history_manager import save_to_history
from src.ui.components.prompt_box import PromptBox
from src.core.styles import AppStyle  # Import Style


class CreateTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO

        self.gemini_provider = GeminiProvider()
        self.toast = CustomToast(page)
        self.selected_files = []

        # --- UI Components ---
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)

        self.upload_btn = ft.ElevatedButton(
            "เลือกรูปภาพ (Max 2)",
            icon=AppStyle.ICON_IMAGE,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=True, allowed_extensions=["png", "jpg", "jpeg", "webp"]
            ),
            # ใช้สี Secondary Container แทน Hardcode
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_SECONDARY, color="onSecondaryContainer"
            ),
        )
        self.image_preview_row = ft.Row(scroll=ft.ScrollMode.AUTO)

        self.prompt_input = ft.TextField(
            label="รายละเอียดสิ่งที่อยากได้ (Input)",
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="เช่น สินค้าวางอยู่บนโต๊ะไม้, แสงธรรมชาติ...",
            border_color=AppStyle.BORDER_DIM,  # ใช้สีขอบระบบ
        )

        # ... (Dropdowns Code เหมือนเดิม) ...
        self.style_dropdown = ft.Dropdown(
            label="Style",
            options=[
                ft.dropdown.Option("Photorealistic"),
                ft.dropdown.Option("Cinematic"),
                ft.dropdown.Option("Anime"),
                ft.dropdown.Option("Comic Book"),
                ft.dropdown.Option("3D Render"),
            ],
            value="Photorealistic",
            expand=True,
        )

        self.ratio_dropdown = ft.Dropdown(
            label="Aspect Ratio",
            options=[
                ft.dropdown.Option("1:1"),
                ft.dropdown.Option("16:9"),
                ft.dropdown.Option("9:16"),
            ],
            value="1:1",
            expand=True,
        )

        provider_options = list(AI_MODELS_MAP.keys())
        self.provider_dropdown = ft.Dropdown(
            label="1. เลือก Provider",
            options=[ft.dropdown.Option(p) for p in provider_options],
            value=provider_options[0],
            on_change=self.on_provider_change,
            expand=True,
        )

        initial_models = AI_MODELS_MAP[provider_options[0]]
        self.model_dropdown = ft.Dropdown(
            label="2. เลือก Model",
            options=[ft.dropdown.Option(m) for m in initial_models],
            value=initial_models[0],
            expand=True,
        )

        self.count_slider = ft.Slider(
            min=1,
            max=30,
            divisions=29,
            value=3,
            label="{value} Prompts",
            on_change=self.on_slider_change,
            active_color=AppStyle.BTN_PRIMARY,  # สี Slider ตามธีม
        )
        self.count_label = ft.Text("จำนวน: 3")

        self.generate_btn = ft.ElevatedButton(
            text="Generate Prompts",
            icon=AppStyle.ICON_GENERATE,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_PRIMARY,  # สีปุ่มหลัก
                color=AppStyle.BTN_ON_PRIMARY,  # สีตัวหนังสือบนปุ่ม
                padding=20,
            ),
            on_click=self.on_click_generate,
            width=200,
        )

        self.progress_bar = ft.ProgressBar(visible=False, color=AppStyle.LOADING)
        self.status_text = ft.Text("", color=AppStyle.TEXT_SECONDARY)
        self.output_list = ft.Column(spacing=10)

        self.controls = [
            ft.Container(height=10),
            ft.Card(
                # Card ไม่ต้องกำหนดสีพื้นหลัง Flet จะใช้ surfaceVariant ให้อัตโนมัติ
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Text("Reference & Input", weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    self.upload_btn,
                                    ft.Text(
                                        "รองรับ .png, .jpg (Max 2)",
                                        size=12,
                                        color=AppStyle.TEXT_SECONDARY,
                                    ),
                                ]
                            ),
                            self.image_preview_row,
                            ft.Divider(),
                            self.prompt_input,
                            ft.Row([self.style_dropdown, self.ratio_dropdown]),
                            ft.Divider(),
                            ft.Text("AI Configuration", weight=ft.FontWeight.BOLD),
                            ft.Row([self.provider_dropdown, self.model_dropdown]),
                            ft.Row(
                                [
                                    ft.Text("Outputs:"),
                                    self.count_label,
                                    self.count_slider,
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Container(height=20),
                            ft.Container(
                                content=self.generate_btn, alignment=ft.alignment.center
                            ),
                            ft.Container(height=10),
                            self.progress_bar,
                            ft.Container(
                                content=self.status_text, alignment=ft.alignment.center
                            ),
                        ]
                    ),
                )
            ),
            ft.Container(height=20),
            ft.Text("Generated Prompts", size=20, weight=ft.FontWeight.BOLD),
            self.output_list,
            ft.Container(height=50),
        ]

    def did_mount(self):
        self.page.overlay.append(self.file_picker)
        self.page.update()

    # ... (Logic อื่นๆ เหมือนเดิม Copy มาได้เลย) ...
    def on_provider_change(self, e):
        selected_provider = self.provider_dropdown.value
        new_models = AI_MODELS_MAP.get(selected_provider, [])
        self.model_dropdown.options = [ft.dropdown.Option(m) for m in new_models]
        if new_models:
            self.model_dropdown.value = new_models[0]
        else:
            self.model_dropdown.value = None
        self.update()

    def on_slider_change(self, e):
        self.count_label.value = f"จำนวน: {int(e.control.value)}"
        self.update()

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            files = e.files[:2]
            self.selected_files = [f.path for f in files]
            self.image_preview_row.controls.clear()
            for f in files:
                self.image_preview_row.controls.append(
                    ft.Container(
                        content=ft.Image(
                            src=f.path,
                            width=80,
                            height=80,
                            fit=ft.ImageFit.COVER,
                            border_radius=8,
                        ),
                        border=ft.border.all(1, AppStyle.BORDER),
                        border_radius=8,
                    )
                )
            self.update()

    async def on_click_generate(self, e):
        if "Google" not in self.provider_dropdown.value:
            self.toast.show("Provider นี้ยังไม่เปิดให้บริการ", is_error=True)
            return
        api_key = get_api_key()
        if not api_key:
            self.toast.show("ไม่พบ API Key", is_error=True)
            return
        if not self.selected_files and not self.prompt_input.value:
            self.toast.show("ต้องใส่รูปหรือข้อความอย่างน้อย 1 อย่าง", is_error=True)
            return

        self.generate_btn.disabled = True
        self.generate_btn.text = "Generating..."
        self.generate_btn.icon = ft.Icons.HOURGLASS_TOP
        self.generate_btn.style.bgcolor = "surfaceVariant"  # สีตอน Disable

        self.progress_bar.visible = True
        self.status_text.value = "AI is thinking..."
        self.output_list.controls.clear()
        self.update()

        try:
            self.gemini_provider.set_api_key(api_key)
            prompts = await self.gemini_provider.generate_prompts_from_image(
                model_name=self.model_dropdown.value,
                image_paths=self.selected_files,
                user_input=self.prompt_input.value,
                style=self.style_dropdown.value,
                ratio=self.ratio_dropdown.value,
                count=int(self.count_slider.value),
            )
            for i, prompt in enumerate(prompts):
                self.add_prompt_result(i + 1, prompt)

            save_to_history(
                provider=self.provider_dropdown.value,
                model=self.model_dropdown.value,
                input_text=self.prompt_input.value,
                image_paths=self.selected_files,
                prompts=prompts,
            )
            self.status_text.value = "Done!"
            self.toast.show(f"สร้างสำเร็จ {len(prompts)} รายการ")
        except Exception as err:
            self.status_text.value = f"Error: {err}"
            self.toast.show("เกิดข้อผิดพลาดในการเชื่อมต่อ AI", is_error=True)
        finally:
            self.generate_btn.disabled = False
            self.generate_btn.text = "Generate Prompts"
            self.generate_btn.icon = AppStyle.ICON_GENERATE
            self.generate_btn.style.bgcolor = AppStyle.BTN_PRIMARY  # คืนค่าสีหลัก
            self.progress_bar.visible = False
            self.update()

    def add_prompt_result(self, index, prompt_text):
        self.output_list.controls.append(PromptBox(self.page, prompt_text, index))
