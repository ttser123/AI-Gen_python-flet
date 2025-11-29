import flet as ft
from src.core.history_manager import (
    load_history,
    delete_history_item,
    clear_all_history,
)
from src.ui.components.toast import CustomToast
from src.ui.components.prompt_box import PromptBox
from src.core.styles import AppStyle  # Import


class GalleryTab(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.toast = CustomToast(page)
        self.item_to_delete = None

        self.history_list = ft.Column(spacing=20)
        self.no_data_text = ft.Text(
            "ยังไม่มีประวัติการสร้าง", size=16, color=AppStyle.TEXT_SECONDARY
        )

        self.clear_btn = ft.ElevatedButton(
            "Clear All",
            icon=AppStyle.ICON_DELETE,
            style=ft.ButtonStyle(
                bgcolor=AppStyle.BTN_DANGER,  # สีแดง Error
                color="onError",  # ตัวหนังสือบนสีแดง
            ),
            on_click=self.show_clear_all_dialog,
        )

        self.refresh_btn = ft.IconButton(
            icon=AppStyle.ICON_REFRESH,
            tooltip="โหลดข้อมูลใหม่",
            icon_color=AppStyle.BTN_PRIMARY,  # สี Primary
            on_click=lambda _: self.refresh_gallery(),
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

        # ... (Dialogs Code เหมือนเดิม ไม่ต้องแก้) ...
        self.delete_confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ยืนยันการลบ"),
            content=ft.Text("คุณต้องการลบรายการนี้ใช่หรือไม่?"),
            actions=[
                ft.TextButton("ยกเลิก", on_click=self.close_dialog),  # สี default
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

    # ... (Logic เหมือนเดิม) ...
    def did_mount(self):
        self.refresh_gallery()

    def refresh_gallery(self):
        self.history_list.controls.clear()
        data = load_history()
        if not data:
            self.history_list.controls.append(
                ft.Container(
                    content=self.no_data_text, alignment=ft.alignment.center, padding=50
                )
            )
        else:
            for item in data:
                self.history_list.controls.append(self.create_history_card(item))
        self.update()

    def create_history_card(self, item):
        prompts_col = ft.Column()
        for i, p in enumerate(item["prompts"]):
            prompts_col.controls.append(
                PromptBox(self.page, prompt_text=p, index=i + 1)
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
                                        ft.Container(width=10),
                                        ft.Container(
                                            content=ft.Text(
                                                item["model"],
                                                size=10,
                                                color="onSecondaryContainer",
                                            ),
                                            bgcolor="secondaryContainer",  # สีพื้นหลัง Tag
                                            padding=5,
                                            border_radius=5,
                                        ),
                                    ]
                                ),
                                ft.IconButton(
                                    AppStyle.ICON_DELETE,
                                    icon_color=AppStyle.BTN_DANGER,
                                    tooltip="ลบรายการนี้",
                                    on_click=lambda e: self.show_delete_dialog(
                                        item["id"]
                                    ),
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
                                f"View {len(item['prompts'])} Prompts",
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

    # ... (Dialog Handling functions Copy from previous turn) ...
    def close_dialog(self, e):
        self.page.close(self.delete_confirm_dialog)
        self.page.close(self.clear_all_confirm_dialog)

    def show_delete_dialog(self, item_id):
        self.item_to_delete = item_id
        self.page.open(self.delete_confirm_dialog)

    def confirm_delete_item(self, e):
        if self.item_to_delete:
            delete_history_item(self.item_to_delete)
            self.toast.show("ลบรายการเรียบร้อย")
            self.refresh_gallery()
        self.page.close(self.delete_confirm_dialog)

    def show_clear_all_dialog(self, e):
        self.page.open(self.clear_all_confirm_dialog)

    def confirm_clear_all(self, e):
        clear_all_history()
        self.toast.show("ลบประวัติทั้งหมดเรียบร้อย")
        self.refresh_gallery()
        self.page.close(self.clear_all_confirm_dialog)
