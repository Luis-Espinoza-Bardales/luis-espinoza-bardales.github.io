from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "data" / "papers.json"
SIZE = 900
BACKGROUND = "white"


def trim_whitespace(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, BACKGROUND)
    diff = ImageChops.difference(rgb, background).convert("L")
    mask = diff.point(lambda pixel: 255 if pixel > 18 else 0)
    box = mask.getbbox()
    if not box:
        return rgb

    left, top, right, bottom = box
    margin_x = max(12, int((right - left) * 0.06))
    margin_y = max(12, int((bottom - top) * 0.06))
    left = max(0, left - margin_x)
    top = max(0, top - margin_y)
    right = min(rgb.width, right + margin_x)
    bottom = min(rgb.height, bottom + margin_y)
    return rgb.crop((left, top, right, bottom))


def square_thumbnail(image: Image.Image) -> Image.Image:
    trimmed = trim_whitespace(image)
    target = SIZE - 70
    scale = max(target / trimmed.width, target / trimmed.height)
    resized = trimmed.resize(
        (max(1, int(trimmed.width * scale)), max(1, int(trimmed.height * scale))),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new("RGB", (SIZE, SIZE), BACKGROUND)
    x = (SIZE - resized.width) // 2
    y = (SIZE - resized.height) // 2
    canvas.paste(resized, (x, y))
    return canvas.crop((0, 0, SIZE, SIZE))


def extract_image(source_pdf: Path, page_number: int, image_index: int) -> Image.Image:
    reader = PdfReader(str(source_pdf))
    page = reader.pages[page_number - 1]
    images = list(page.images)
    if image_index >= len(images):
        raise IndexError(f"{source_pdf.name} page {page_number} has only {len(images)} embedded images")
    return images[image_index].image.convert("RGB")


def main() -> None:
    papers = json.loads(PAPERS.read_text(encoding="utf-8"))
    generated = 0

    for paper in papers:
        thumbnail = paper.get("thumbnail")
        output = paper.get("image")
        if not thumbnail or not output:
            continue

        source_pdf = ROOT / thumbnail["sourcePdf"]
        image = extract_image(
            source_pdf=source_pdf,
            page_number=int(thumbnail["sourcePage"]),
            image_index=int(thumbnail["sourceImage"]),
        )
        output_path = ROOT / output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        square_thumbnail(image).save(output_path, "PNG", optimize=True)
        generated += 1

    print(f"Generated {generated} thumbnails from real PDF figures/images")


if __name__ == "__main__":
    main()
