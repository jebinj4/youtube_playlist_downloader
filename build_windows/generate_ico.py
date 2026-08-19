import os
from PIL import Image, ImageDraw

def create_windows_ico():
    build_dir = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(build_dir, "app_icon.ico")
    
    # Try converting existing macOS icon if available
    mac_icon_png = os.path.join(os.path.dirname(build_dir), "build_assets", "dmg_background.png")
    
    # Generate high quality 256x256 app icon
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer dark rounded square
    draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=50, fill=(18, 22, 32), outline=(255, 255, 255, 30), width=4)
    
    # Red inner play button box
    play_box = [50, 68, size - 50, size - 68]
    draw.rounded_rectangle(play_box, radius=32, fill=(229, 9, 20))
    
    # White Play Triangle
    triangle = [
        (108, 96),
        (108, 160),
        (164, 128)
    ]
    draw.polygon(triangle, fill=(255, 255, 255))
    
    # Save multi-resolution .ico
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"✅ Generated Windows Icon at: {ico_path}")
    return ico_path

if __name__ == "__main__":
    create_windows_ico()
