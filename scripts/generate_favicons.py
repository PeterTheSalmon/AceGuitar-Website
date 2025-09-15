#!/usr/bin/env python3
"""
Generate a full favicon set from a source image, applying a true "squircle" mask
(superellipse) rather than simple rounded corners.

Outputs:
- Assets/favicons/favicon-16x16.png
- Assets/favicons/favicon-32x32.png
- Assets/favicons/apple-touch-icon.png (180x180)
- Assets/favicons/android-chrome-192x192.png
- Assets/favicons/android-chrome-512x512.png
- favicon.ico at repo root (multi-resolution 16, 32, 48)
- site.webmanifest at repo root (referencing 192 & 512)

Usage:
    python3 scripts/generate_favicons.py --src Assets/favicon-source.png

You can optionally pass --bg "#ffffff" to set a background color under transparent
pixels when resizing (default: transparent).
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Iterable, Tuple

try:
    from PIL import Image, ImageOps
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "Pillow (PIL) is required. Install with: python3 -m pip install --user Pillow"
    ) from e

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "Assets" / "favicons"

# Target sizes
PNG_SIZES = [
    (16, 16),
    (32, 32),
    (180, 180),  # Apple touch icon
    (192, 192),  # Android/manifest
    (512, 512),  # Android/manifest
]

ICO_SIZES = [(16, 16), (32, 32), (48, 48)]


def make_superellipse_mask(size: Tuple[int, int], n: float = 4.0) -> Image.Image:
    """
    Create a squircle/superellipse mask of the given size.

    Uses the superellipse equation: |x/a|^n + |y/b|^n <= 1
    n=4 is a pleasant iOS-like squircle. Increase n to approach a rectangle,
    decrease towards 2 for a circle.
    """
    w, h = size
    a, b = (w - 1) / 2.0, (h - 1) / 2.0
    cx, cy = a, b

    mask = Image.new("L", (w, h), 0)
    px = mask.load()

    inv_n = 1.0 / n
    for y in range(h):
        dy = abs(y - cy) / b
        for x in range(w):
            dx = abs(x - cx) / a
            if (dx ** n + dy ** n) <= 1.0:
                px[x, y] = 255
    return mask


def fit_and_mask(img: Image.Image, size: Tuple[int, int], bg: Tuple[int, int, int, int] | None) -> Image.Image:
    """Resize image to square 'size', preserving aspect and applying squircle mask.

    If bg is provided (RGBA tuple), composite under the masked image to replace
    transparent regions with the background color.
    """
    target = max(size)
    # Ensure RGBA for masking
    img_rgba = img.convert("RGBA")

    # Letterbox to square canvas before mask (preserve aspect)
    # Use high-quality LANCZOS resampling
    fitted = ImageOps.contain(img_rgba, (target, target), method=Image.LANCZOS)
    canvas = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    ox = (target - fitted.width) // 2
    oy = (target - fitted.height) // 2
    canvas.paste(fitted, (ox, oy))

    # Apply superellipse mask
    mask = make_superellipse_mask((target, target), n=4.0)
    masked = Image.new("RGBA", (target, target))
    masked.paste(canvas, (0, 0), mask=mask)

    if bg is not None:
        base = Image.new("RGBA", (target, target), bg)
        base.paste(masked, (0, 0), masked)
        masked = base

    # Ensure exact requested size (already square)
    if (target, target) != size:
        masked = masked.resize(size, Image.LANCZOS)
    return masked


def save_pngs(src: Image.Image, bg_color: str | None) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    bg_rgba = None
    if bg_color:
        # Normalize hex -> RGBA
        hex_str = bg_color.lstrip('#')
        if len(hex_str) == 3:
            r, g, b = (int(hex_str[i] * 2, 16) for i in range(3))
        else:
            r, g, b = (int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        bg_rgba = (r, g, b, 255)

    for w, h in PNG_SIZES:
        out_name = None
        if (w, h) == (16, 16):
            out_name = "favicon-16x16.png"
        elif (w, h) == (32, 32):
            out_name = "favicon-32x32.png"
        elif (w, h) == (180, 180):
            out_name = "apple-touch-icon.png"
        elif (w, h) == (192, 192):
            out_name = "android-chrome-192x192.png"
        elif (w, h) == (512, 512):
            out_name = "android-chrome-512x512.png"
        else:
            out_name = f"icon-{w}x{h}.png"

        icon = fit_and_mask(src, (w, h), bg_rgba)
        icon.save(OUT_DIR / out_name, format="PNG")
        print(f"wrote {OUT_DIR / out_name}")


def save_ico(src: Image.Image, bg_color: str | None) -> None:
    sizes = []
    for size in ICO_SIZES:
        sizes.append(fit_and_mask(src, size, (255, 255, 255, 0) if bg_color is None else None))
    # Build multi-res ICO
    ico_path = ROOT / "favicon.ico"
    sizes[0].save(ico_path, format="ICO", sizes=[im.size for im in sizes])
    print(f"wrote {ico_path}")


def write_manifest() -> None:
    manifest = {
        "name": "AceGuitar",
        "short_name": "AceGuitar",
        "icons": [
            {
                "src": "Assets/favicons/android-chrome-192x192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "Assets/favicons/android-chrome-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ],
        "theme_color": "#175F49",
        "background_color": "#175F49",
        "display": "standalone"
    }
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, indent=2))
    print(f"wrote {ROOT / 'site.webmanifest'}")


def main():
    parser = argparse.ArgumentParser(description="Generate favicon set with squircle mask")
    parser.add_argument("--src", required=True, help="Path to source image (PNG/JPG/SVG rasterized)")
    parser.add_argument("--bg", default=None, help="Hex background color (e.g. #ffffff) for non-transparent background")
    args = parser.parse_args()

    src_path = Path(args.src)
    if not src_path.exists():
        raise SystemExit(f"Source image not found: {src_path}")

    with Image.open(src_path) as im:
        save_pngs(im, args.bg)
        save_ico(im, args.bg)
        write_manifest()


if __name__ == "__main__":
    main()
