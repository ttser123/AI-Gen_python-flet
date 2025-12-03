import flet as ft
from src.core.config import AI_MODELS_MAP, IMAGE_GEN_MODELS_MAP
from src.core.styles import AppStyle
from src.core.ollama_manager import load_ollama_settings


class ConfigPart(ft.Column):
    def __init__(self, on_click_gen_text, on_click_gen_image):
        super().__init__()

        # --- Step 1: Text Gen Controls ---
        provider_options = list(AI_MODELS_MAP.keys()) + ["Ollama (Local)"]

        self.provider_dropdown = ft.Dropdown(
            label="1. Text Provider",
            options=[ft.dropdown.Option(p) for p in provider_options],
            value=provider_options[0],
            on_change=self.on_text_provider_change,
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )

        # ... (ส่วนสร้าง model_dropdown และปุ่มต่างๆ เหมือนเดิม ไม่ต้องแก้) ...
        # (Copy โค้ดเดิมส่วน UI มาวางได้เลยครับ)
        # -------------------------------------------------------------

        # ใส่ Logic UI เดิมลงไปตรงนี้ (เพื่อความกระชับผมขอละไว้)
        self.model_dropdown = ft.Dropdown(
            label="Text Model",
            options=[
                ft.dropdown.Option(key=m["id"], text=m["name"])
                for m in AI_MODELS_MAP[provider_options[0]]
            ],
            value=AI_MODELS_MAP[provider_options[0]][0]["id"],
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )
        self.count_slider = ft.Slider(
            min=1,
            max=30,
            divisions=29,
            value=3,
            active_color=AppStyle.BTN_PRIMARY,
            on_change=self.on_slider_change,
        )
        self.count_label = ft.Text("จำนวน: 3")
        self.generate_text_btn = ft.ElevatedButton(
            "Generate Prompts (Step 1)",
            icon=AppStyle.ICON_GENERATE,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_PRIMARY, color=AppStyle.BTN_ON_PRIMARY, padding=20
            ),
            on_click=on_click_gen_text,
            width=250,
        )

        # Step 2 Image Gen (เหมือนเดิม)
        img_providers = list(IMAGE_GEN_MODELS_MAP.keys())
        self.img_provider_dropdown = ft.Dropdown(
            label="2. Image Provider",
            options=[ft.dropdown.Option(p) for p in img_providers],
            value=img_providers[0],
            on_change=self.on_img_provider_change,
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )
        self.img_model_dropdown = ft.Dropdown(
            label="Image Model",
            options=[
                ft.dropdown.Option(key=m["id"], text=m["name"])
                for m in IMAGE_GEN_MODELS_MAP[img_providers[0]]
            ],
            value=IMAGE_GEN_MODELS_MAP[img_providers[0]][0]["id"],
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )
        self.generate_image_btn = ft.ElevatedButton(
            "Generate Images (Step 2)",
            icon=AppStyle.ICON_IMAGE,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_SECONDARY, color="onSecondaryContainer", padding=20
            ),
            on_click=on_click_gen_image,
            visible=False,
        )

        self.controls = [
            ft.Row(
                [
                    ft.Icon(ft.Icons.LOOKS_ONE, color=AppStyle.BTN_PRIMARY),
                    ft.Text("Text Prompt Config", weight=ft.FontWeight.BOLD, size=16),
                ]
            ),
            ft.Row([self.provider_dropdown, self.model_dropdown]),
            ft.Row(
                [ft.Text("Outputs:"), self.count_label, self.count_slider],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Container(height=10),
            ft.Container(content=self.generate_text_btn, alignment=ft.alignment.center),
            ft.Divider(height=30, thickness=1),
            ft.Row(
                [
                    ft.Icon(ft.Icons.LOOKS_TWO, color=AppStyle.BTN_SECONDARY),
                    ft.Text("Image Gen Config", weight=ft.FontWeight.BOLD, size=16),
                ]
            ),
            ft.Row([self.img_provider_dropdown, self.img_model_dropdown]),
            ft.Container(height=10),
            ft.Container(
                content=self.generate_image_btn, alignment=ft.alignment.center
            ),
        ]

    # --- ส่วนสำคัญ: Lifecycle & Logic ---

    def did_mount(self):
        # Subscribe รับข่าวสาร
        self.page.pubsub.subscribe(self.on_message)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_all()

    def on_message(self, message):
        # ถ้าหน้า Setting บันทึกเสร็จ -> บังคับโหลดใหม่ทันที
        if message == "refresh_ollama_models":
            if self.provider_dropdown.value == "Ollama (Local)":
                self.load_ollama_models()

    def load_ollama_models(self):
        """โหลดรายชื่อจากไฟล์สดๆ"""
        # 1. โหลดไฟล์ใหม่ทุกครั้งที่เรียก (สำคัญ!)
        settings = load_ollama_settings()
        models = settings.get("selected_models", [])  # ใช้ key 'selected_models'

        if not models:
            # กรณีไม่มีข้อมูลในไฟล์เลย
            self.model_dropdown.options = [
                ft.dropdown.Option("Please scan models in Settings first")
            ]
            self.model_dropdown.value = "Please scan models in Settings first"
        else:
            # มีข้อมูล -> ใส่ Dropdown
            self.model_dropdown.options = [
                ft.dropdown.Option(key=m, text=m) for m in models
            ]
            # เลือกตัวแรก (ถ้าค่าเดิมไม่อยู่ในลิสต์ใหม่)
            if self.model_dropdown.value not in models:
                self.model_dropdown.value = models[0]

        self.model_dropdown.update()

    def on_text_provider_change(self, e):
        selected = self.provider_dropdown.value

        if selected == "Ollama (Local)":
            # เรียกฟังก์ชันโหลดสด
            self.load_ollama_models()
        else:
            # Logic เดิมของ Google/OpenAI
            models = AI_MODELS_MAP.get(selected, [])
            self.model_dropdown.options = [
                ft.dropdown.Option(key=m["id"], text=m["name"]) for m in models
            ]
            self.model_dropdown.value = models[0]["id"] if models else None
            self.model_dropdown.update()

    def on_img_provider_change(self, e):
        models = IMAGE_GEN_MODELS_MAP.get(self.img_provider_dropdown.value, [])
        self.img_model_dropdown.options = [
            ft.dropdown.Option(key=m["id"], text=m["name"]) for m in models
        ]
        self.img_model_dropdown.value = models[0]["id"] if models else None
        self.update()

    def on_slider_change(self, e):
        self.count_label.value = f"จำนวน: {int(e.control.value)}"
        self.update()
