"""Exports the data the specimen app (specimen/, SvelteKit) is built from.

Writes specimen/src/lib/data/specimen.json (metrics, weights, versions and every glyph cell's
outline), copies the variable fonts (Llama Sans, and Llama Mono for its code sample) to specimen/src/lib/fonts/ and writes their @font-face rules
(fonts.css). Then build the page with:

    cd specimen && npm run build        # -> specimen/build/index.html, a single self-contained file

Run:  python scripts/build_specimen.py
      python scripts/build_specimen.py --prev-fonts=DIR [--fonts=DIR] [--prev-label="Before|After"]
      (--prev-fonts adds a floating Before/After switch comparing every version and the glyph grid with
       another build laid out like this folder: variable/LlamaSans{Display,UI,Text}[wght].ttf and static/;
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
VARIANTS = ["Display", "UI"]                         # versions of Llama Sans the page can switch between
GRID_VARIANT = "UI"                           # the glyph grid is drawn from this version's statics
STYLES = [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")]
WATERFALL = [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")]
GROUPS = [("Uppercase", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
          ("Lowercase", "abcdefghijklmnopqrstuvwxyz"),
          ("Figures", "0123456789"),
          ("Punctuation & symbols", ".,:;!?'\"-–—()[]/&@#%*+=$€"),
          ("Llama icon · U+E000", "\ue000")]

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


def main():
    fonts = FONTS or "."
    statics = {w: TTFont(f"{fonts}/static/LlamaSans{GRID_VARIANT}-{s}.ttf") for w, s in STYLES}
    base = statics[400]
    os2 = base["OS/2"]
    asc, dsc = round(bounds(base, "l")[3]), round(bounds(base, "p")[1])
    top, bot = asc + 60, dsc - 40
    chars = [c for _, s in GROUPS for c in s]
    vw = max(f["hmtx"][f.getBestCmap()[ord(c)]][0] for f in statics.values() for c in chars) + 60
    prev = {w: TTFont(f"{PREV}/static/LlamaSans{GRID_VARIANT}-{s}.ttf") for w, s in STYLES} if PREV else {}

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
    axis = TTFont(f"{fonts}/variable/LlamaSans{GRID_VARIANT}[wght].ttf")["fvar"].axes[0]

    fonts_dir = os.path.join(APP, "src", "lib", "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    for old in os.listdir(fonts_dir):  # start clean: a previous comparison build may be lying around
        if old.endswith(".ttf"):
            os.remove(os.path.join(fonts_dir, old))
    faces = []
    for v in VARIANTS:  # brackets in file names trip up bundlers, so the app gets plain names
        shutil.copy(f"{fonts}/variable/LlamaSans{v}[wght].ttf", os.path.join(fonts_dir, f"LlamaSans{v}-VF.ttf"))
        faces.append((f"Llama Sans {v}", f"LlamaSans{v}-VF.ttf"))
        if PREV:
            shutil.copy(f"{PREV}/variable/LlamaSans{v}[wght].ttf", os.path.join(fonts_dir, f"LlamaSansPrev{v}-VF.ttf"))
            faces.append((f"Llama Sans Prev {v}", f"LlamaSansPrev{v}-VF.ttf"))
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
