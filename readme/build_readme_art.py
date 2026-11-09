"""Builds the README's artwork in readme/: a specimen card for Llama Sans and one for Llama Mono, a palette card, and a
swatch per colour for the README's colour table, each card in a light and a dark version.

Text is shaped with HarfBuzz from the fonts in fonts/variable/ and outlined, as the logo's lockups are, so GitHub
shows the real typefaces without loading a font. Colours are the ones in css/colors.css. Run it again after a change
to the fonts or the colours.

Run:  uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python readme/build_readme_art.py
"""
import io
import os
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont
import uharfbuzz as hb

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts", "variable")
SANS, MONO = "LlamaSans[opsz,wght].ttf", "LlamaMono[wght].ttf"

INK, LIGHT, CINDER = "#111111", "#FAFAFA", "#EE6C1E"
# the cards' grounds and inks: muted text at 62% of the ink, hairlines at 10%, as on communications' light and dark
GROUNDS = {
    "light": dict(bg=LIGHT, ink=INK, muted="rgb(17 17 17 / 0.62)", line="rgb(17 17 17 / 0.1)"),
    "dark": dict(bg=INK, ink=LIGHT, muted="rgb(250 250 250 / 0.62)", line="rgb(250 250 250 / 0.13)"),
}

# the palette, as css/colors.css has it, in sRGB hex
COLOURS = [
    ("Ink", "brand-ink", "#111111"),
    ("Light", "brand-light", "#FAFAFA"),
    ("Sand 50", "sand-50", "#F7F3EC"),
    ("Sand 100", "sand-100", "#EFE9DF"),
    ("Sand ink", "sand-900", "#2B2620"),
    ("Cinder", "art-cinder", "#EE6C1E"),
    ("Cinder light", "art-cinder-light", "#F3C1AB"),
    ("Day sky", "art-day-sky", "#8FBDE5"),
    ("Night sky", "art-night-sky", "#1B3659"),
]

_fonts = {}


def font(path, **location):
    """The font at `path`, cut at `location` on its axes, with its bytes kept for HarfBuzz."""
    key = (path, tuple(sorted(location.items())))
    if key not in _fonts:
        cut = instantiateVariableFont(TTFont(os.path.join(FONTS, path)), location, inplace=False,
                                      overlap=OverlapMode.REMOVE)
        buf = io.BytesIO()
        cut.save(buf)
        cut = TTFont(io.BytesIO(buf.getvalue()))
        cut.hb = buf.getvalue()
        _fonts[key] = cut
    return _fonts[key]


def text(f, s, x, y, size, fill, tracking=0):
    """`s` set in font `f` at `size` px with its baseline at (x, y), as a <path>; returns (svg, width)."""
    face = hb.Face(hb.Blob(f.hb))
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(hb.Font(face), buf, {"kern": True, "liga": True, "calt": True})
    k = size / f["head"].unitsPerEm
    gs, order = f.getGlyphSet(), f.getGlyphOrder()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    pos = 0
    for info, p in zip(buf.glyph_infos, buf.glyph_positions):
        gs[order[info.codepoint]].draw(TransformPen(pen, (k, 0, 0, -k, x + (pos + p.x_offset) * k, y)))
        pos += p.x_advance + tracking * f["head"].unitsPerEm
    width = pos * k
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>', width


def card(w, h, g, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="24" fill="{g["bg"]}" stroke="{g["line"]}"/>'
            f'{"".join(body)}</svg>\n')


def fits(width, limit, what):
    assert width <= limit, f"{what} is {width:.0f} px wide, over {limit}"


def sans_card(g):
    W, H, M = 1600, 900, 96
    label = font(MONO, wght=500)
    body = []
    t, _ = text(label, "LLAMA SANS", M, M + 20, 24, g["muted"], tracking=0.08)
    body.append(t)
    t, w = text(font(SANS, wght=700, opsz=40), "Simple by default,", M, 268, 112, g["ink"])
    fits(w, W - 2 * M, "headline")
    body.append(t)
    t, w = text(font(SANS, wght=700, opsz=40), "powerful on request.", M, 388, 112, g["ink"])
    fits(w, W - 2 * M, "headline")
    body.append(t)
    t, _ = text(font(SANS, wght=400, opsz=24), "One variable font, from 400 to 700, with an optical size from 16 to 40.",
                M, 470, 34, g["muted"])
    body.append(t)
    # the four weights, at the UI end
    x = M
    for name, wght in (("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)):
        t, w = text(font(SANS, wght=wght, opsz=16), name, x, 600, 52, g["ink"])
        body.append(t)
        x += w + 56
    fits(x - 56 - M, W - 2 * M, "weights")
    body.append(f'<rect x="{M}" y="650" width="{W - 2 * M}" height="1" fill="{g["line"]}"/>')
    for i, line in enumerate(("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz 0123456789")):
        t, w = text(font(SANS, wght=400, opsz=16), line, M, 730 + i * 64, 44, g["ink"], tracking=0.01)
        fits(w, W - 2 * M, line)
        body.append(t)
    # the icon glyph, top right, at the headline's cap height
    t, w = text(font(SANS, wght=700, opsz=40), "", 0, 0, 72, g["ink"])
    body.append(t.replace("<path ", f'<path transform="translate({W - M - w} {M + 52})" ', 1))
    return card(W, H, g, body)


def mono_card(g):
    W, H, M = 1600, 760, 96
    mono, bold, label = font(MONO, wght=400), font(MONO, wght=700), font(MONO, wght=500)
    body = []
    t, _ = text(label, "LLAMA MONO", M, M + 20, 24, g["muted"], tracking=0.08)
    body.append(t)
    t, _ = text(bold, "llama.cpp", M, 248, 112, g["ink"])
    body.append(t)
    t, _ = text(font(SANS, wght=400, opsz=24), "Every character in one cell, coding ligatures included.", M, 324, 34,
                g["muted"])
    body.append(t)
    body.append(f'<rect x="{M}" y="380" width="{W - 2 * M}" height="1" fill="{g["line"]}"/>')
    # a command, its prompt muted and its flag in cinder
    size, y = 40, 470
    x = M
    for part, fill in (("$ ", g["muted"]), ("llama-server ", g["ink"]), ("-hf ", CINDER),
                       ("ggml-org/gemma-3-4b-it-GGUF", g["ink"])):
        t, w = text(mono, part, x, y, size, fill)
        body.append(t)
        x += w
    fits(x - M, W - 2 * M, "command")
    for i, line in enumerate(("const ok = (a, b) => a !== b && a >= 0;", "0O 1lI| {} [] () -> :: != www")):
        t, w = text(mono, line, M, 560 + i * 64, size, g["ink"])
        fits(w, W - 2 * M, line)
        body.append(t)
    return card(W, H, g, body)


def palette_card(g):
    W, H, M = 1600, 640, 96
    label, name_font = font(MONO, wght=400), font(SANS, wght=600, opsz=16)
    body = []
    t, _ = text(font(MONO, wght=500), "COLOURS", M, M + 20, 24, g["muted"], tracking=0.08)
    body.append(t)
    gap = 16
    n = len(COLOURS)
    tile = (W - 2 * M - gap * (n - 1)) / n
    top = 176
    for i, (name, _, hex_) in enumerate(COLOURS):
        x = M + i * (tile + gap)
        body.append(f'<rect x="{x:.1f}" y="{top}" width="{tile:.1f}" height="{tile * 1.4:.1f}" rx="16" '
                    f'fill="{hex_}" stroke="{g["line"]}"/>')
        t, w = text(name_font, name, x, top + tile * 1.4 + 40, 22, g["ink"])
        fits(w, tile + gap, name)
        body.append(t)
        t, _ = text(label, hex_.lower(), x, top + tile * 1.4 + 72, 20, g["muted"])
        body.append(t)
    # the two skies as grounds, after llama.app's hero
    y = top + tile * 1.4 + 112
    half = (W - 2 * M - gap) / 2
    body.append(
        '<defs>'
        '<linearGradient id="day" x1="0.3" y1="0" x2="0.7" y2="1">'
        '<stop offset="0" stop-color="#C4DDF6"/><stop offset="0.55" stop-color="#D0E4F7"/>'
        '<stop offset="1" stop-color="#DFECF9"/></linearGradient>'
        '<radialGradient id="day-glow" cx="0.15" cy="0.1" r="0.6">'
        '<stop offset="0" stop-color="#DCECFB"/><stop offset="1" stop-color="#DCECFB" stop-opacity="0"/>'
        '</radialGradient>'
        '<linearGradient id="night" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#0F1A2B"/><stop offset="0.55" stop-color="#13213A"/>'
        '<stop offset="1" stop-color="#182A45"/></linearGradient>'
        '<radialGradient id="night-glow" cx="0.5" cy="1.15" r="0.7">'
        '<stop offset="0" stop-color="#2E4668" stop-opacity="0.35"/>'
        '<stop offset="1" stop-color="#2E4668" stop-opacity="0"/></radialGradient>'
        '</defs>')
    for i, (sky, ink) in enumerate((("day", INK), ("night", LIGHT))):
        x = M + i * (half + gap)
        for fill in (sky, f"{sky}-glow"):
            body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{half:.1f}" height="64" rx="16" fill="url(#{fill})"/>')
        t, _ = text(label, f"--gradient-{sky}-sky", x + 24, y + 40, 20, ink)
        body.append(t)
    return card(W, H, g, body)


def swatch(hex_):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
            f'<rect x="0.5" y="0.5" width="39" height="39" rx="8" fill="{hex_}" stroke="rgb(128 128 128 / 0.4)"/>'
            f'</svg>\n')


def write(name, svg):
    path = os.path.join(HERE, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(svg)
    print(os.path.relpath(path, os.path.join(HERE, "..")))


for tone, g in GROUNDS.items():
    write(f"llama-sans-{tone}.svg", sans_card(g))
    write(f"llama-mono-{tone}.svg", mono_card(g))
    write(f"colours-{tone}.svg", palette_card(g))
for _, token, hex_ in COLOURS:
    write(f"swatches/{token}.svg", swatch(hex_))
