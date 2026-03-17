#!/usr/bin/env python3
"""Generate AudioForge app icons for macOS, Windows, and Linux."""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def squircle_mask(size: int, radius_factor: float = 0.225) -> Image.Image:
    """Create a macOS-style continuous squircle (superellipse) mask.

    Uses the superellipse formula |x|^n + |y|^n = 1 with n≈4.5
    which closely matches Apple's icon shape.
    """
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)

    n = 4.5  # Superellipse exponent (Apple uses ~4-5)
    half = size / 2
    r = half * (1 - 0.01)  # Slight inset to avoid edge aliasing

    for y in range(size):
        for x in range(size):
            nx = abs((x - half) / r)
            ny = abs((y - half) / r)
            if nx == 0 and ny == 0:
                mask.putpixel((x, y), 255)
            elif (nx ** n + ny ** n) <= 1.0:
                # Anti-alias the edge
                dist = nx ** n + ny ** n
                if dist > 0.97:
                    alpha = int(255 * (1.0 - (dist - 0.97) / 0.03))
                    mask.putpixel((x, y), max(0, min(255, alpha)))
                else:
                    mask.putpixel((x, y), 255)

    return mask


def draw_icon(size: int) -> Image.Image:
    """Draw the AudioForge icon at the given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # Background gradient: deep navy to dark teal
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)

    for y in range(size):
        t = y / size
        # Top: #1b1f3b (dark navy)  →  Bottom: #0c2e3d (dark teal)
        r = int(27 + (12 - 27) * t)
        g = int(31 + (46 - 31) * t)
        b = int(59 + (61 - 59) * t)
        bg_draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Apply squircle mask
    mask = squircle_mask(size)
    bg.putalpha(mask)
    img = Image.alpha_composite(img, bg)

    # Subtle top highlight for depth (macOS-style lighting)
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for y in range(size // 4):
        t = y / (size // 4)
        alpha = int(18 * (1 - t))  # Subtle: max 18/255 opacity
        glow_draw.line([(0, y), (size, y)], fill=(255, 255, 255, alpha))
    # Multiply glow alpha with squircle mask (don't replace)
    glow_alpha = glow.getchannel("A")
    from PIL import ImageChops
    clipped_alpha = ImageChops.multiply(glow_alpha, mask)
    glow.putalpha(clipped_alpha)
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2
    scale = size / 1024  # Design at 1024, scale everything

    # Shift waveform area up a bit to make room for text
    wave_cy = int(cy - 50 * scale)

    # --- Draw audio waveform bars (left side — input) ---
    bar_color_left = (90, 190, 255, 240)  # Cyan-blue
    bar_width = int(30 * scale)
    bar_gap = int(46 * scale)
    bar_x_start = int(155 * scale)
    bar_heights = [0.28, 0.58, 0.88, 0.68, 0.38]

    max_bar_h = int(320 * scale)

    for i, h_pct in enumerate(bar_heights):
        x = bar_x_start + i * bar_gap
        h = int(max_bar_h * h_pct)
        y1 = wave_cy - h // 2
        y2 = wave_cy + h // 2
        r = bar_width // 2
        draw.rounded_rectangle(
            [x, y1, x + bar_width, y2],
            radius=r,
            fill=bar_color_left,
        )

    # --- Draw arrow (conversion symbol) — larger and bolder ---
    arrow_color = (255, 255, 255, 220)
    arrow_cx = int(cx + 8 * scale)
    arrow_cy = wave_cy
    shaft_len = int(100 * scale)
    shaft_thick = int(14 * scale)
    head_w = int(50 * scale)
    head_h = int(38 * scale)

    # Shaft
    shaft_left = arrow_cx - shaft_len // 2
    shaft_right = arrow_cx + shaft_len // 2 - head_w // 3
    draw.rounded_rectangle(
        [shaft_left, arrow_cy - shaft_thick // 2,
         shaft_right, arrow_cy + shaft_thick // 2],
        radius=shaft_thick // 2,
        fill=arrow_color,
    )

    # Chevron head
    tip_x = arrow_cx + shaft_len // 2 + int(10 * scale)
    base_x = tip_x - head_w
    draw.polygon(
        [
            (tip_x, arrow_cy),
            (base_x, arrow_cy - head_h),
            (base_x, arrow_cy + head_h),
        ],
        fill=arrow_color,
    )

    # --- Draw output waveform bars (right side — output) ---
    bar_color_right = (255, 165, 70, 240)  # Warm amber-orange
    bar_x_start_r = int(590 * scale)
    bar_heights_r = [0.32, 0.68, 0.92, 0.68, 0.32]  # Symmetric = "clean"

    for i, h_pct in enumerate(bar_heights_r):
        x = bar_x_start_r + i * bar_gap
        h = int(max_bar_h * h_pct)
        y1 = wave_cy - h // 2
        y2 = wave_cy + h // 2
        r = bar_width // 2
        draw.rounded_rectangle(
            [x, y1, x + bar_width, y2],
            radius=r,
            fill=bar_color_right,
        )

    # --- Accent line above text ---
    line_y = int(cy + 175 * scale)
    line_half = int(140 * scale)
    accent_color = (90, 190, 255, 80)
    draw.rounded_rectangle(
        [int(cx - line_half), line_y, int(cx + line_half), line_y + int(3 * scale)],
        radius=int(2 * scale),
        fill=accent_color,
    )

    # --- "FORGE" text ---
    text_color = (255, 255, 255, 200)
    font_size = int(100 * scale)

    font = None
    font_candidates = [
        "/System/Library/Fonts/SFCompact.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for fp in font_candidates:
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except (OSError, IOError):
            continue
    if font is None:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    text = "FORGE"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    text_x = (size - tw) / 2
    text_y = int(cy + 195 * scale)
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    return img


def generate_macos_iconset(base_icon: Image.Image, output_dir: Path):
    """Generate .iconset folder with all required sizes for macOS."""
    iconset_dir = output_dir / "AudioForge.iconset"
    iconset_dir.mkdir(parents=True, exist_ok=True)

    # macOS iconset requires these exact sizes and naming
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for px, filename in sizes:
        resized = base_icon.resize((px, px), Image.LANCZOS)
        resized.save(iconset_dir / filename, "PNG")

    return iconset_dir


def generate_ico(base_icon: Image.Image, output_path: Path):
    """Generate .ico file with multiple sizes for Windows."""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    icons = []
    for s in sizes:
        icons.append(base_icon.resize((s, s), Image.LANCZOS))

    icons[0].save(
        output_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=icons[1:],
    )


def main():
    assets_dir = Path(__file__).parent.parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    print("Generating 1024x1024 base icon...")
    icon = draw_icon(1024)
    icon.save(assets_dir / "icon.png", "PNG")
    print(f"  Saved: {assets_dir / 'icon.png'}")

    print("Generating macOS .iconset...")
    iconset_dir = generate_macos_iconset(icon, assets_dir)
    print(f"  Saved: {iconset_dir}")

    print("Generating Windows .ico...")
    generate_ico(icon, assets_dir / "icon.ico")
    print(f"  Saved: {assets_dir / 'icon.ico'}")

    print("\nTo create .icns (macOS), run:")
    print(f"  iconutil -c icns {iconset_dir} -o {assets_dir / 'icon.icns'}")


if __name__ == "__main__":
    main()
