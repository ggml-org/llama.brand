"""Builds the Llama and Llama.cpp lockups and covers in logo/svg/ from the current icon and Llama Sans Display.

The icon comes from svg/icon/icon-light.svg; the wordmark, "Llama" and "llama.cpp" (always lowercase), is set in
fonts/static/LlamaSansDisplay-Bold.ttf, shaped with HarfBuzz (so its kerning applies) and outlined, so the logo
follows the fonts whenever they change. The icon is 520 px tall at the left of a 600 px lockup; the wordmark's cap
height is 272.6 px on a baseline at 436, centred on the icon, its first letter starting at 741.5; each cover is the lockup centred
on a 7500 × 2500 field. Then render the WebP and PNG files with render_webp.sh.

Run:  uvx --with fonttools==4.68.0 --with uharfbuzz python logo/scripts/build_lockups.py
"""
import os
import re
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
import uharfbuzz as hb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FONT = os.path.join(ROOT, "..", "fonts", "static", "LlamaSansDisplay-Bold.ttf")
ICON_SIZE, ICON_TOP = 520, 40  # the icon in a 600 px lockup
BASELINE, CAP_HEIGHT = 436, 272.6  # the wordmark's capitals span 163.4 to 436, centred on the icon
WORD_LEFT = 741.5              # where the first letter starts
COVER_W, COVER_H, LOCKUP_H = 7500, 2500, 600

# colours: icon, wordmark, ".cpp", and the cover's field. The .cpp takes the palette's accent orange (art-orange in
# the design system, oklch(0.619 0.171 33)), not the old brand orange
ORANGE = "#D9553B"
LIGHT = dict(icon="#111111", word="#111111", cpp=ORANGE, field="#FAFAFA")
DARK = dict(icon="#FAFAFA", word="#FAFAFA", cpp=ORANGE, field="#111111")


def icon_paths():
    svg = open(os.path.join(ROOT, "svg", "icon", "icon-light.svg")).read()
    return re.findall(r'<path d="([^"]+)"', svg)


def shaped(text):
    """HarfBuzz's glyphs and positions for `text` in the font: [(glyph id, x offset, x advance)]."""
    face = hb.Face(hb.Blob.from_file_path(FONT))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb.Font(face), buf, {"kern": True, "liga": True})
    return [(i.codepoint, i.cluster, p.x_offset, p.x_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def wordmark(font, text, split, x, k):
    """Two outlines of `text`, set from x on the baseline at scale k: the characters before `split`, then the rest."""
    gs, order = font.getGlyphSet(), font.getGlyphOrder()
    ntos = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
    pens = [SVGPathPen(gs, ntos=ntos), SVGPathPen(gs, ntos=ntos)]
    for gid, cluster, offset, advance in shaped(text):
        pen = pens[cluster >= split]
        gs[order[gid]].draw(TransformPen(pen, (k, 0, 0, -k, x + offset * k, BASELINE)))
        x += advance * k
    return [p.getCommands() for p in pens], x


def lockup(font, name, colours, dx=0, dy=0):
    """The paths of one lockup, offset by (dx, dy), and its width."""
    k = CAP_HEIGHT / font["OS/2"].sCapHeight
    text = "llama.cpp" if name == "llama-cpp" else "Llama"  # llama.cpp is always lowercase, Llama capitalised
    first = shaped(text[0])[0][0]
    x0 = WORD_LEFT - font["glyf"][font.getGlyphOrder()[first]].xMin * k
    s = ICON_SIZE / 600
    group = f'<g transform="translate({dx} {dy})">'
    group += "".join(f'<path transform="translate(0 {ICON_TOP}) scale({s:.6f})" d="{d}" fill="{colours["icon"]}"/>'
                     for d in icon_paths())
    (word, cpp), x = wordmark(font, text, 5, x0, k)
    group += f'<path d="{word}" fill="{colours["word"]}"/>'
    if cpp:
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
    font = TTFont(FONT)
    for name in ("llama", "llama-cpp"):
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            body, width = lockup(font, name, colours)
            write(os.path.join(ROOT, "svg", "lockup", name, f"logo-{name}-{mode}.svg"), svg(width, LOCKUP_H, body))
        _, width = lockup(font, name, LIGHT)
        dx, dy = (COVER_W - width) / 2, (COVER_H - LOCKUP_H) / 2
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            body, _ = lockup(font, name, colours, dx, dy)
            field = f'<rect width="{COVER_W}" height="{COVER_H}" fill="{colours["field"]}"/>\n'
            write(os.path.join(ROOT, "svg", "cover", name, f"cover-{name}-{mode}.svg"), svg(COVER_W, COVER_H, field + body))
