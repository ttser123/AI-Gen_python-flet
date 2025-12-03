import flet as ft
import asyncio

# --- UPDATED IMPORTS (ตามโครงสร้างโฟลเดอร์ใหม่) ---
from src.ui.tabs.settings_tab import SettingsTab
from src.ui.tabs.display_tab import DisplayTab

# Import จากโฟลเดอร์ create_group
from src.ui.tabs.create_group.create_tab import CreateTab
from src.ui.tabs.create_group.gallery_tab import GalleryTab

# Import จากโฟลเดอร์ virtual_studio_group
from src.ui.tabs.virtual_studio_group.virtual_studio_tab import VirtualStudioTab


def get_main_layout(page: ft.Page):
    # --- 1. Init All Content Instances ---
    create_tab = CreateTab(page)
    gallery_tab = GalleryTab(page)
    virtual_studio_tab = VirtualStudioTab(page)
    settings_tab = SettingsTab(page)
    display_tab = DisplayTab(page)

    # --- 2. Define Nested Views ---
    view_create_group = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=True,
        divider_color="transparent",
        tabs=[
            ft.Tab(text="Generate", icon=ft.Icons.AUTO_AWESOME, content=create_tab),
            ft.Tab(text="Gallery", icon=ft.Icons.HISTORY, content=gallery_tab),
        ],
    )

    view_studio_group = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=True,
        divider_color="transparent",
        tabs=[
            ft.Tab(
                text="Studio Editor",
                icon=ft.Icons.PHOTO_SIZE_SELECT_LARGE,
                content=virtual_studio_tab,
            ),
        ],
    )

    # --- 3. Content Management ---
    screens = [
        ft.Container(content=view_create_group, visible=True, expand=True),
        ft.Container(content=view_studio_group, visible=False, expand=True),
        ft.Container(content=settings_tab, visible=False, expand=True),
        ft.Container(content=display_tab, visible=False, expand=True),
    ]

    main_content_area = ft.Stack(controls=screens, expand=True)

    # --- 4. State & Logic ---
    sidebar_width_state = [250]

    async def on_nav_change(e):
        idx = e.control.selected_index
        for i, screen in enumerate(screens):
            screen.visible = i == idx
        main_content_area.update()

        if idx == 0 and hasattr(create_tab, "update_models"):
            await asyncio.to_thread(create_tab.update_models)

    def toggle_sidebar(e):
        is_open = sidebar_width_state[0] > 0

        if is_open:
            # สั่งปิดเมนู
            sidebar_width_state[0] = 0
            sidebar_container.width = 0

            # แสดงแถบ Top Bar
            top_bar_container.height = 50
            top_bar_container.opacity = 1
            top_bar_container.visible = True
        else:
            # สั่งเปิดเมนู
            sidebar_width_state[0] = 250
            sidebar_container.width = 250

            # ซ่อนแถบ Top Bar
            top_bar_container.height = 0
            top_bar_container.opacity = 0
            # top_bar_container.visible = False

        page.update()

    # --- 5. UI Components ---

    # 5.1 Sidebar (เมนูด้านซ้าย)
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=72,
        min_extended_width=200,
        extended=True,
        bgcolor="surface",
        leading=ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_LEFT,  # ปิด
                        tooltip="Hide Menu",
                        icon_color="primary",
                        on_click=toggle_sidebar,
                    ),
                    ft.Text("Hide Menu", weight="bold", color="primary"),
                ],
                spacing=5,
            ),
            padding=ft.padding.only(top=10, bottom=10, left=5),
        ),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.BRUSH_OUTLINED,
                selected_icon=ft.Icons.BRUSH,
                label="Create",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CAMERA_ENHANCE_OUTLINED,
                selected_icon=ft.Icons.CAMERA_ENHANCE,
                label="Studio",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_DISPLAY_OUTLINED,
                selected_icon=ft.Icons.SETTINGS_DISPLAY,
                label="Display",
            ),
        ],
        on_change=on_nav_change,
    )

    vertical_divider = ft.VerticalDivider(width=1, thickness=1, color="outlineVariant")

    # Sidebar Container
    sidebar_container = ft.Container(
        width=sidebar_width_state[0],
        content=ft.Row([rail, vertical_divider], spacing=0),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT_CUBIC),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        alignment=ft.alignment.center_left,
    )

    # 5.2 Top Bar (แถบบนสุดที่จะโผล่มาตอนปิดเมนู)
    open_menu_btn = ft.IconButton(
        icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT,  # เปิด
        icon_size=24,
        tooltip="Show Menu",
        on_click=toggle_sidebar,
        icon_color="primary",
    )

    top_bar_container = ft.Container(
        height=0,
        opacity=0,
        visible=False,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        bgcolor="surfaceVariant",
        padding=ft.padding.symmetric(horizontal=10),
        content=ft.Row(
            controls=[open_menu_btn, ft.Text("Open Menu", size=12, color="primary")],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # --- 6. Assembly ---
    right_content_area = ft.Column(
        controls=[top_bar_container, main_content_area], spacing=0, expand=True
    )

    return ft.Row(
        controls=[sidebar_container, right_content_area], expand=True, spacing=0
    )
