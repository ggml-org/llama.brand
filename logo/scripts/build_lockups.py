"""Builds the Llama and Llama.cpp lockups and covers in logo/svg/ from the current icon and Llama Mono.

The icon comes from svg/icon/icon-light.svg; the wordmark is set in fonts/variable/LlamaMono[wght].ttf at WEIGHT,
outlined, one 600-unit cell per character, so the logo follows the fonts whenever they change. The layout and the
colours stay those of the existing files: the icon 520 px tall at the left of a 600 px lockup, the wordmark on a
baseline at 436 with its l 272.6 px tall, and each cover the lockup centred on a 7500 × 2500 field. Then render the
WebP and PNG files with render_webp.sh.

Run:  uvx --with fonttools==4.68.0 python logo/scripts/build_lockups.py
"""
import os
import re
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FONT = os.path.join(ROOT, "..", "fonts", "variable", "LlamaMono[wght].ttf")
WEIGHT = 530                  # Llama Mono's l stem at 530 matches the wordmark's (about 101 units)
ICON_SIZE, ICON_TOP = 520, 40  # the icon in a 600 px lockup
BASELINE, L_HEIGHT = 436, 272.6
WORD_LEFT = 741.5              # where the first l's foot starts
GAP = 0                        # cells between the words: llama.cpp is set solid
COVER_W, COVER_H, LOCKUP_H = 7500, 2500, 600

# colours: icon, wordmark, ".cpp", and the cover's field
LIGHT = dict(icon="#111111", word="#111111", cpp="#F65E00", field="#FAFAFA")
DARK = dict(icon="#FAFAFA", word="#FAFAFA", cpp="#F65E00", field="#111111")
ALT = dict(icon="#111111", word="#111111", cpp="#FAFAFA", field="#F65E00")


def icon_paths():
    svg = open(os.path.join(ROOT, "svg", "icon", "icon-light.svg")).read()
    return re.findall(r'<path d="([^"]+)"', svg)


def word_path(font, text, x, k):
    """The outline of `text` in the font, set from x on the baseline at scale k (font units to px)."""
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.3f}".rstrip("0").rstrip("."))
    for ch in text:
        name = cmap[ord(ch)]
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x, BASELINE)))
        x += font["hmtx"][name][0] * k
    return pen.getCommands(), x


def lockup(font, name, colours, dx=0, dy=0):
    """The paths of one lockup, offset by (dx, dy), and its width."""
    cmap = font.getBestCmap()
    l = font["glyf"][cmap[ord("l")]]
    k = L_HEIGHT / l.yMax
    l_left = l.xMin
    x0 = WORD_LEFT - l_left * k
    s = ICON_SIZE / 600
    group = f'<g transform="translate({dx} {dy})">'
    group += "".join(f'<path transform="translate(0 {ICON_TOP}) scale({s:.6f})" d="{d}" fill="{colours["icon"]}"/>'
                     for d in icon_paths())
    word, x = word_path(font, "llama", x0, k)
    group += f'<path d="{word}" fill="{colours["word"]}"/>'
    if name == "llama-cpp":
        cpp, x = word_path(font, ".cpp", x + GAP * 600 * k, k)
        group += f'<path d="{cpp}" fill="{colours["cpp"]}"/>'
    return group + "</g>", round(x)


def svg(width, height, body):
    return (f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg">\n{body}\n</svg>\n')


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    font = instantiateVariableFont(TTFont(FONT), {"wght": WEIGHT})
    for name in ("llama", "llama-cpp"):
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            body, width = lockup(font, name, colours)
            write(os.path.join(ROOT, "svg", "lockup", name, f"logo-{name}-{mode}.svg"), svg(width, LOCKUP_H, body))
        _, width = lockup(font, name, LIGHT)
        dx, dy = (COVER_W - width) / 2, (COVER_H - LOCKUP_H) / 2
        for mode, colours in (("light", LIGHT), ("dark", DARK), ("alt", ALT)):
            body, _ = lockup(font, name, colours, dx, dy)
            field = f'<rect width="{COVER_W}" height="{COVER_H}" fill="{colours["field"]}"/>\n'
            write(os.path.join(ROOT, "svg", "cover", name, f"cover-{name}-{mode}.svg"), svg(COVER_W, COVER_H, field + body))
