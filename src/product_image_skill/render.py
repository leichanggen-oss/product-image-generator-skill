from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from .models import DimensionSpec, SceneConfig


BACKGROUND = (244, 247, 250)
PANEL = (255, 255, 255)
INK = (24, 48, 64)
MUTED = (86, 101, 113)
ACCENT = (31, 132, 214)


def canvas_size(size: str) -> tuple[int, int]:
    width, height = (int(part) for part in size.split("x", 1))
    return width, height


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def rounded_shadow(canvas: Image.Image, box: tuple[int, int, int, int], radius: int = 28) -> None:
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 8, y1 + 12, x2 + 8, y2 + 12), radius=radius, fill=(0, 0, 0, 48))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(shadow)


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width_chars: int, font: ImageFont.ImageFont, fill: tuple[int, int, int], spacing: int = 10) -> None:
    wrapped = "\n".join(textwrap.wrap(text, width=width_chars))
    draw.multiline_text(xy, wrapped, font=font, fill=fill, spacing=spacing)


def render_detail_card(scene: SceneConfig, source: Path, target: Path, size: str) -> None:
    width, height = canvas_size(size)
    image = Image.new("RGBA", (width, height), BACKGROUND + (255,))
    panel_box = (48, 48, width - 48, height - 48)
    rounded_shadow(image, panel_box)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(panel_box, radius=34, fill=PANEL + (255,))

    original = Image.open(source).convert("RGB")
    crop = original.crop(scene.crop)
    image_box = (72, 72, int(width * 0.62), height - 72)
    fitted = ImageOps.fit(crop, (image_box[2] - image_box[0], image_box[3] - image_box[1]), method=Image.Resampling.LANCZOS)
    image.paste(fitted, (image_box[0], image_box[1]))

    text_x = int(width * 0.68)
    title_font = load_font(max(30, width // 25), bold=True)
    body_font = load_font(max(20, width // 48))
    draw.text((text_x, int(height * 0.28)), (scene.title or scene.id).upper(), font=title_font, fill=INK)
    line_y = int(height * 0.28) + int(title_font.size * 1.5 if hasattr(title_font, "size") else 60)
    draw.rounded_rectangle((text_x, line_y, text_x + int(width * 0.16), line_y + 6), radius=3, fill=ACCENT)
    if scene.body:
        draw_wrapped(draw, scene.body, (text_x, line_y + 42), 28, body_font, MUTED, spacing=12)

    target.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(target, quality=92)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], label: str, font: ImageFont.ImageFont) -> None:
    draw.line((start, end), fill=INK, width=3)
    x1, y1 = start
    x2, y2 = end
    cap = 12
    if abs(x2 - x1) >= abs(y2 - y1):
        draw.line((x1, y1 - cap, x1, y1 + cap), fill=INK, width=3)
        draw.line((x2, y2 - cap, x2, y2 + cap), fill=INK, width=3)
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(((x1 + x2 - text_w) / 2, y1 + 18), label, font=font, fill=INK)
    else:
        draw.line((x1 - cap, y1, x1 + cap, y1), fill=INK, width=3)
        draw.line((x2 - cap, y2, x2 + cap, y2), fill=INK, width=3)
        bbox = draw.textbbox((0, 0), label, font=font)
        text_h = bbox[3] - bbox[1]
        draw.text((x1 + 18, (y1 + y2 - text_h) / 2), label, font=font, fill=INK)


def render_dimensions(scene: SceneConfig, source: Path, target: Path, size: str) -> None:
    if scene.dimensions is None:
        raise ValueError("Dimension specification is required")
    dims: DimensionSpec = scene.dimensions
    width, height = canvas_size(size)
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    title_font = load_font(max(38, width // 24), bold=True)
    label_font = load_font(max(24, width // 48), bold=False)
    title = (scene.title or "PRODUCT SIZE").upper()
    bbox = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (bbox[2] - bbox[0])) / 2, 55), title, font=title_font, fill=INK)
    draw.rounded_rectangle((width // 2 - 55, 125, width // 2 + 55, 132), radius=4, fill=ACCENT)

    product = Image.open(source).convert("RGB")
    product_box = (int(width * 0.19), int(height * 0.20), int(width * 0.81), int(height * 0.79))
    fitted = ImageOps.contain(product, (product_box[2] - product_box[0], product_box[3] - product_box[1]), method=Image.Resampling.LANCZOS)
    px = (width - fitted.width) // 2
    py = product_box[1] + (product_box[3] - product_box[1] - fitted.height) // 2
    image.paste(fitted, (px, py))

    left = px
    right = px + fitted.width
    top = py
    bottom = py + fitted.height
    draw_arrow(draw, (left, bottom + 45), (right, bottom + 45), f"{dims.width_mm} mm", label_font)
    draw_arrow(draw, (right + 55, top), (right + 55, bottom), f"{dims.height_mm} mm", label_font)
    depth_y = min(height - 85, bottom + 125)
    depth_start = int(width * 0.35)
    depth_end = int(width * 0.65)
    draw_arrow(draw, (depth_start, depth_y), (depth_end, depth_y), f"Depth {dims.depth_mm} mm", label_font)

    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, quality=95)
