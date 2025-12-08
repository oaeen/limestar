"""将 🍋 emoji 转换为纯绿色 favicon"""

from PIL import Image, ImageDraw, ImageFont
import platform

def create_emoji_favicon(output_dir: str):
    """使用系统字体渲染 emoji 为纯绿色 favicon"""

    # Header 使用的绿色: #84cc16 = (132, 204, 22)
    TARGET_COLOR = (132, 204, 22)

    # 根据操作系统选择 emoji 字体
    system = platform.system()
    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/seguiemj.ttf",
            "C:/Windows/Fonts/segoe ui emoji.ttf",
        ]
    elif system == "Darwin":
        font_paths = ["/System/Library/Fonts/Apple Color Emoji.ttc"]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/noto-emoji/NotoColorEmoji.ttf",
        ]

    font_path = None
    for path in font_paths:
        try:
            ImageFont.truetype(path, 100)
            font_path = path
            break
        except:
            continue

    if not font_path:
        font_path = "seguiemj.ttf"

    # 生成大尺寸图片
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, int(size * 0.85))
    except Exception as e:
        print(f"加载字体失败: {e}")
        return

    emoji = "🍋"
    bbox = draw.textbbox((0, 0), emoji, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]
    draw.text((x, y), emoji, font=font, embedded_color=True)

    # 将所有非透明像素转换为纯绿色
    pixels = img.load()
    for py in range(size):
        for px in range(size):
            r, g, b, a = pixels[px, py]
            if a > 0:  # 非透明像素
                # 保持 alpha 通道，颜色改为目标绿色
                pixels[px, py] = (TARGET_COLOR[0], TARGET_COLOR[1], TARGET_COLOR[2], a)

    # 保存不同尺寸
    sizes_to_save = [
        ("favicon-16x16.png", 16),
        ("favicon-32x32.png", 32),
        ("apple-touch-icon.png", 180),
    ]

    for filename, target_size in sizes_to_save:
        resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        resized.save(f"{output_dir}/{filename}", "PNG")
        print(f"Saved {filename}")

    # ICO 文件
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    ico_images = [img.resize(s, Image.Resampling.LANCZOS) for s in ico_sizes]
    ico_images[0].save(
        f"{output_dir}/favicon.ico",
        format="ICO",
        sizes=ico_sizes,
        append_images=ico_images[1:]
    )
    print("Saved favicon.ico")

if __name__ == "__main__":
    create_emoji_favicon("frontend/public")
    print("\nDone!")
