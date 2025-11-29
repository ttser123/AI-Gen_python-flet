import flet as ft
from src.core.styles import AppStyle


class InputPart(ft.Column):
    def __init__(self, page, on_files_selected):
        super().__init__()
        self.page = page
        self.selected_files = []

        # File Picker
        self.file_picker = ft.FilePicker(on_result=lambda e: on_files_selected(e))

        self.upload_btn = ft.ElevatedButton(
            "เลือกรูปภาพ (Max 2)",
            icon=AppStyle.ICON_IMAGE,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=True, allowed_extensions=["png", "jpg", "jpeg", "webp"]
            ),
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
            border_color=AppStyle.BORDER_DIM,
        )

        self.style_dropdown = ft.Dropdown(
            label="Style",
            options=[
                ft.dropdown.Option(x)
                for x in [
                    "Photorealistic",
                    "Cinematic",
                    "Anime",
                    "Comic Book",
                    "3D Render",
                ]
            ],
            value="Photorealistic",
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )

        self.ratio_dropdown = ft.Dropdown(
            label="Aspect Ratio",
            options=[ft.dropdown.Option(x) for x in ["1:1", "16:9", "9:16"]],
            value="1:1",
            expand=True,
            border_color=AppStyle.BORDER_DIM,
        )

        self.controls = [
            ft.Text("Reference & Input", weight=ft.FontWeight.BOLD, size=16),
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
            ft.Container(height=10),
            self.prompt_input,
            ft.Row([self.style_dropdown, self.ratio_dropdown]),
        ]

    def update_preview(self, files):
        self.selected_files = [f.path for f in files[:2]]  # เก็บแค่ 2 รูป
        self.image_preview_row.controls.clear()
        for path in self.selected_files:
            self.image_preview_row.controls.append(
                ft.Container(
                    content=ft.Image(
                        src=path,
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
