import flet as ft
import asyncio
import requests  # ใช้สำหรับดึงข้อมูลจาก Ollama API

# Logic & Utils
from src.core.key_manager import get_api_keys
from src.core.history_manager import (
    save_to_history,
    update_history_images,
    get_latest_history_id,
)
from src.core.styles import AppStyle
from src.logic.zip_manager import create_images_zip, create_project_zip

# Providers
from src.logic.providers.gemini_provider import GeminiProvider
from src.logic.image_providers.gemini_image import GeminiImageProvider
from src.logic.image_providers.pollinations import PollinationsProvider
from src.logic.providers.ollama_provider import OllamaProvider

# Components & Parts
from src.ui.components.toast import CustomToast
from src.ui.components.prompt_box import PromptBox
from src.ui.tabs.parts.input_part import InputPart
from src.ui.tabs.parts.config_part import ConfigPart
from src.core.config import AI_MODELS_MAP, IMAGE_GEN_MODELS_MAP
from src.core.ollama_manager import load_ollama_settings


class CreateTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO

        # Init Services
        self.gemini_provider = GeminiProvider()
        self.ollama_provider = OllamaProvider()
        self.gemini_image_provider = GeminiImageProvider()
        self.pollinations_provider = PollinationsProvider()
        self.toast = CustomToast(page)
        self.current_history_id = None

        # --- Instantiate UI Parts ---
        self.input_part = InputPart(page, self.on_file_picked)
        self.config_part = ConfigPart(self.on_click_generate, self.on_click_gen_images)

        # Zip Pickers
        self.save_all_images_picker = ft.FilePicker(
            on_result=self.on_save_all_images_result
        )
        self.save_project_zip_picker = ft.FilePicker(
            on_result=self.on_save_project_zip_result
        )

        # Output Section
        self.download_all_btn = ft.ElevatedButton(
            "Download Images (ZIP)",
            icon=ft.Icons.PHOTO_LIBRARY,
            on_click=lambda _: self.save_all_images_picker.save_file(
                "images.zip", allowed_extensions=["zip"]
            ),
            visible=False,
        )
        self.download_project_btn = ft.ElevatedButton(
            "Download Project (ZIP)",
            icon=ft.Icons.FOLDER_ZIP,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_PRIMARY, color=AppStyle.BTN_ON_PRIMARY
            ),
            on_click=lambda _: self.save_project_zip_picker.save_file(
                "project.zip", allowed_extensions=["zip"]
            ),
            visible=False,
        )

        self.progress_bar = ft.ProgressBar(visible=False, color=AppStyle.LOADING)
        self.status_text = ft.Text("", color=AppStyle.TEXT_SECONDARY)
        self.output_list = ft.Column(spacing=15)

        # --- Layout Assembly ---
        self.controls = [
            ft.Container(height=10),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        [
                            self.input_part,
                            ft.Divider(height=30),
                            self.config_part,
                            ft.Container(height=15),
                            self.progress_bar,
                            ft.Container(
                                content=self.status_text, alignment=ft.alignment.center
                            ),
                        ]
                    ),
                )
            ),
            ft.Container(height=20),
            ft.Row(
                [
                    ft.Text("Generated Results", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([self.download_all_btn, self.download_project_btn]),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            self.output_list,
            ft.Container(height=50),
        ]

    def did_mount(self):
        # Add Overlay logic
        self.page.overlay.extend(
            [
                self.input_part.file_picker,
                self.save_all_images_picker,
                self.save_project_zip_picker,
            ]
        )
        self.page.update()

        # Optional: โหลดครั้งแรกตอนเปิดแอพเลยก็ได้
        # self.update_models(is_silent=True)

    # --- UPDATED METHOD: รองรับ Silent Update ---
    def update_models(self, is_silent=True):
        """
        โหลดรายชื่อโมเดลจาก Settings (ที่ติ๊กเลือกไว้) มาแสดง
        """
        current_provider = self.config_part.provider_dropdown.value

        if "Ollama" in current_provider:
            # 1. โหลด Config
            settings = load_ollama_settings()
            selected_models = settings.get("selected_models", [])

            if selected_models:
                # ถ้ามีการเลือกไว้ ให้เอามาใส่ Dropdown เลย
                self.config_part.model_dropdown.options = [
                    ft.dropdown.Option(m) for m in selected_models
                ]

                # เช็ค value ปัจจุบัน
                if self.config_part.model_dropdown.value not in selected_models:
                    self.config_part.model_dropdown.value = selected_models[0]

                self.config_part.model_dropdown.update()

                if not is_silent:
                    print(f"Loaded {len(selected_models)} models from settings.")

            else:
                # ถ้าใน Config เป็น List ว่างเปล่า (ผู้ใช้ยังไม่เคยไปติ๊ก)
                # ให้แสดงข้อความเตือน หรือใส่ Option ว่างๆ ไว้
                if not is_silent:
                    self.toast.show("ยังไม่ได้เลือกโมเดลในหน้า Settings", is_error=True)

                # Optional: Fallback ไปดึงสด (ถ้าต้องการ) แต่ตามโจทย์คือให้เลือกเอง
                # self.config_part.model_dropdown.options = []
                # self.config_part.model_dropdown.update()

        else:
            pass  # Provider อื่นไม่ต้องทำอะไร

    # --- Event Logic ---
    def on_file_picked(self, e):
        if e.files:
            self.input_part.update_preview(e.files)

    # Step 1: Text Gen
    async def on_click_generate(self, e):
        selected_provider = self.config_part.provider_dropdown.value

        if (
            not self.input_part.selected_files
            and not self.input_part.prompt_input.value
        ):
            self.toast.show("ต้องใส่รูปหรือข้อความอย่างน้อย 1 อย่าง", is_error=True)
            return

        self.set_loading(True, f"Generating with {selected_provider}...")
        self.config_part.generate_image_btn.visible = False
        self.download_all_btn.visible = False
        self.download_project_btn.visible = False
        self.output_list.controls.clear()
        self.update()

        try:
            # CASE A: Google
            if "Google" in selected_provider:
                keys = get_api_keys()
                api_key = keys.get("gemini_text_key")
                if not api_key:
                    raise ValueError("ไม่พบ Text API Key")
                self.gemini_provider.set_api_key(api_key)
                prompts = await self.gemini_provider.generate_prompts_from_image(
                    model_name=self.config_part.model_dropdown.value,
                    image_paths=self.input_part.selected_files,
                    user_input=self.input_part.prompt_input.value,
                    style=self.input_part.style_dropdown.value,
                    ratio=self.input_part.ratio_dropdown.value,
                    count=int(self.config_part.count_slider.value),
                )

            # CASE B: Ollama
            elif "Ollama" in selected_provider:
                settings = load_ollama_settings()
                self.ollama_provider.base_url = settings.get(
                    "base_url", "http://localhost:11434"
                )
                prompts = await self.ollama_provider.generate_prompts_from_image(
                    model=self.config_part.model_dropdown.value,
                    image_paths=self.input_part.selected_files,
                    user_input=self.input_part.prompt_input.value,
                    style=self.input_part.style_dropdown.value,
                    ratio=self.input_part.ratio_dropdown.value,
                    count=int(self.config_part.count_slider.value),
                )
            else:
                raise ValueError("Provider ไม่ถูกต้อง")

            # Common Output
            if not prompts or (len(prompts) == 1 and "Error" in prompts[0]):
                raise ValueError(prompts[0] if prompts else "No response")

            for i, p in enumerate(prompts):
                self.output_list.controls.append(PromptBox(self.page, p, i + 1))

            self.current_history_id = save_to_history(
                selected_provider,
                self.config_part.model_dropdown.value,
                self.input_part.prompt_input.value,
                self.input_part.selected_files,
                prompts,
            )
            self.page.pubsub.send_all("refresh_gallery")
            self.toast.show(f"สร้างสำเร็จ {len(prompts)} รายการ")
            self.config_part.generate_image_btn.visible = True

        except Exception as err:
            self.toast.show(f"Error: {err}", is_error=True)
            self.status_text.value = "Generation Failed"
        finally:
            self.set_loading(False)

    # Step 2: Image Gen
    async def on_click_gen_images(self, e):
        prompt_boxes = [
            c for c in self.output_list.controls if isinstance(c, PromptBox)
        ]
        if not prompt_boxes:
            return

        keys = get_api_keys()
        provider_name = self.config_part.img_provider_dropdown.value
        active_provider = None

        if "Google" in provider_name:
            if not keys.get("gemini_image_key"):
                self.toast.show("ไม่พบ Image API Key", is_error=True)
                return
            self.gemini_image_provider.set_api_key(keys.get("gemini_image_key"))
            active_provider = self.gemini_image_provider
        else:
            active_provider = self.pollinations_provider

        self.set_loading(True, "Generating Images...")
        self.update()

        tasks = []
        for i, box in enumerate(prompt_boxes):
            tasks.append(
                self.generate_single_image(
                    provider=active_provider,
                    prompt_box=box,
                    model=self.config_part.img_model_dropdown.value,
                    index=i + 1,
                )
            )

        await asyncio.gather(*tasks)
        self.set_loading(False)
        self.toast.show("สร้างรูปภาพครบแล้ว!")
        self.download_all_btn.visible = True
        self.download_project_btn.visible = True
        self.update()

    async def generate_single_image(self, provider, prompt_box, model, index=0):
        try:
            result = await provider.generate_image(
                prompt=prompt_box.prompt_text,
                model=model,
                ref_image_paths=self.input_part.selected_files,
                ratio=self.input_part.ratio_dropdown.value,
            )

            if isinstance(result, bytes):
                prompt_box.set_image(result)
                target_id = self.current_history_id
                if not target_id:
                    target_id = get_latest_history_id()
                if target_id:
                    update_history_images(target_id, index, result, image_model=model)
                    self.page.pubsub.send_all("refresh_gallery")
            elif isinstance(result, str):
                prompt_box.set_error(result)
        except Exception as e:
            print(f"Gen Error: {e}")
            prompt_box.set_error(f"App Error: {str(e)}")

    # Helpers
    def set_loading(self, is_loading, text=""):
        self.config_part.generate_text_btn.disabled = is_loading
        self.config_part.generate_image_btn.disabled = is_loading
        self.progress_bar.visible = is_loading
        self.status_text.value = text if is_loading else ""
        self.update()

    def on_save_all_images_result(self, e):
        if not e.path:
            return
        prompt_boxes = [
            c for c in self.output_list.controls if isinstance(c, PromptBox)
        ]
        success, msg = create_images_zip(e.path, prompt_boxes)
        self.toast.show(msg, is_error=not success)

    def on_save_project_zip_result(self, e):
        if not e.path:
            return
        prompt_boxes = [
            c for c in self.output_list.controls if isinstance(c, PromptBox)
        ]
        success, msg = create_project_zip(
            e.path, prompt_boxes, self.input_part.selected_files
        )
        self.toast.show(msg, is_error=not success)
