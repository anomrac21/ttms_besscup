#!/usr/bin/env python3
"""Download copyright-free section images (Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "static" / "images"
CONTENT = ROOT / "content"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

DOWNLOADS: dict[str, tuple[str, str]] = {
    "hot-cups.webp": (PEX.format(id="894695"), "Pexels #894695"),
    "cold-cups.webp": (PEX.format(id="997296"), "Pexels #997296"),
    "specialty-cups.webp": (PEX.format(id="2789326"), "Pexels #2789326"),
    "mocktails.webp": (PEX.format(id="1126728"), "Pexels #1126728"),
    "desserts.webp": (PEX.format(id="291528"), "Pexels #291528"),
    "promotions.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "hero.webp": (PEX.format(id="302899"), "Pexels #302899"),
    "slideshow-hot.webp": (PEX.format(id="894695"), "Pexels #894695"),
    "slideshow-specialty.webp": (PEX.format(id="2789326"), "Pexels #2789326"),
    "slideshow-mocktails.webp": (PEX.format(id="1126728"), "Pexels #1126728"),
    "slideshow-desserts.webp": (PEX.format(id="291528"), "Pexels #291528"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "hot-cups": "hot-cups.webp",
    "cold-cups": "cold-cups.webp",
    "specialty-cups": "specialty-cups.webp",
    "mocktails": "mocktails.webp",
    "desserts": "desserts.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def download_one(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Halal certified independent cafe in Chaguanas. Hot and iced coffee, "
            "specialty cups, mocktails, and desserts. Fresh local beans.</p>"
        )
    text = (
        "---\n"
        'title: "Bess Cup"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('hot-cups.webp')}\n"
        f"    - image: {img('specialty-cups.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('slideshow-hot.webp')}\n"
        f"    - image: {img('slideshow-specialty.webp')}\n"
        f"    - image: {img('slideshow-mocktails.webp')}\n"
        f"    - image: {img('slideshow-desserts.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    credits: list[str] = []
    for filename, (url, credit) in DOWNLOADS.items():
        if download_one(filename, url):
            credits.append(f"- {filename} — {credit}")

    for section, image_file in SECTIONS.items():
        if (IMAGES_DIR / image_file).exists():
            update_section_index(section, image_file)
        else:
            print(f"WARN: missing {image_file} for {section}")

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (Pexels License — free to use):\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
