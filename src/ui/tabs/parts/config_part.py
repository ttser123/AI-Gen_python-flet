import flet as ft
from src.core.config import AI_MODELS_MAP, IMAGE_GEN_MODELS_MAP
from src.core.styles import AppStyle


class ConfigPart(ft.Column):
    def __init__(self, on_click_gen_text, on_click_gen_image):
        super().__init__()

        # --- Step 1: Text Gen Controls ---
        provider_options = list(AI_MODELS_MAP.keys())

        self.provider_dropdown = ft.Dropdown(
            label="1. Text Provider",
            options=[ft.dropdown.Option(p) for p in provider_options],
            value=provider_options[0],
            on_change=self.on_text_provider_change,
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )

        # โหลดโมเดลเริ่มต้น
        initial_text_models = AI_MODELS_MAP[provider_options[0]]
        self.model_dropdown = ft.Dropdown(
            label="Text Model",
            options=[
                ft.dropdown.Option(key=m["id"], text=m["name"])
                for m in initial_text_models
            ],
            value=initial_text_models[0]["id"],  # ใช้ ID เป็นค่า Value
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

        # --- Step 2: Image Gen Controls ---
        img_providers = list(IMAGE_GEN_MODELS_MAP.keys())

        self.img_provider_dropdown = ft.Dropdown(
            label="2. Image Provider",
            options=[ft.dropdown.Option(p) for p in img_providers],
            value=img_providers[0],
            on_change=self.on_img_provider_change,
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )

        initial_img_models = IMAGE_GEN_MODELS_MAP[img_providers[0]]
        self.img_model_dropdown = ft.Dropdown(
            label="Image Model",
            options=[
                ft.dropdown.Option(key=m["id"], text=m["name"])
                for m in initial_img_models
            ],
            value=initial_img_models[0]["id"],  # ใช้ ID
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
                    ft.Icon(ft.Icons.LOOKS_TWO, color=AppStyle.BTN_ON_PRIMARY),
                    ft.Text("Image Gen Config", weight=ft.FontWeight.BOLD, size=16),
                ]
            ),
            ft.Row([self.img_provider_dropdown, self.img_model_dropdown]),
            ft.Container(height=10),
            ft.Container(
                content=self.generate_image_btn, alignment=ft.alignment.center
            ),
        ]

    # --- Event Handlers ---
    def on_text_provider_change(self, e):
        models = AI_MODELS_MAP.get(self.provider_dropdown.value, [])
        self.model_dropdown.options = [
            ft.dropdown.Option(key=m["id"], text=m["name"]) for m in models
        ]
        self.model_dropdown.value = models[0]["id"] if models else None
        self.update()

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
