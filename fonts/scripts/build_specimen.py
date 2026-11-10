"""Exports the data the specimen app (specimen/, SvelteKit) is built from.

Writes specimen/src/lib/data/specimen.json (metrics, weights, versions and every glyph cell's
outline), copies the variable fonts (Llama Sans, one font over wght and opsz, and Llama Mono for its code sample) to specimen/src/lib/fonts/ and writes their @font-face rules
(fonts.css). Then build the page with:

    cd specimen && npm run build        # -> specimen/build/index.html, a single self-contained file

Run:  python scripts/build_specimen.py
      python scripts/build_specimen.py --prev-fonts=DIR [--fonts=DIR] [--prev-label="Before|After"]
      (--prev-fonts adds a floating Before/After switch comparing every version and the glyph grid with
       another build laid out like this folder: variable/LlamaSans[opsz,wght].ttf and static/;
       --fonts takes the "after" build from somewhere other than this folder)
"""
import json
import os
import re
import shutil
import sys
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

APP = "specimen"
VARIANTS = ["Display", "UI"]                  # the optical sizes the page can switch between (the axis's named ends)
GRID_VARIANT = "UI"                           # the glyph grid is drawn from the statics, which are cut at UI's size
STYLES = [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")]
WATERFALL = [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")]
GROUPS = [("Uppercase", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
          ("Lowercase", "abcdefghijklmnopqrstuvwxyz"),
          ("Figures", "0123456789"),
          ("Punctuation & symbols", ".,:;!?'\"-–—()[]/&@#%*+=$€"),
          ("Llama icon · U+E000, U+E001, U+E002", "\ue000\ue001\ue002")]

PREV = next((os.path.abspath(a[13:]) for a in sys.argv[1:] if a.startswith("--prev-fonts=")), None)
FONTS = next((os.path.abspath(a[8:]) for a in sys.argv[1:] if a.startswith("--fonts=")), None)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # fonts/, one level above scripts/
PREV_LABELS = next((a[13:] for a in sys.argv[1:] if a.startswith("--prev-label=")), "Before|After").split("|")


def bounds(font, ch):
    gs = font.getGlyphSet()
    pen = BoundsPen(gs)
    gs[font.getBestCmap()[ord(ch)]].draw(pen)
    return pen.bounds


def path(font, ch, dx, top):
    """SVG path of a glyph, flipped and placed (dx, top) in its cell, rounded to whole units."""
    name = font.getBestCmap().get(ord(ch))
    if not name:
        return None, 0
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}")
    gs[name].draw(TransformPen(pen, (1, 0, 0, -1, round(dx), top)))
    return pen.getCommands(), font["hmtx"][name][0]


def differs(a, b, tol=2):
    """True when two outlines differ by more than interpolation rounding (tol font units)."""
    na, nb = re.findall(r"-?\d+", a), re.findall(r"-?\d+", b)
    return len(na) != len(nb) or any(abs(int(x) - int(y)) > tol for x, y in zip(na, nb))


SMALL_SIZES = [10, 11, 12, 13, 14, 16]         # the font sizes (CSS px) the small-sizes section sets


def small_tracking(path):
    """Units each advance gains at SMALL_SIZES over the font's opsz 16, read off the n (a size below the axis clamps)."""
    font = TTFont(path)
    lo = next(a.minValue for a in font["fvar"].axes if a.axisTag == "opsz")
    width = lambda size: font.getGlyphSet(location={"opsz": max(size, lo)})["n"].width
    return [round(width(size) - width(16)) for size in SMALL_SIZES]


def main():
    fonts = FONTS or "."
    statics = {w: TTFont(f"{fonts}/static/LlamaSans-{s}.ttf") for w, s in STYLES}
    base = statics[400]
    os2 = base["OS/2"]
    asc, dsc = round(bounds(base, "l")[3]), round(bounds(base, "p")[1])
    top, bot = asc + 60, dsc - 40
    chars = [c for _, s in GROUPS for c in s]
    vw = max(f["hmtx"][f.getBestCmap()[ord(c)]][0] for f in statics.values() for c in chars) + 60
    prev = {w: TTFont(f"{PREV}/static/LlamaSans-{s}.ttf") for w, s in STYLES} if PREV else {}

    cells = {}
    for w, font in statics.items():
        row = []
        for c in chars:
            _, adv = path(font, c, 0, top)
            dx = (vw - adv) / 2
            d, _ = path(font, c, dx, top)
            cell = {"ch": c, "adv": adv, "dx": round(dx), "d": d}
            if w in prev:
                pname = prev[w].getBestCmap().get(ord(c))
                if pname:
                    pd, _ = path(prev[w], c, (vw - prev[w]["hmtx"][pname][0]) / 2, top)
                    if differs(pd, d):
                        cell["prev"] = pd
            row.append(cell)
        cells[w] = row

    stems = {}
    for w, font in statics.items():
        b = bounds(font, "I")
        stems[w] = round(b[2] - b[0])
    axis = next(a for a in TTFont(f"{fonts}/variable/LlamaSans[opsz,wght].ttf")["fvar"].axes if a.axisTag == "wght")

    fonts_dir = os.path.join(APP, "src", "lib", "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    for old in os.listdir(fonts_dir):  # start clean: a previous comparison build may be lying around
        if old.endswith(".ttf"):
            os.remove(os.path.join(fonts_dir, old))
    faces = []
    # brackets in file names trip up bundlers, so the app gets plain names
    shutil.copy(f"{fonts}/variable/LlamaSans[opsz,wght].ttf", os.path.join(fonts_dir, "LlamaSans-VF.ttf"))
    faces.append(("Llama Sans", "LlamaSans-VF.ttf"))
    if PREV:
        shutil.copy(f"{PREV}/variable/LlamaSans[opsz,wght].ttf", os.path.join(fonts_dir, "LlamaSansPrev-VF.ttf"))
        faces.append(("Llama Sans Prev", "LlamaSansPrev-VF.ttf"))
    if os.path.exists(f"{fonts}/variable/LlamaMono[wght].ttf"):  # Llama Mono, for the code sample
        shutil.copy(f"{fonts}/variable/LlamaMono[wght].ttf", os.path.join(fonts_dir, "LlamaMono-VF.ttf"))
        faces.append(("Llama Mono", "LlamaMono-VF.ttf"))
    with open(os.path.join(fonts_dir, "fonts.css"), "w") as f:
        f.write("/* generated by build_specimen.py */\n")
        for family, file in faces:
            f.write(f'@font-face {{ font-family: "{family}"; font-weight: {int(axis.minValue)} {int(axis.maxValue)}; '
                    f'src: url("./{file}") format("truetype-variations"); font-display: block; }}\n')

    data = {
        "glyphCount": len([g for g in base.getGlyphOrder() if g != ".notdef"]),
        "metrics": {"upm": base["head"].unitsPerEm, "cap": os2.sCapHeight, "x": os2.sxHeight, "asc": asc, "dsc": dsc},
        "axis": {"min": int(axis.minValue), "max": int(axis.maxValue)},
        "styles": [{"weight": w, "name": s, "stem": stems[w]} for w, s in STYLES],
        "waterfall": [{"weight": w, "name": s} for w, s in WATERFALL],
        "variants": VARIANTS,
        "compare": {"labels": PREV_LABELS} if PREV else None,
        "small": {"sizes": SMALL_SIZES, "tracking": small_tracking(f"{fonts}/variable/LlamaSans[opsz,wght].ttf"),
                  "prevTracking": small_tracking(f"{PREV}/variable/LlamaSans[opsz,wght].ttf") if PREV else None},
        "grid": {
            "variant": GRID_VARIANT, "width": vw, "height": top - bot,
            "guides": {"base": top, "x": top - os2.sxHeight, "cap": top - os2.sCapHeight,
                       "asc": top - asc, "dsc": top - dsc},
            "groups": [{"title": t, "chars": list(s)} for t, s in GROUPS],
            "cells": cells,
        },
    }
    out = os.path.join(APP, "src", "lib", "data", "specimen.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("wrote", out, os.path.getsize(out) // 1024, "KB, and", len(faces), "fonts to", fonts_dir)


if __name__ == "__main__":
    os.chdir(ROOT)  # every path is relative to fonts/, wherever this is run from
    main()
