import flet as ft

# กำหนดรายการ Theme ที่มีให้เลือก
# key: ชื่อที่จะบันทึกลงไฟล์
# label: ชื่อที่จะโชว์ใน Dropdown
# mode: Light หรือ Dark
# seed: สีหลักของ Theme (ใส่ None คือใช้สี Default ของ Flet)

THEME_PRESETS = {
    "system_light": {
        "label": "Standard Light",
        "mode": ft.ThemeMode.LIGHT,
        "seed": None,
    },
    "system_dark": {"label": "Standard Dark", "mode": ft.ThemeMode.DARK, "seed": None},
    "forest_green": {
        "label": "Forest Green (Light)",
        "mode": ft.ThemeMode.LIGHT,
        "seed": ft.Colors.GREEN,
    },
    "royal_purple": {
        "label": "Royal Purple (Dark)",
        "mode": ft.ThemeMode.DARK,
        "seed": ft.Colors.PURPLE,
    },
    "cherry_red": {
        "label": "Cherry Red (Light)",
        "mode": ft.ThemeMode.LIGHT,
        "seed": ft.Colors.RED,
    },
    "hacker_green": {
        "label": "Matrix (Dark)",
        "mode": ft.ThemeMode.DARK,
        "seed": ft.Colors.LIME,
    },
}
