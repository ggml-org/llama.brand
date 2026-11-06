"""Builds the Llama and llama.cpp lockups and covers in logo/svg/ from the current icon, Llama Sans and Llama Mono.

The icon comes from svg/icon/icon-light.svg; the wordmark is "Llama" in Llama Sans Bold at its Display optical size
(fonts/variable/LlamaSans[opsz,wght].ttf at wght 700, opsz 40) or "llama.cpp", always lowercase, in Llama Mono Bold
(fonts/variable/LlamaMono[wght].ttf at wght 700), shaped with HarfBuzz (so kerning applies) and outlined, so the logo
follows the fonts whenever they change. The icon is 520 px tall at the left of a 600 px lockup, and the lockup's
proportion is the font's own lockup icon (U+E002, in both fonts): the icon 1.24 times the cap height, centred on the
capitals, and the first letter as far after it as the glyph's advance puts it, so the lockup matches U+E002 typed
before the name. Each cover
is the lockup centred on a 7500 × 2500 field. The icon and each lockup also come on their background (-bg): the same canvas, the mark
centred on the light or dark field with an even margin, the icon optically centred (lifted and nudged left). Then render the WebP and PNG
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
FONTS = os.path.join(ROOT, "..", "fonts", "variable")
# each name's wordmark: its font and where on the axes it is cut. Llama in Llama Sans Bold, at the Display end of the
# optical size axis; llama.cpp in Llama Mono Bold
WORDMARKS = {
    "llama": ("LlamaSans[opsz,wght].ttf", {"wght": 700, "opsz": 40}),
    "llama-cpp": ("LlamaMono[wght].ttf", {"wght": 700}),
}
ICON_SIZE, ICON_TOP = 520, 40  # the icon in a 600 px lockup
LOCKUP_ICON = "\ue002"  # the fonts' lockup icon: the lockup takes its size and spacing from it
COVER_W, COVER_H, LOCKUP_H = 7500, 2500, 600
# the on-background versions: the same canvas as the transparent file, the mark centred on the field with an even
# margin of FIELD_MARGIN of the shorter side. The icon sits OPTICAL_LIFT of its height above centre and OPTICAL_NUDGE
# of its width left of it. Its weight is low (the wide bottom bar), so mathematically centred it reads as sitting low;
# lifted and nudged so, a circle round it (the avatars' crop, the PWA icon) clears its three pairs of outer points
# nearly evenly: the rounded corners (the blade's top left, the foot's bottom right), the sharp corners (the blade's
# top right, the foot's bottom left) and the tips at its middle (the blade's left, the foot's right). No placement
# evens all three, since the tips are even only without a nudge; this one keeps each pair within 2% of the side
FIELD_MARGIN = 0.12
OPTICAL_LIFT = 1 / 40
OPTICAL_NUDGE = 1 / 100

# colours: icon, wordmark, ".cpp", and the cover's field. The .cpp takes cinder, the brand's one accent orange
# (art-cinder in the design system, oklch(0.68 0.18 46))
CINDER = "#EE6C1E"
LIGHT = dict(icon="#111111", word="#111111", cpp=CINDER, field="#FAFAFA")
DARK = dict(icon="#FAFAFA", word="#FAFAFA", cpp=CINDER, field="#111111")


def icon_paths():
    svg = open(os.path.join(ROOT, "svg", "icon", "icon-light.svg")).read()
    return re.findall(r'<path d="([^"]+)"', svg)


_fonts = {}


def load_font(name):
    """The font of `name`'s wordmark, cut as WORDMARKS says, as a TTFont, with its bytes kept for HarfBuzz."""
    if name not in _fonts:
        path, location = WORDMARKS[name]
        font = instantiateVariableFont(TTFont(os.path.join(FONTS, path)), location, inplace=False,
                                       overlap=OverlapMode.REMOVE)
        buf = io.BytesIO()
        font.save(buf)
        font = TTFont(io.BytesIO(buf.getvalue()))
        font.hb = buf.getvalue()
        _fonts[name] = font
    return _fonts[name]


def shaped(font, text):
    """HarfBuzz's glyphs and positions for `text` in the font: [(glyph id, x offset, x advance)]."""
    face = hb.Face(hb.Blob(font.hb))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb.Font(face), buf, {"kern": True, "liga": True})
    return [(i.codepoint, i.cluster, p.x_offset, p.x_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def proportions(font, text):
    """The lockup's geometry from the font's lockup icon: the cap height (px) when the icon is ICON_SIZE tall, the
    baseline that centres the capitals on the icon, and where the first letter's ink starts, as typed after it."""
    cap = font["OS/2"].sCapHeight
    glyphs = shaped(font, LOCKUP_ICON + text[0])
    order, glyf = font.getGlyphOrder(), font["glyf"]
    icon, first = glyf[order[glyphs[0][0]]], glyf[order[glyphs[1][0]]]
    for g in (icon, first):
        g.recalcBounds(glyf)
    k = ICON_SIZE / (icon.yMax - icon.yMin)  # px per font unit
    ink_gap = glyphs[0][3] + first.xMin - icon.xMax
    return cap * k, ICON_TOP + ICON_SIZE / 2 + cap * k / 2, ICON_SIZE + ink_gap * k


def wordmark(font, text, split, x, k, baseline):
    """Two outlines of `text`, set from x on `baseline` at scale k: the characters before `split`, then the rest."""
    gs, order = font.getGlyphSet(), font.getGlyphOrder()
    ntos = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
    pens = [SVGPathPen(gs, ntos=ntos), SVGPathPen(gs, ntos=ntos)]
    for gid, cluster, offset, advance in shaped(font, text):
        pen = pens[cluster >= split]
        gs[order[gid]].draw(TransformPen(pen, (k, 0, 0, -k, x + offset * k, baseline)))
        x += advance * k
    return [p.getCommands() for p in pens], x


def lockup(name, colours, dx=0, dy=0):
    """The paths of one lockup, offset by (dx, dy), and its width."""
    text = "llama.cpp" if name == "llama-cpp" else "Llama"  # llama.cpp is always lowercase, Llama capitalised
    font = load_font(name)
    cap_height, baseline, word_left = proportions(font, text)
    k = cap_height / font["OS/2"].sCapHeight
    first = shaped(font, text[0])[0][0]
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


def on_field(body, w, h, colours, lift=0, nudge=0):
    """A mark drawn on a w × h canvas (body), set on its field: scaled to leave FIELD_MARGIN all round, centred,
    raised by lift of its own height and moved left by nudge of its width."""
    m = FIELD_MARGIN * min(w, h)
    s = min((w - 2 * m) / w, (h - 2 * m) / h)
    x, y = (w - w * s) / 2 - nudge * w * s, (h - h * s) / 2 - lift * h * s
    return svg(w, h, f'<rect width="{w}" height="{h}" fill="{colours["field"]}"/>\n'
                     f'<g transform="translate({x:.3f} {y:.3f}) scale({s:.6f})">{body}</g>')


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    for mode, colours in (("light", LIGHT), ("dark", DARK)):
        icon = "".join(f'<path d="{d}" fill="{colours["icon"]}"/>' for d in icon_paths())
        write(os.path.join(ROOT, "svg", "icon", f"icon-{mode}-bg.svg"), on_field(icon, 600, 600, colours, OPTICAL_LIFT, OPTICAL_NUDGE))
    for name in ("llama", "llama-cpp"):
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            body, width = lockup(name, colours)
            write(os.path.join(ROOT, "svg", "lockup", name, f"logo-{name}-{mode}.svg"), svg(width, LOCKUP_H, body))
            write(os.path.join(ROOT, "svg", "lockup", name, f"logo-{name}-{mode}-bg.svg"),
                  on_field(body, width, LOCKUP_H, colours))
        _, width = lockup(name, LIGHT)
        dx, dy = (COVER_W - width) / 2, (COVER_H - LOCKUP_H) / 2
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            body, _ = lockup(name, colours, dx, dy)
            field = f'<rect width="{COVER_W}" height="{COVER_H}" fill="{colours["field"]}"/>\n'
            write(os.path.join(ROOT, "svg", "cover", name, f"cover-{name}-{mode}.svg"), svg(COVER_W, COVER_H, field + body))
