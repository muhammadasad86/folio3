"""Trim client logos to their visible content (ignores transparent and near-white padding) for the static client grid.
Writes assets/figma/client-XX-t.webp + assets/figma/client-trim.json (aspect ratio per logo)."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent / "assets/figma"
meta = {}
for i in range(1, 16):
    im = Image.open(ROOT / f"client-{i:02d}.webp").convert("RGBA"); a = np.asarray(im)
    ink = (a[..., 3] > 24) & ~((a[..., :3] > 236).all(-1))
    ys, xs = np.where(ink); box = (max(xs.min() - 2, 0), max(ys.min() - 2, 0), min(xs.max() + 3, im.width), min(ys.max() + 3, im.height))
    t = im.crop(box); t.save(ROOT / f"client-{i:02d}-t.webp", "WEBP", quality=90, method=6)
    meta[f"{i:02d}"] = round(t.width / t.height, 3)
json.dump(meta, open(ROOT / "client-trim.json", "w"))
print(meta)
award = {}
for i in range(1, 21):   # award badges (already background-free) — trim to content for the awards wall
    im = Image.open(ROOT / f"award-{i:02d}.webp").convert("RGBA"); a = np.asarray(im)
    ink = (a[..., 3] > 24) & ~((a[..., :3] > 236).all(-1)); ys, xs = np.where(ink)
    t = im.crop((max(xs.min() - 2, 0), max(ys.min() - 2, 0), min(xs.max() + 3, im.width), min(ys.max() + 3, im.height)))
    t.save(ROOT / f"award-{i:02d}-t.webp", "WEBP", quality=90, method=6); award[f"{i:02d}"] = round(t.width / t.height, 3)
json.dump(award, open(ROOT / "award-trim.json", "w")); print(award)
