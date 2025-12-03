import flet as ft
import asyncio
import io
from rembg import remove, new_session  # Import new_session เพิ่ม
from PIL import Image
from src.core.styles import AppStyle
from src.ui.components.toast import CustomToast
from src.core.key_manager import get_api_keys
from src.logic.image_providers.gemini_image import GeminiImageProvider
from src.core.template_manager import load_templates, save_templates
from src.core.config import IMAGE_EDIT_MODELS_MAP


class VirtualStudioTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO

        self.gemini_image = GeminiImageProvider()
        self.toast = CustomToast(page)

        self.selected_files = []
        self.custom_bg_path = None

        # --- Performance Optimization ---
        # เก็บ Session ของ rembg ไว้ใช้ซ้ำ (ไม่ต้องโหลดใหม่ทุกรอบ)
        self.rembg_session = None

        # --- 1. Templates ---
        self.templates = load_templates()
        self.template_dropdown = ft.Dropdown(
            label="เลือก Template ฉากหลัง",
            options=[ft.dropdown.Option(k) for k in self.templates.keys()],
            on_change=self.on_template_change,
            expand=True,
            text_size=12,
            border_color=AppStyle.BORDER_DIM,
        )
        self.btn_save_template = ft.IconButton(
            icon=ft.Icons.SAVE_AS,
            tooltip="Save Template",
            on_click=self.open_save_template_dialog,
        )

        # --- 2. Product Inputs ---
        self.file_picker = ft.FilePicker(on_result=self.on_files_picked)
        self.upload_btn = ft.ElevatedButton(
            "1. อัปโหลดสินค้า (Product)",
            icon=ft.Icons.UPLOAD_FILE,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_SECONDARY, color="onSecondaryContainer"
            ),
            on_click=lambda _: self.file_picker.pick_files(allow_multiple=True),
        )
        self.preview_row = ft.Row(scroll=ft.ScrollMode.AUTO, height=80)

        # --- 3. Composition ---
        self.scale_slider = ft.Slider(
            min=0.3,
            max=1.0,
            value=0.8,
            divisions=7,
            label="ขนาดสินค้า: {value}",
            active_color=AppStyle.BTN_PRIMARY,
        )
        self.pos_dropdown = ft.Dropdown(
            label="ตำแหน่งจัดวาง",
            options=[
                ft.dropdown.Option("center", "ตรงกลาง (Center)"),
                ft.dropdown.Option("bottom", "วางบนพื้น (Bottom)"),
                ft.dropdown.Option("bottom_left", "ซ้ายล่าง (Left)"),
                ft.dropdown.Option("bottom_right", "ขวาล่าง (Right)"),
            ],
            value="center",
            text_size=12,
            border_color=AppStyle.BORDER_DIM,
            expand=True,
        )

        # --- 4. Background ---
        self.bg_file_picker = ft.FilePicker(on_result=self.on_bg_picked)
        self.bg_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="AI Generate", icon=ft.Icons.AUTO_AWESOME),
                ft.Tab(text="Custom BG", icon=ft.Icons.IMAGE),
            ],
            on_change=self.on_tab_change,
        )

        self.prompt_field = ft.TextField(
            label="คำบรรยายฉากหลัง (Prompt)",
            hint_text="e.g. on a white podium, soft lighting",
            multiline=True,
            min_lines=2,
            border_color=AppStyle.BORDER_DIM,
        )

        self.bg_upload_btn = ft.ElevatedButton(
            "เลือกรูปพื้นหลัง (Background)",
            icon=ft.Icons.IMAGE_SEARCH,
            on_click=lambda _: self.bg_file_picker.pick_files(allow_multiple=False),
            visible=False,
        )
        self.bg_preview = ft.Image(
            src="",
            width=100,
            height=100,
            fit=ft.ImageFit.COVER,
            visible=False,
            border_radius=8,
        )

        # --- 5. Settings ---
        edit_models = IMAGE_EDIT_MODELS_MAP["Google (Gemini/Imagen)"]
        self.model_dropdown = ft.Dropdown(
            label="เลือกโมเดล (AI Model)",
            options=[
                ft.dropdown.Option(key=m["id"], text=m["name"]) for m in edit_models
            ],
            value=edit_models[0]["id"],
            expand=True,
            text_size=12,
            border_color=AppStyle.BORDER_DIM,
        )

        # --- 6. Generate Action ---
        self.generate_btn = ft.ElevatedButton(
            "Render Studio Image",
            icon=ft.Icons.CAMERA,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_PRIMARY, color=AppStyle.BTN_ON_PRIMARY, padding=20
            ),
            on_click=self.on_click_generate,
            width=300,
        )

        self.output_grid = ft.GridView(
            runs_count=2,
            max_extent=400,
            spacing=10,
            run_spacing=10,
            child_aspect_ratio=1.0,
            expand=True,
        )
        self.status_text = ft.Text(
            "Ready (Loading Models...)", color=AppStyle.TEXT_SECONDARY
        )
        self.progress_bar = ft.ProgressBar(visible=False, color=AppStyle.LOADING)

        # --- Layout ---
        self.controls = [
            ft.Container(height=10),
            ft.Text("Virtual Studio", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(
                [
                    # Left Panel
                    ft.Container(
                        width=400,
                        padding=15,
                        border=ft.border.all(1, AppStyle.BORDER_DIM),
                        border_radius=10,
                        content=ft.Column(
                            [
                                ft.Text("Step 1: Product", weight="bold"),
                                self.upload_btn,
                                self.preview_row,
                                ft.Divider(),
                                ft.Text("Step 2: Composition", weight="bold"),
                                self.scale_slider,
                                self.pos_dropdown,
                                ft.Divider(),
                                ft.Text("Step 3: Background", weight="bold"),
                                self.bg_tabs,
                                ft.Container(height=10),
                                self.prompt_field,
                                ft.Row(
                                    [self.template_dropdown, self.btn_save_template]
                                ),
                                self.bg_upload_btn,
                                self.bg_preview,
                                ft.Divider(),
                                ft.Text("Step 4: AI Settings", weight="bold"),
                                self.model_dropdown,
                                ft.Container(height=20),
                                ft.Container(
                                    content=self.generate_btn,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(height=10),
                                self.progress_bar,
                                ft.Container(
                                    content=self.status_text,
                                    alignment=ft.alignment.center,
                                ),
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    # Right Panel
                    ft.Container(
                        expand=True,
                        padding=20,
                        content=ft.Column(
                            [
                                ft.Text("Studio Results", size=20, weight="bold"),
                                self.output_grid,
                            ]
                        ),
                    ),
                ],
                expand=True,
            ),
        ]

        # Dialogs
        self.dlg_template_name = ft.TextField(label="Template Name")
        self.save_template_dialog = ft.AlertDialog(
            title=ft.Text("Save Template"),
            content=self.dlg_template_name,
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: self.page.close(self.save_template_dialog),
                ),
                ft.TextButton("Save", on_click=self.save_current_template),
            ],
        )

    def did_mount(self):
        self.page.overlay.extend([self.file_picker, self.bg_file_picker])
        self.page.update()

        # --- เริ่มโหลด Rembg Session ใน Background (เพื่อไม่ให้กดแล้วค้างครั้งแรก) ---
        self.page.run_task(self.init_rembg)

    async def init_rembg(self):
        """โหลดโมเดลตัดพื้นหลังเตรียมไว้"""
        if self.rembg_session is None:
            self.status_text.value = "Initializing AI Models..."
            self.update()
            # โหลดโมเดล u2net (มาตรฐาน)
            self.rembg_session = await asyncio.to_thread(new_session, "u2net")
            self.status_text.value = "Ready"
            self.update()

    # --- Handlers (ส่วนเดิม) ---
    def on_files_picked(self, e):
        if e.files:
            self.selected_files = [f.path for f in e.files]
            self.preview_row.controls.clear()
            for path in self.selected_files:
                self.preview_row.controls.append(
                    ft.Image(
                        src=path,
                        width=60,
                        height=60,
                        fit=ft.ImageFit.COVER,
                        border_radius=6,
                    )
                )
            self.update()

    def on_bg_picked(self, e):
        if e.files:
            self.custom_bg_path = e.files[0].path
            self.bg_preview.src = self.custom_bg_path
            self.bg_preview.visible = True
            self.update()

    def on_tab_change(self, e):
        is_ai_mode = self.bg_tabs.selected_index == 0
        self.prompt_field.visible = is_ai_mode
        self.template_dropdown.visible = is_ai_mode
        self.btn_save_template.visible = is_ai_mode
        self.bg_upload_btn.visible = not is_ai_mode
        self.bg_preview.visible = (not is_ai_mode) and (self.custom_bg_path is not None)
        self.update()

    def on_template_change(self, e):
        selected = self.template_dropdown.value
        if selected in self.templates:
            self.prompt_field.value = self.templates[selected]
            self.update()

    def open_save_template_dialog(self, e):
        if not self.prompt_field.value:
            self.toast.show("กรุณาพิมพ์ Prompt ก่อน", is_error=True)
            return
        self.dlg_template_name.value = ""
        self.page.open(self.save_template_dialog)

    def save_current_template(self, e):
        name = self.dlg_template_name.value
        if name:
            self.templates[name] = self.prompt_field.value
            save_templates(self.templates)
            self.template_dropdown.options = [
                ft.dropdown.Option(k) for k in self.templates.keys()
            ]
            self.template_dropdown.value = name
            self.page.close(self.save_template_dialog)
            self.update()

    # --- MAIN LOGIC (Optimized) ---
    async def on_click_generate(self, e):
        if not self.selected_files:
            self.toast.show("กรุณาเลือกรูปสินค้า", is_error=True)
            return
        keys = get_api_keys()
        if not keys.get("gemini_image_key"):
            self.toast.show("ไม่พบ Image API Key", is_error=True)
            return

        self.generate_btn.disabled = True
        self.progress_bar.visible = True
        self.output_grid.controls.clear()
        self.gemini_image.set_api_key(keys.get("gemini_image_key"))

        # รอ session ถ้ายังไม่พร้อม
        if self.rembg_session is None:
            self.status_text.value = "Loading RemBG Model (First run only)..."
            self.update()
            await self.init_rembg()

        use_custom_bg = self.bg_tabs.selected_index == 1
        if use_custom_bg and not self.custom_bg_path:
            self.toast.show("กรุณาเลือกรูปพื้นหลัง", is_error=True)
            self.generate_btn.disabled = False
            self.progress_bar.visible = False
            self.update()
            return

        total = len(self.selected_files)

        for i, file_path in enumerate(self.selected_files):
            self.status_text.value = f"Processing {i+1}/{total}..."
            self.update()

            try:
                base_bytes, mask_bytes = await asyncio.to_thread(
                    self.process_single_product,
                    file_path,
                    self.scale_slider.value,
                    self.pos_dropdown.value,
                    use_custom_bg,
                    self.custom_bg_path,
                )

                if mask_bytes is None:
                    raise Exception(base_bytes)

                final_prompt = (
                    self.prompt_field.value
                    if not use_custom_bg
                    else "blending object into background, realistic lighting, shadows, high quality"
                )

                result_bytes = await self.gemini_image.edit_image(
                    base_image_bytes=base_bytes,
                    mask_bytes=mask_bytes,
                    prompt=final_prompt,
                    model=self.model_dropdown.value,
                )

                if isinstance(result_bytes, str):
                    self.toast.show(f"Failed: {result_bytes}", is_error=True)
                else:
                    import base64

                    b64_img = base64.b64encode(result_bytes).decode("utf-8")
                    self.output_grid.controls.append(
                        ft.Container(
                            content=ft.Image(
                                src_base64=b64_img,
                                fit=ft.ImageFit.CONTAIN,
                                border_radius=8,
                            ),
                            border=ft.border.all(1, AppStyle.BORDER_DIM),
                            border_radius=8,
                            padding=5,
                            bgcolor="surfaceVariant",
                        )
                    )
                    self.update()

            except Exception as err:
                print(err)

        self.generate_btn.disabled = False
        self.progress_bar.visible = False
        self.status_text.value = "Done!"
        self.update()

    def process_single_product(
        self, file_path, scale, position, use_custom_bg, bg_path
    ):
        try:
            # 1. OPTIMIZATION: Load & Resize Input Image ก่อนส่งเข้า Rembg
            # การลดขนาดรูปลงก่อนตัดพื้นหลัง จะช่วยลดภาระ CPU ได้มหาศาล (แก้ปัญหาจอค้าง)

            with open(file_path, "rb") as f:
                input_bytes = f.read()

            # แปลงเป็น PIL เพื่อย่อขนาด
            original_pil = Image.open(io.BytesIO(input_bytes))

            # ถ้าภาพใหญ่เกิน 1500px ให้ย่อลง (คุณภาพยังดีอยู่สำหรับการ Gen AI ต่อ)
            if original_pil.width > 1500 or original_pil.height > 1500:
                original_pil.thumbnail((1500, 1500))

            # แปลงกลับเป็น bytes เพื่อส่ง rembg
            buffered = io.BytesIO()
            original_pil.save(buffered, format="PNG")
            optimized_input_bytes = buffered.getvalue()

            # 2. Remove Background (ใช้ Session ที่เตรียมไว้)
            subject_no_bg = remove(optimized_input_bytes, session=self.rembg_session)

            # (ส่วน Logic การจัดวาง Composition เหมือนเดิม)
            img_pil = Image.open(io.BytesIO(subject_no_bg)).convert("RGBA")

            CANVAS_SIZE = (1024, 1024)
            bg_img = None
            if use_custom_bg and bg_path:
                bg_img = Image.open(bg_path).convert("RGB")
                bg_img.thumbnail((1024, 1024))
                CANVAS_SIZE = bg_img.size
            else:
                bg_img = Image.new("RGB", CANVAS_SIZE, (255, 255, 255))

            target_w = int(CANVAS_SIZE[0] * scale)
            target_h = int(CANVAS_SIZE[1] * scale)
            img_pil.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)

            pw, ph = img_pil.size
            cw, ch = CANVAS_SIZE
            x, y = (cw - pw) // 2, (ch - ph) // 2

            if position == "bottom":
                y = ch - ph - 50
            elif position == "bottom_left":
                x = 50
                y = ch - ph - 50
            elif position == "bottom_right":
                x = cw - pw - 50
                y = ch - ph - 50

            final_comp = bg_img.copy()
            final_comp.paste(img_pil, (x, y), img_pil)

            mask = Image.new("L", CANVAS_SIZE, 255)
            product_mask = Image.new("L", img_pil.size, 0)
            for px in range(img_pil.width):
                for py in range(img_pil.height):
                    if img_pil.getpixel((px, py))[3] > 0:
                        product_mask.putpixel((px, py), 0)
                    else:
                        product_mask.putpixel((px, py), 255)
            mask.paste(product_mask, (x, y), img_pil)

            base_io = io.BytesIO()
            final_comp.save(base_io, format="PNG")
            mask_io = io.BytesIO()
            mask.save(mask_io, format="PNG")

            return base_io.getvalue(), mask_io.getvalue()

        except Exception as e:
            return str(e), None
