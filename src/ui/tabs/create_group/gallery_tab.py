import flet as ft
from src.core.history_manager import (
    load_history,
    delete_history_item,
    clear_all_history,
)
from src.core.styles import AppStyle
from src.ui.components.toast import CustomToast
from src.ui.components.prompt_box import PromptBox
from src.logic.zip_manager import create_zip_from_history_item


class GalleryTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.toast = CustomToast(page)
        self.item_to_delete = None
        self.item_to_zip = None

        # เก็บ References ของ Card ไว้เพื่อลบเฉพาะจุดได้ {history_id: card_control}
        self.cards_map = {}

        # 1. สร้าง Picker
        self.save_zip_picker = ft.FilePicker(on_result=self.on_save_zip_result)
        self.page.overlay.append(self.save_zip_picker)

        self.history_list = ft.Column(spacing=20)
        self.no_data_text = ft.Text(
            "ยังไม่มีประวัติการสร้าง", size=16, color=AppStyle.TEXT_SECONDARY
        )

        self.clear_btn = ft.ElevatedButton(
            "Clear All",
            icon=AppStyle.ICON_DELETE,
            style=ft.ButtonStyle(bgcolor=AppStyle.BTN_DANGER, color="onError"),
            on_click=self.show_clear_all_dialog,
        )
        self.refresh_btn = ft.IconButton(
            icon=AppStyle.ICON_REFRESH,
            tooltip="โหลดข้อมูลใหม่",
            icon_color=AppStyle.BTN_PRIMARY,
            on_click=lambda _: self.refresh_gallery(force=True),
        )

        self.controls = [
            ft.Container(height=10),
            ft.Row(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "History Gallery", size=24, weight=ft.FontWeight.BOLD
                            ),
                            self.refresh_btn,
                        ]
                    ),
                    self.clear_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(),
            self.history_list,
        ]

        # Dialogs
        self.delete_confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ยืนยันการลบ"),
            content=ft.Text("คุณต้องการลบรายการนี้ใช่หรือไม่?"),
            actions=[
                ft.TextButton("ยกเลิก", on_click=self.close_dialog),
                ft.TextButton(
                    "ลบ",
                    on_click=self.confirm_delete_item,
                    style=ft.ButtonStyle(color=AppStyle.BTN_DANGER),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.clear_all_confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ยืนยันการลบทั้งหมด"),
            content=ft.Text("ประวัติทั้งหมดจะหายไปและกู้คืนไม่ได้ ยืนยันหรือไม่?"),
            actions=[
                ft.TextButton("ยกเลิก", on_click=self.close_dialog),
                ft.TextButton(
                    "ลบทั้งหมด",
                    on_click=self.confirm_clear_all,
                    style=ft.ButtonStyle(color=AppStyle.BTN_DANGER),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def did_mount(self):
        self.refresh_gallery(force=True)
        self.page.pubsub.subscribe(self.on_message)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_all()

    def on_message(self, message):
        if message == "refresh_gallery":
            # โหลดแบบเงียบๆ ไม่ต้อง Force Clear
            self.refresh_gallery(force=False)

    def refresh_gallery(self, force=False):
        """
        Smart Refresh:
        - force=True: ลบทุกอย่างแล้วโหลดใหม่ (ใช้ตอนเปิดแอพ หรือกดปุ่ม Refresh)
        - force=False: (ใช้ตอน Auto Update) จะเช็คก่อนว่ามีอะไรใหม่ไหม ถ้ามีแค่เพิ่มเข้าไป
        """
        data = load_history()

        if not data:
            self.history_list.controls.clear()
            self.history_list.controls.append(
                ft.Container(
                    content=self.no_data_text, alignment=ft.alignment.center, padding=50
                )
            )
            self.cards_map = {}
            self.update()
            return

        # เอา Text "ไม่มีข้อมูล" ออก ถ้ามีข้อมูลมาแล้ว
        if len(self.history_list.controls) == 1 and isinstance(
            self.history_list.controls[0].content, ft.Text
        ):
            self.history_list.controls.clear()

        if force:
            # แบบเดิม: ลบสร้างใหม่หมด (อาจกระพริบ แต่ชัวร์)
            self.history_list.controls.clear()
            self.cards_map = {}
            for item in data:
                self.add_card_to_ui(item)
        else:
            # แบบใหม่: Smart Add (เพิ่มเฉพาะตัวที่ยังไม่มี)
            # data[0] คือตัวใหม่สุด
            # เช็คว่า ID ของตัวใหม่สุด มีอยู่ใน UI หรือยัง
            newest_item = data[0]
            if newest_item["id"] not in self.cards_map:
                # ถ้ายังไม่มี ให้แทรกไว้บนสุด (index 0)
                self.add_card_to_ui(newest_item, index=0)

        self.update()

    def add_card_to_ui(self, item, index=None):
        card = self.create_history_card(item)
        self.cards_map[item["id"]] = card  # จำไว้ว่า ID นี้คือ Card ใบไหน

        if index is not None:
            self.history_list.controls.insert(index, card)
        else:
            self.history_list.controls.append(card)

    def create_history_card(self, item):
        prompts_col = ft.Column()
        img_map = {}
        if "generated_images" in item:
            for img in item["generated_images"]:
                img_map[img["index"]] = img["path"]

        for i, p in enumerate(item["prompts"]):
            idx = i + 1
            pbox = PromptBox(self.page, prompt_text=p, index=idx)
            if idx in img_map:
                try:
                    with open(img_map[idx], "rb") as f:
                        img_bytes = f.read()
                        pbox.set_image(img_bytes, run_update=False)
                except:
                    pass
            prompts_col.controls.append(pbox)

        # Badges
        model_badges = [
            ft.Container(
                content=ft.Text(
                    f"Text: {item.get('model', 'Unknown')}",
                    size=10,
                    color="onSecondaryContainer",
                ),
                bgcolor="secondaryContainer",
                padding=5,
                border_radius=5,
            )
        ]
        if item.get("image_model"):
            model_badges.append(
                ft.Container(
                    content=ft.Text(
                        f"Img: {item['image_model']}",
                        size=10,
                        color="onTertiaryContainer",
                    ),
                    bgcolor="tertiaryContainer",
                    padding=5,
                    border_radius=5,
                )
            )

        card = ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.ACCESS_TIME,
                                            size=16,
                                            color=AppStyle.TEXT_SECONDARY,
                                        ),
                                        ft.Text(
                                            item["timestamp"],
                                            color=AppStyle.TEXT_SECONDARY,
                                            size=12,
                                        ),
                                        ft.Container(width=5),
                                        *model_badges,
                                    ]
                                ),
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            ft.Icons.FOLDER_ZIP,
                                            icon_color=AppStyle.BTN_PRIMARY,
                                            tooltip="Download Project ZIP",
                                            on_click=lambda e: self.download_project_zip(
                                                item
                                            ),
                                        ),
                                        ft.IconButton(
                                            AppStyle.ICON_DELETE,
                                            icon_color=AppStyle.BTN_DANGER,
                                            tooltip="ลบรายการนี้",
                                            on_click=lambda e: self.show_delete_dialog(
                                                item["id"]
                                            ),
                                        ),
                                    ]
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            (
                                f"Input: {item['input_text']}"
                                if item["input_text"]
                                else "Input: (No Text)"
                            ),
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=10),
                        ft.ExpansionTile(
                            title=ft.Text(
                                f"View {len(item['prompts'])} Prompts & Images",
                                color=AppStyle.BTN_PRIMARY,
                            ),
                            controls=[prompts_col],
                            initially_expanded=False,
                        ),
                    ]
                ),
            )
        )
        return card

    # ... (Zip Logic เหมือนเดิม) ...
    def download_project_zip(self, item):
        self.item_to_zip = item
        filename = f"project_{item['id']}.zip"
        self.save_zip_picker.save_file(file_name=filename, allowed_extensions=["zip"])

    def on_save_zip_result(self, e):
        if e.path and self.item_to_zip:
            success, msg = create_zip_from_history_item(e.path, self.item_to_zip)
            self.toast.show(msg, is_error=not success)
            self.item_to_zip = None

    # --- Optimize Delete Logic ---
    def close_dialog(self, e):
        self.page.close(self.delete_confirm_dialog)
        self.page.close(self.clear_all_confirm_dialog)

    def show_delete_dialog(self, item_id):
        self.item_to_delete = item_id
        self.page.open(self.delete_confirm_dialog)

    def confirm_delete_item(self, e):
        """ลบแบบ Smart Remove (ไม่โหลดใหม่ทั้งหน้า)"""
        target_id = self.item_to_delete
        if target_id:
            # 1. ลบจาก Database/File
            delete_history_item(target_id)

            # 2. ลบเฉพาะ Card นั้นออกจาก UI (ไม่ต้อง refresh_gallery ทั้งหมด)
            if target_id in self.cards_map:
                card_to_remove = self.cards_map[target_id]
                try:
                    self.history_list.controls.remove(card_to_remove)
                    del self.cards_map[target_id]  # ลบออกจาก Map ด้วย

                    # ถ้าลบจนหมดเกลี้ยง ให้โชว์ Text ว่าง
                    if not self.history_list.controls:
                        self.history_list.controls.append(
                            ft.Container(
                                content=self.no_data_text,
                                alignment=ft.alignment.center,
                                padding=50,
                            )
                        )

                    self.history_list.update()  # อัปเดตแค่ List
                    self.toast.show("ลบรายการเรียบร้อย")
                except ValueError:
                    # กันเหนียวเผื่อหาไม่เจอจริงๆ ค่อยโหลดใหม่
                    self.refresh_gallery(force=True)
            else:
                self.refresh_gallery(force=True)

        self.page.close(self.delete_confirm_dialog)

    def show_clear_all_dialog(self, e):
        self.page.open(self.clear_all_confirm_dialog)

    def confirm_clear_all(self, e):
        clear_all_history()
        self.history_list.controls.clear()
        self.cards_map = {}
        self.history_list.controls.append(
            ft.Container(
                content=self.no_data_text, alignment=ft.alignment.center, padding=50
            )
        )
        self.history_list.update()
        self.toast.show("ลบประวัติทั้งหมดเรียบร้อย")
        self.page.close(self.clear_all_confirm_dialog)
