import flet as ft


class AppStyle:
    # --- Icons ---
    ICON_COPY = ft.Icons.CONTENT_COPY
    ICON_DELETE = ft.Icons.DELETE_OUTLINE
    ICON_SAVE = ft.Icons.SAVE
    ICON_REFRESH = ft.Icons.REFRESH
    ICON_UPLOAD = ft.Icons.UPLOAD_FILE
    ICON_GENERATE = ft.Icons.AUTO_AWESOME
    ICON_SETTINGS = ft.Icons.SETTINGS
    ICON_IMAGE = ft.Icons.IMAGE

    # --- Semantic Colors (ใช้ String เพื่อให้ Flet จัดการตาม Theme) ---

    # 1. สีพื้นหลังและคอนเทนเนอร์
    BG_SURFACE = "surface"  # พื้นหลังหลัก
    BG_SURFACE_VARIANT = "surfaceVariant"  # พื้นหลังรอง (เช่น Header, Card)

    # 2. สีตัวหนังสือ
    TEXT_PRIMARY = "onSurface"  # ตัวหนังสือหลัก
    TEXT_SECONDARY = "onSurfaceVariant"  # ตัวหนังสือรอง (สีเทาๆ)
    TEXT_INVERSE = "onInverseSurface"  # ตัวหนังสือบนพื้นหลังสีตรงข้าม

    # 3. สีปุ่มและการกระทำ
    BTN_PRIMARY = "primary"  # ปุ่มหลัก (สีเด่นสุด)
    BTN_ON_PRIMARY = "onPrimary"  # ตัวหนังสือบนปุ่มหลัก
    BTN_SECONDARY = "secondaryContainer"  # ปุ่มรอง
    BTN_DANGER = "error"  # ปุ่มลบ/อันตราย

    # 4. สีเส้นขอบ
    BORDER = "outline"  # เส้นขอบชัด
    BORDER_DIM = "outlineVariant"  # เส้นขอบจางๆ

    # *** เพิ่มตัวนี้กลับมาเพื่อแก้ Error ***
    BORDER_COLOR = "outlineVariant"  # ใช้ outlineVariant เป็นค่ามาตรฐานของขอบ

    # 5. สีเฉพาะ Prompt Box
    PROMPT_HEADER_BG = "surfaceVariant"
    PROMPT_BODY_BG = "surface"

    # 6. สถานะ
    SUCCESS = ft.Colors.GREEN
    LOADING = "primary"
