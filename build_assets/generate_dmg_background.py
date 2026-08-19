import os
from PIL import Image, ImageDraw, ImageFont

def generate_dmg_background():
    build_dir = os.path.dirname(os.path.abspath(__file__))
    # 2x Retina resolution for razor-sharp rendering
    width = 660 * 2
    height = 400 * 2

    img = Image.new("RGB", (width, height), (12, 14, 20))
    draw = ImageDraw.Draw(img)

    # 1. Solid Red Top Accent Bar (No gradients)
    draw.rectangle([0, 0, width, 8], fill=(229, 9, 20))

    # 2. Main Outer Card Border
    draw.rounded_rectangle(
        [32, 28, width - 32, height - 28],
        radius=24,
        outline=(255, 255, 255, 20),
        width=2
    )

    # Fonts loader
    def get_font(size, bold=False):
        font_paths = [
            "/System/Library/Fonts/SFPro-Bold.otf" if bold else "/System/Library/Fonts/SFPro-Regular.otf",
            "/System/Library/Fonts/SFProDisplay-Bold.otf" if bold else "/System/Library/Fonts/SFProDisplay-Regular.otf",
            "/System/Library/Fonts/SFProText-Bold.otf" if bold else "/System/Library/Fonts/SFProText-Regular.otf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
        for p in font_paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    font_title = get_font(38, bold=True)
    font_badge = get_font(20, bold=True)
    font_subtitle = get_font(24, bold=False)
    font_arrow = get_font(20, bold=True)
    font_footer_main = get_font(20, bold=True)
    font_footer_sub = get_font(18, bold=False)

    # 3. Header Section
    # Title
    title_text = "YouTube Playlist Downloader"
    draw.text((width // 2, 76), title_text, fill=(255, 255, 255), font=font_title, anchor="mm")

    # Developer Subtitle & Version
    dev_text = "Developed by Just Rise Technologies W.L.L.  •  PRO v2.0 (5x Turbo Engine)"
    draw.text((width // 2, 126), dev_text, fill=(148, 163, 184), font=font_subtitle, anchor="mm")

    # 4. Target Drop Zones (Left: App Icon, Right: Applications Folder)
    # Left Box around (320, 400) in 2x coords
    left_cx, right_cx = 320, 1000
    icon_cy = 400
    box_w, box_h = 230, 230

    # Draw left drop card
    draw.rounded_rectangle(
        [left_cx - box_w//2, icon_cy - box_h//2, left_cx + box_w//2, icon_cy + box_h//2],
        radius=20,
        fill=(18, 22, 32),
        outline=(255, 255, 255, 22),
        width=2
    )

    # Draw right drop card
    draw.rounded_rectangle(
        [right_cx - box_w//2, icon_cy - box_h//2, right_cx + box_w//2, icon_cy + box_h//2],
        radius=20,
        fill=(18, 22, 32),
        outline=(255, 255, 255, 22),
        width=2
    )

    # 5. Center Solid Installation Arrow & Label
    arrow_y = icon_cy - 10
    arr_start_x = left_cx + box_w//2 + 30
    arr_end_x = right_cx - box_w//2 - 30

    # Solid Arrow Stem
    draw.rectangle([arr_start_x, arrow_y - 3, arr_end_x - 14, arrow_y + 3], fill=(229, 9, 20))

    # Arrow Head
    arrow_head = [
        (arr_end_x + 10, arrow_y),
        (arr_end_x - 18, arrow_y - 16),
        (arr_end_x - 18, arrow_y + 16)
    ]
    draw.polygon(arrow_head, fill=(229, 9, 20))

    # "Drag to Install" Text above arrow
    draw.text(((arr_start_x + arr_end_x) // 2, arrow_y - 28), "Drag to Applications to Install", fill=(248, 250, 252), font=font_arrow, anchor="mm")

    # 6. Corporate Footer Section
    divider_y = height - 110
    draw.line([60, divider_y, width - 60, divider_y], fill=(255, 255, 255, 18), width=2)

    # Company & Location
    company_text = "Just Rise Technologies W.L.L.  •  Kingdom of Bahrain 🇧🇭"
    draw.text((width // 2, divider_y + 32), company_text, fill=(241, 245, 249), font=font_footer_main, anchor="mm")

    # Contact Details
    contact_text = "Website: https://justrise.bh   |   Email: info@justrise.bh   |   Phone: +973 33051719"
    draw.text((width // 2, divider_y + 68), contact_text, fill=(148, 163, 184), font=font_footer_sub, anchor="mm")

    # Save 2x Retina & 1x standard images
    bg_2x_path = os.path.join(build_dir, "dmg_background@2x.png")
    img.save(bg_2x_path, "PNG")

    img_1x = img.resize((660, 400), Image.Resampling.LANCZOS)
    bg_1x_path = os.path.join(build_dir, "dmg_background.png")
    img_1x.save(bg_1x_path, "PNG")

    print(f"✅ Generated Retina DMG Background at: {bg_1x_path}")
    return bg_1x_path

if __name__ == "__main__":
    generate_dmg_background()
