import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def create_app_icon():
    build_dir = os.path.dirname(os.path.abspath(__file__))
    iconset_dir = os.path.join(build_dir, "AppIcon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    # Base high-res 1024x1024 icon
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle background with rich gradient
    # Deep obsidian with YouTube Red & Cyan gradient ring
    margin = 40
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=220,
        fill=(14, 18, 28, 255),
        outline=(255, 0, 51, 230),
        width=16
    )

    # Subtle inner glow
    draw.rounded_rectangle(
        [margin + 20, margin + 20, size - margin - 20, size - margin - 20],
        radius=200,
        outline=(0, 229, 255, 120),
        width=6
    )

    # YouTube Play & Music Icon in center
    # YouTube Red Play Button
    center_x, center_y = size // 2, size // 2
    poly = [
        (center_x - 120, center_y - 180),
        (center_x + 190, center_y),
        (center_x - 120, center_y + 180)
    ]
    draw.polygon(poly, fill=(255, 0, 51, 255))

    # Cyan download arrow badge
    arrow_poly = [
        (center_x + 180, center_y + 100),
        (center_x + 290, center_y + 100),
        (center_x + 290, center_y + 200),
        (center_x + 350, center_y + 200),
        (center_x + 235, center_y + 320),
        (center_x + 120, center_y + 200),
        (center_x + 180, center_y + 200),
    ]
    draw.polygon(arrow_poly, fill=(0, 229, 255, 255), outline=(14, 18, 28, 255))

    # Icon sizes needed for macOS .icns
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(os.path.join(iconset_dir, f"icon_{s}x{s}.png"))
        if s * 2 in sizes:
            resized_2x = img.resize((s * 2, s * 2), Image.Resampling.LANCZOS)
            resized_2x.save(os.path.join(iconset_dir, f"icon_{s}x{s}@2x.png"))

    icns_path = os.path.join(build_dir, "AppIcon.icns")
    # Convert iconset to .icns using macOS native iconutil
    subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
    return icns_path

if __name__ == "__main__":
    path = create_app_icon()
    print(f"Generated icns at: {path}")
