import os
from PIL import Image, ImageDraw, ImageFont

def generate_dmg_background():
    build_dir = os.path.dirname(os.path.abspath(__file__))
    width = 660
    height = 400

    # 1x Background Image
    img = Image.new("RGB", (width, height), (13, 16, 23))
    draw = ImageDraw.Draw(img)

    # Subtle gradient top border
    for y in range(4):
        alpha = int(255 * (1 - y/4))
        # Draw gradient from Red (left) to Cyan (right)
        for x in range(width):
            r = int(255 * (1 - x/width))
            g = int(229 * (x/width))
            b = int(255 * (x/width))
            draw.point((x, y), fill=(r, g, b))

    # Inner decorative rounded card
    draw.rounded_rectangle(
        [20, 20, width - 20, height - 20],
        radius=16,
        outline=(255, 255, 255, 25),
        width=1
    )

    # App Title Header
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/SFProText-Bold.otf", 20)
        font_sub = ImageFont.truetype("/System/Library/Fonts/SFProText-Regular.otf", 13)
        font_arrow = ImageFont.truetype("/System/Library/Fonts/SFProText-Bold.otf", 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_arrow = ImageFont.load_default()

    title_text = "YouTube Playlist Downloader"
    draw.text((width // 2, 48), title_text, fill=(248, 250, 252), font=font_title, anchor="mm")

    sub_text = "Drag and drop the app into Applications to install"
    draw.text((width // 2, 340), sub_text, fill=(148, 163, 184), font=font_sub, anchor="mm")

    # Center Drag & Drop Arrow Graphic
    arrow_y = 190
    start_x = 240
    end_x = 420

    # Gradient line
    for x in range(start_x, end_x):
        t = (x - start_x) / (end_x - start_x)
        r = int(255 * (1 - t) + 0 * t)
        g = int(0 * (1 - t) + 229 * t)
        b = int(51 * (1 - t) + 255 * t)
        for dy in range(-3, 4):
            draw.point((x, arrow_y + dy), fill=(r, g, b))

    # Arrow head pointing right
    arrow_head = [
        (end_x + 16, arrow_y),
        (end_x - 4, arrow_y - 12),
        (end_x - 4, arrow_y + 12)
    ]
    draw.polygon(arrow_head, fill=(0, 229, 255))

    # Glowing subtle rings for where icons sit
    draw.ellipse([100, 130, 220, 250], outline=(255, 0, 51, 60), width=2)
    draw.ellipse([440, 130, 560, 250], outline=(0, 229, 255, 60), width=2)

    bg_path = os.path.join(build_dir, "dmg_background.png")
    img.save(bg_path, "PNG")

    # Also save 2x retina version
    img_2x = img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    bg_2x_path = os.path.join(build_dir, "dmg_background@2x.png")
    img_2x.save(bg_2x_path, "PNG")

    print(f"DMG Background generated at: {bg_path}")
    return bg_path

if __name__ == "__main__":
    generate_dmg_background()
