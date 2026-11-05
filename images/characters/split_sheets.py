"""Split 3x3 chibi character sheets on magenta into transparent PNGs.

usage:  python split_sheets.py            (processes every sheets/*.png)
        python split_sheets.py sheets/sheet-3-patients.png

For each sheet it
  1. measures the magenta from the sheet's own border (generators vary it),
  2. turns each pixel's "magenta strength" into an alpha value, so the
     anti-aliased outline keeps a smooth edge instead of a jagged cutout,
  3. un-mixes the magenta out of those edge pixels (no pink fringe),
  4. finds each figure as a connected blob (props such as walkers and IV
     poles stay attached) and assigns it to a grid cell by its centre,
  5. writes figures/<prefix>-NN.png cropped to the figure, plus cast.png,
     a labelled index of every figure.

Figures keep their native pixel scale, so any two shown at the same CSS
scale stand at the same size.
"""
import hashlib
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
PREFIX = {"sheet-1": "nurse", "sheet-2": "staff", "sheet-3": "patient", "sheet-4": "family"}
PAD = 6          # transparent margin around each crop, in pixels
MIN_BLOB = 400   # smaller blobs are background noise


def magenta_strength(rgb):
    """How magenta a pixel is: high red and blue, low green."""
    return np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]


def border_pixels(a, w=10):
    return np.concatenate([a[:w].reshape(-1, 3), a[-w:].reshape(-1, 3),
                           a[:, :w].reshape(-1, 3), a[:, -w:].reshape(-1, 3)])


def alpha_and_colour(rgb):
    bg = border_pixels(rgb)
    bg_colour = np.median(bg, axis=0)
    k_bg = magenta_strength(bg)
    hi = np.percentile(k_bg, 0.5) - 8        # at or above this: pure background
    lo = 45.0                                 # at or below this: pure figure
    k = magenta_strength(rgb)
    alpha = np.clip((hi - k) / (hi - lo), 0.0, 1.0)
    alpha[alpha < 0.06] = 0.0

    # Un-mix: observed = a*figure + (1-a)*magenta  =>  figure = (observed - (1-a)*magenta) / a
    colour = rgb.copy()
    edge = (alpha > 0) & (alpha < 1)
    a = alpha[edge][:, None]
    colour[edge] = np.clip((rgb[edge] - (1 - a) * bg_colour) / a, 0, 255)
    return alpha, colour, hi


def dilate(mask, r):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy * dy + dx * dx <= r * r:
                out |= np.roll(np.roll(mask, dy, 0), dx, 1)
    return out


def label_blobs(mask, block=4):
    """Connected components on a coarse grid (fast enough without scipy)."""
    h, w = mask.shape
    coarse = mask[: h - h % block, : w - w % block]
    coarse = coarse.reshape(h // block, block, w // block, block).any(axis=(1, 3))
    labels = np.zeros(coarse.shape, dtype=int)
    n = 0
    for y0, x0 in zip(*np.nonzero(coarse)):
        if labels[y0, x0]:
            continue
        n += 1
        labels[y0, x0] = n
        queue = deque([(y0, x0)])
        while queue:
            y, x = queue.popleft()
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < coarse.shape[0] and 0 <= nx < coarse.shape[1] \
                        and coarse[ny, nx] and not labels[ny, nx]:
                    labels[ny, nx] = n
                    queue.append((ny, nx))
    full = np.kron(labels, np.ones((block, block), dtype=int))
    out = np.zeros((h, w), dtype=int)
    out[: full.shape[0], : full.shape[1]] = full
    return out, n


def split(sheet_path):
    sheet_path = Path(sheet_path)
    prefix = next(v for k, v in PREFIX.items() if sheet_path.stem.startswith(k))
    rgb = np.asarray(Image.open(sheet_path).convert("RGB")).astype(float)
    h, w = rgb.shape[:2]
    alpha, colour, hi = alpha_and_colour(rgb)

    solid = alpha > 0.5
    labels, n = label_blobs(dilate(solid, 3))
    cells = {}
    for i in range(1, n + 1):
        blob = labels == i
        if (blob & solid).sum() < MIN_BLOB:
            continue
        ys, xs = np.nonzero(blob & solid)
        cell = (min(int(ys.mean() * 3 / h), 2), min(int(xs.mean() * 3 / w), 2))
        cells.setdefault(cell, np.zeros_like(blob))
        cells[cell] |= blob

    results = []
    for row in range(3):
        for col in range(3):
            if (row, col) not in cells:
                print(f"  WARNING: no figure found in row {row + 1}, col {col + 1}")
                continue
            keep = cells[(row, col)] & (alpha > 0)
            ys, xs = np.nonzero(keep)
            y0, y1 = max(ys.min() - PAD, 0), min(ys.max() + PAD + 1, h)
            x0, x1 = max(xs.min() - PAD, 0), min(xs.max() + PAD + 1, w)
            a = np.where(keep, alpha, 0.0)[y0:y1, x0:x1]
            rgba = np.dstack([colour[y0:y1, x0:x1], a * 255]).round().astype(np.uint8)
            name = f"{prefix}-{row * 3 + col + 1:02d}.png"
            Image.fromarray(rgba, "RGBA").save(OUT / name, optimize=True)
            results.append((name, x1 - x0, y1 - y0))
            print(f"  {name}: {x1 - x0}x{y1 - y0}")
    return results


def cast_index(names, scale=0.55):
    """A labelled index of every figure (cast.png), at a shared scale, feet on
    a common baseline per row, on a faint checkerboard so edges show."""
    from PIL import ImageDraw, ImageFont
    ims = [Image.open(OUT / nm) for nm in names]
    ims = [im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS) for im in ims]
    cw = max(i.width for i in ims) + 24
    ch = max(i.height for i in ims) + 40
    cols = 9
    rows = -(-len(ims) // cols)
    sheet = Image.new("RGBA", (cols * cw, rows * ch), "white")
    tile = 10
    for y in range(0, rows * ch, tile):
        for x in range(0, cols * cw, tile):
            if (x // tile + y // tile) % 2:
                sheet.paste((236, 239, 243, 255), (x, y, x + tile, y + tile))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    for k, (im, nm) in enumerate(zip(ims, names)):
        cx, top = (k % cols) * cw, (k // cols) * ch
        sheet.alpha_composite(im, (cx + (cw - im.width) // 2, top + ch - 30 - im.height))
        label = Path(nm).stem
        w = draw.textlength(label, font=font)
        draw.text((cx + (cw - w) / 2, top + ch - 24), label, fill=(51, 65, 85), font=font)
    sheet.convert("RGB").save(HERE / "cast.png", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    paths = sys.argv[1:] or sorted(str(p) for p in (HERE / "sheets").glob("sheet-*.png"))
    seen, names = set(), []
    for p in paths:
        digest = hashlib.md5(Path(p).read_bytes()).hexdigest()
        if digest in seen:          # the same sheet saved under two names
            continue
        seen.add(digest)
        print(Path(p).name)
        names += [r[0] for r in split(p)]
    cast_index(sorted(set(names)))
    print(f"{len(names)} figures -> {OUT}")
