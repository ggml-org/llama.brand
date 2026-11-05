"""Builds the Llama and Llama.cpp lockups and covers in logo/svg/ from the current icon and Llama Sans.

The icon comes from svg/icon/icon-light.svg; the wordmark, "Llama" and "llama.cpp" (always lowercase), is set in
Llama Sans Bold at its Display optical size (fonts/variable/LlamaSans[opsz,wght].ttf at wght 700, opsz 40), shaped
with HarfBuzz (so its kerning applies) and outlined, so the logo
follows the fonts whenever they change. The icon is 520 px tall at the left of a 600 px lockup, and the lockup's
proportion is the font's own capital icon (U+E001): the icon 1.24 times the cap height, centred on the capitals, and
the first letter as far after it as a space puts it, so the lockup matches the icon typed before the name. Each cover
is the lockup centred on a 7500 × 2500 field. The icon and each lockup also come on their background (-bg): the same canvas, the mark
centred on the light or dark field with an even margin, the icon optically lifted. Then render the WebP and PNG
files with render_webp.sh.

Run:  uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_lockups.py
"""
import io
import os
import re
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont
import uharfbuzz as hb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FONT = os.path.join(ROOT, "..", "fonts", "variable", "LlamaSans[opsz,wght].ttf")
WORDMARK = {"wght": 700, "opsz": 40}  # Bold, at the Display end of the optical size axis
ICON_SIZE, ICON_TOP = 520, 40  # the icon in a 600 px lockup
CAPITAL_ICON = "\ue001"  # the font's capital icon: the lockup takes its size and spacing from it
COVER_W, COVER_H, LOCKUP_H = 7500, 2500, 600
# the on-background versions: the same canvas as the transparent file, the mark centred on the field with an even
# margin of FIELD_MARGIN of the shorter side; the icon sits OPTICAL_LIFT of its height above centre, as in the Llama
# app icon: its weight is low (the wide bottom bar), so mathematically centred it reads as sitting low
FIELD_MARGIN = 0.12
OPTICAL_LIFT = 1 / 60

# colours: icon, wordmark, ".cpp", and the cover's field. The .cpp takes cinder, the brand's one accent orange
# (art-cinder in the design system, oklch(0.68 0.18 46))
CINDER = "#EE6C1E"
LIGHT = dict(icon="#111111", word="#111111", cpp=CINDER, field="#FAFAFA")
DARK = dict(icon="#FAFAFA", word="#FAFAFA", cpp=CINDER, field="#111111")


def icon_paths():
    svg = open(os.path.join(ROOT, "svg", "icon", "icon-light.svg")).read()
    return re.findall(r'<path d="([^"]+)"', svg)


_font = None


def load_font():
    """The wordmark's font: Llama Sans cut to WORDMARK, as a TTFont, with its bytes kept for HarfBuzz."""
    global _font
    if _font is None:
        font = instantiateVariableFont(TTFont(FONT), WORDMARK, inplace=False, overlap=OverlapMode.REMOVE)
        buf = io.BytesIO()
        font.save(buf)
        _font = TTFont(io.BytesIO(buf.getvalue())), buf.getvalue()
    return _font[0]


def shaped(text):
    """HarfBuzz's glyphs and positions for `text` in the font: [(glyph id, x offset, x advance)]."""
    load_font()
    face = hb.Face(hb.Blob(_font[1]))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb.Font(face), buf, {"kern": True, "liga": True})
    return [(i.codepoint, i.cluster, p.x_offset, p.x_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def proportions(font, text):
    """The lockup's geometry from the font's capital icon: the cap height (px) when the icon is ICON_SIZE tall, the
    baseline that centres the capitals on the icon, and where the first letter's ink starts, as typed after the icon
    and a space."""
    cap = font["OS/2"].sCapHeight
    glyphs = shaped(CAPITAL_ICON + " " + text[0])
    order, glyf = font.getGlyphOrder(), font["glyf"]
    icon, first = glyf[order[glyphs[0][0]]], glyf[order[glyphs[2][0]]]
    for g in (icon, first):
        g.recalcBounds(glyf)
    k = ICON_SIZE / (icon.yMax - icon.yMin)  # px per font unit
    ink_gap = glyphs[0][3] + glyphs[1][3] + first.xMin - icon.xMax
    return cap * k, ICON_TOP + ICON_SIZE / 2 + cap * k / 2, ICON_SIZE + ink_gap * k


def wordmark(font, text, split, x, k, baseline):
    """Two outlines of `text`, set from x on `baseline` at scale k: the characters before `split`, then the rest."""
    gs, order = font.getGlyphSet(), font.getGlyphOrder()
    ntos = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
    pens = [SVGPathPen(gs, ntos=ntos), SVGPathPen(gs, ntos=ntos)]
    for gid, cluster, offset, advance in shaped(text):
        pen = pens[cluster >= split]
        gs[order[gid]].draw(TransformPen(pen, (k, 0, 0, -k, x + offset * k, baseline)))
        x += advance * k
    return [p.getCommands() for p in pens], x


def lockup(font, name, colours, dx=0, dy=0):
    """The paths of one lockup, offset by (dx, dy), and its width."""
    text = "llama.cpp" if name == "llama-cpp" else "Llama"  # llama.cpp is always lowercase, Llama capitalised
    cap_height, baseline, word_left = proportions(font, text)
    k = cap_height / font["OS/2"].sCapHeight
    first = shaped(text[0])[0][0]
    x0 = word_left - font["glyf"][font.getGlyphOrder()[first]].xMin * k
    s = ICON_SIZE / 600
    group = f'<g transform="translate({dx} {dy})">'
    group += "".join(f'<path transform="translate(0 {ICON_TOP}) scale({s:.6f})" d="{d}" fill="{colours["icon"]}"/>'
                     for d in icon_paths())
    (word, cpp), x = wordmark(font, text, 5, x0, k, baseline)
    group += f'<path d="{word}" fill="{colours["word"]}"/>'
    if cpp:
        group += f'<path d="{cpp}" fill="{colours["cpp"]}"/>'
    return group + "</g>", round(x)


def svg(width, height, body):
    return (f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg">\n{body}\n</svg>\n')


def on_field(body, w, h, colours, lift=0):
    """A mark drawn on a w × h canvas (body), set on its field: scaled to leave FIELD_MARGIN all round, centred,
    and raised by lift of its own height."""
    m = FIELD_MARGIN * min(w, h)
    s = min((w - 2 * m) / w, (h - 2 * m) / h)
    x, y = (w - w * s) / 2, (h - h * s) / 2 - lift * h * s
    return svg(w, h, f'<rect width="{w}" height="{h}" fill="{colours["field"]}"/>\n'
                     f'<g transform="translate({x:.3f} {y:.3f}) scale({s:.6f})">{body}</g>')


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    font = load_font()
    for mode, colours in (("light", LIGHT), ("dark", DARK)):
        icon = "".join(f'<path d="{d}" fill="{colours["icon"]}"/>' for d in icon_paths())
        write(os.path.join(ROOT, "svg", "icon", f"icon-{mode}-bg.svg"), on_field(icon, 600, 600, colours, OPTICAL_LIFT))
    for name in ("llama", "llama-cpp"):
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            body, width = lockup(font, name, colours)
            write(os.path.join(ROOT, "svg", "lockup", name, f"logo-{name}-{mode}.svg"), svg(width, LOCKUP_H, body))
            write(os.path.join(ROOT, "svg", "lockup", name, f"logo-{name}-{mode}-bg.svg"),
                  on_field(body, width, LOCKUP_H, colours))
        _, width = lockup(font, name, LIGHT)
        dx, dy = (COVER_W - width) / 2, (COVER_H - LOCKUP_H) / 2
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            body, _ = lockup(font, name, colours, dx, dy)
            field = f'<rect width="{COVER_W}" height="{COVER_H}" fill="{colours["field"]}"/>\n'
            write(os.path.join(ROOT, "svg", "cover", name, f"cover-{name}-{mode}.svg"), svg(COVER_W, COVER_H, field + body))
