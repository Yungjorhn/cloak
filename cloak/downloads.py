"""Downloadable files for the moodboard: the finished look, and a shareable
before/after image.

Files are written to a temporary folder on the machine running the app (on
Colab, that machine is wiped when the session ends) under random names, and
removed when the user clears the moodboard. They are served by Gradio, so the
moodboard page itself stays light on mobile data.
"""

import shutil
import tempfile
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LOOKS_DIR = Path(tempfile.gettempdir()) / "cloak_looks"
LOOKS_DIR.mkdir(parents=True, exist_ok=True)

INK = (23, 21, 28)
PAPER = (255, 255, 255)
CREAM = (247, 242, 236)
PURPLE = (122, 60, 240)


def _font(size, bold=False):
    """A clean sans font if one is installed (matplotlib ships DejaVu), else Pillow's default."""
    try:
        import matplotlib
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / name), size)
    except Exception:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def _pill(draw, center_x, y, text, fill, color, font):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    w, h = right - left, bottom - top
    pad_x, pad_y = int(h * 0.9), int(h * 0.55)
    box = (center_x - w // 2 - pad_x, y, center_x + w // 2 + pad_x, y + h + 2 * pad_y)
    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=fill)
    draw.text((center_x - w // 2 - left, y + pad_y - top), text, font=font, fill=color)


def before_after_image(before: Image.Image, after: Image.Image, height: int = 1280) -> Image.Image:
    """Side-by-side image with Before/After labels and a small CLOAK mark."""
    def fit(img):
        img = img.convert("RGB")
        return img.resize((max(1, round(img.width * height / img.height)), height), Image.LANCZOS)

    before, after = fit(before), fit(after)
    gap, margin, footer = height // 64, height // 32, height // 9
    width = before.width + after.width + gap + 2 * margin
    canvas = Image.new("RGB", (width, height + 2 * margin + footer), CREAM)
    canvas.paste(before, (margin, margin))
    canvas.paste(after, (margin + before.width + gap, margin))

    draw = ImageDraw.Draw(canvas)
    label = _font(height // 36, bold=True)
    y = margin + height - height // 12
    _pill(draw, margin + before.width // 2, y, "BEFORE", PAPER, INK, label)
    _pill(draw, margin + before.width + gap + after.width // 2, y, "AFTER", PURPLE, PAPER, label)

    brand, note = _font(height // 22, bold=True), _font(height // 48)
    fy = margin + height + (footer + margin) // 2
    draw.text((margin, fy), "C L O A K", font=brand, fill=INK, anchor="lm")
    draw.text((width - margin, fy), "Virtual try-on with open-source AI", font=note,
              fill=(111, 106, 117), anchor="rm")
    return canvas


def save_look_files(look_no: int, before: Image.Image, after: Image.Image) -> dict:
    """Write the look and its before/after image; returns their file paths."""
    folder = LOOKS_DIR / uuid.uuid4().hex  # random, so links can't be guessed
    folder.mkdir(parents=True, exist_ok=True)
    look_path = folder / f"cloak-look-{look_no:02d}.jpg"
    pair_path = folder / f"cloak-look-{look_no:02d}-before-after.jpg"
    after.convert("RGB").save(look_path, quality=92)
    before_after_image(before, after).save(pair_path, quality=90)
    return {"look": str(look_path), "pair": str(pair_path)}


def delete_look_files(looks) -> None:
    for look in looks:
        for path in (look.get("files") or {}).values():
            shutil.rmtree(Path(path).parent, ignore_errors=True)
