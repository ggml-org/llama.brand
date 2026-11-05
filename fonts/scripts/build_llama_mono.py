"""Llama Mono variable font (wght 400–700), built from Geist Mono's variable font the way Llama Sans is built from Geist.

It takes the same three masters (design 400, 500, and 700 cut from Geist Mono at 650), the same axis (the design's
400–TOP_WEIGHT stretched over 400–700) and the same outline edits from build_llama_sans.py and llama_edits.py:
angle-cut terminals, rounder curves, the tailless a, angled r/t/f ends, the narrower t, UI's descenders and the
deeper stem joins. What differs is what a monospace font needs:

- Every glyph keeps Geist Mono's 600-unit cell. Where an edit changes how wide a drawing is (the a losing its tail,
  the narrower t, the stretched s), the drawing is shifted back so its middle sits where Geist Mono put it, rather
  than the advance narrowing. Accents on composites built on the t follow its stem.
- No tracking and no kerning: in a monospace font every character takes one cell, so there are no pairs to space.
- The l keeps Geist Mono's serifs (Sans makes it a plain stem), so l, 1, I and | stay apart in code.
- G and S keep Geist Mono's width: they already fill most of the cell, and Sans's 5–7% stretch would leave them
  under 30 units of sidebearing. The s, with room to spare, takes Sans's 3%.
- tt joins through contextual alternates (calt) instead of kerning: a t before another t runs its crossbar to the
  right edge of its cell, a t after one runs it to the left edge, so the bars meet across the cells as in Sans.
- Coding ligatures (-> => !== …) keep one cell per character. Geist Mono draws each ligature reaching back over the
  cells before it but substitutes the whole sequence with that one 600-unit glyph, so every ligature pulled the rest
  of the line a cell or more to the left. Each ligature now puts back an empty spacer cell (LIG) for every character
  it swallowed, before the ligature glyph, so `->` takes two cells, `!==` three, and columns stay in line.
- The Llama icon at U+E000 fits the cell (Sans's is cap-height wide, more than a cell) and centres on half the cap
  height, so it lines up with capitals.
- One version, set like Llama Sans UI: its descenders and its line box centred on the cap height.

Geist Mono is downloaded on first build (GEIST_MONO_URL, pinned to the same Geist commit) into sources/geist-mono/.

Run:  python scripts/build_llama_mono.py
      -> variable/LlamaMono[wght].ttf
         static/LlamaMono-{Regular,Medium,SemiBold,Bold}.ttf, cut from it
"""
import os
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
import llama_edits as bg
import build_llama_sans as sans

GEIST_MONO_URL = (f"https://raw.githubusercontent.com/vercel/geist-font/{sans.GEIST_COMMIT}"
                  "/fonts/GeistMono/variable/GeistMono%5Bwght%5D.ttf")
GEIST_MONO_SHA256 = "87c2aff9723544a9adaea19d92e42a33705c9723624801b6e0224c2206a6af0d"
GEIST_MONO_PATH = os.path.join("sources", "geist-mono", "GeistMono[wght].ttf")

FAMILY = "Llama Mono"
CELL = 600                                   # Geist Mono's advance; every spacing glyph gets it
UI = sans.SIZES[min(sans.SIZES)]             # Llama Sans at its text size (opsz 16)
DESCENDER = UI["descender"]                  # code is running text: the text size's descenders
LINE = sans.LINE                             # and Llama Sans's line box, centred on the cap height
WIDEN = {"s": sans.WIDEN["s"]}               # G and S keep Geist Mono's width (see above)
RECENTRE = {"a", "t", *WIDEN}                # drawings whose width the edits change
T_SHAPE = dict(left=0.95, right=0.90)    # Mono's t keeps longer arms than Sans's: its crossbar fills the cell
T_ACCENTED = {"tcaron"}                     # t-based glyphs Geist Mono draws whole rather than as composites
TT_OVERLAP = sans.TT_OVERLAP                 # how far each joined crossbar runs past its cell edge
TT_FORMS = {"t.tt1": "right", "t.tt2": "left", "t.tt3": "both"}  # before a t, after one, between two
TT_FEA = """
lookup tt_join {
    sub [t.tt1 t.tt3] t' t by t.tt3;
    sub [t.tt1 t.tt3] t' by t.tt2;
    sub t' t by t.tt1;
} tt_join;
feature calt { lookup tt_join; } calt;
"""
bg.COPYRIGHT = ("Copyright 2024 The Geist Project Authors (https://github.com/vercel/geist-font). "
                "Modifications copyright 2026 the Llama Mono authors.")


def ink_x(s):
    xs = [p[0] for segs in s for _, pts in segs for p in pts]
    return min(xs), max(xs)


def stem_x(s):
    """Left edge of the tallest contour's long vertical stem (the t's stem)."""
    segs = max(s, key=lambda segs: max(p[1] for _, pts in segs for p in pts))
    return min(pts[0][0] for kind, pts in segs if kind == "L" and abs(pts[0][0] - pts[1][0]) < 1
               and abs(pts[0][1] - pts[1][1]) > 200)


def stem_of(font):
    """The I's stem: Geist Mono's I has slab serifs, so it is measured between its two long vertical edges."""
    glyf = font["glyf"]
    coords, ends, _ = glyf["I"].getCoordinates(glyf)
    edges = {round(a[0]) for a, b in zip(coords, coords[1:]) if a[0] == b[0] and abs(a[1] - b[1]) > 300}
    return max(edges) - min(edges)


def shift_x(s, d):
    for segs in s:
        for i, (kind, pts) in enumerate(segs):
            segs[i] = (kind, tuple((p[0] + d, p[1]) for p in pts))


def joined_t(s, side):
    """A copy of the t with its crossbar (the contour that isn't the stem) run to one or both cell edges."""
    s = [list(segs) for segs in s]
    stem = max(range(len(s)), key=lambda ci: max(p[1] for _, pts in s[ci] for p in pts))
    for ci, segs in enumerate(s):
        if ci == stem:
            continue
        lo, hi = ink_x([segs])
        to = {lo: -TT_OVERLAP if side in ("left", "both") else lo,
              hi: CELL + TT_OVERLAP if side in ("right", "both") else hi}
        for i, (kind, pts) in enumerate(segs):
            segs[i] = (kind, tuple((to.get(p[0], p[0]), p[1]) for p in pts))
    return s


def build_masters(var):
    masters = [instantiateVariableFont(var, {"wght": g}, inplace=False, overlap=OverlapMode.KEEP_AND_SET_FLAGS,
                                       updateFontNames=False) for _, g in sans.MASTERS]
    for m in masters:
        sans.strip_hinting(m)
    ref = masters[0]
    os2 = ref["OS/2"]
    metrics = [0, os2.sxHeight, os2.sCapHeight]
    stems = [stem_of(m) for m in masters]
    scales = [s / 86 for s in stems]  # tuned on Regular's 86-unit I
    rev = {g: chr(u) for u, g in ref.getBestCmap().items()}
    order = ref.getGlyphOrder()
    for name in ["t"] + [n for n in order if n != "t"]:  # the t first: ť is drawn from it
        if any(m["glyf"][name].isComposite() or m["glyf"][name].numberOfContours <= 0 for m in masters):
            continue
        quads = [sans.read_contours(m["glyf"][name], m["glyf"]) for m in masters]
        plans = {(ci, si): sans.plan_spline(*pts) for ci, segs in enumerate(quads[0])
                 for si, (kind, pts) in enumerate(segs) if kind == "Q"}
        cubics = [sans.to_cubic(q, plans) for q in quads]
        if name in T_ACCENTED:  # Geist Mono draws ť whole: its accent, set on the finished t
            xh = os2.sxHeight
            cubics = [[[(k, tuple((p[0] + move, p[1]) for p in pts)) for k, pts in segs] for segs in s
                       if min(p[1] for _, pts in segs for p in pts) > xh] + [list(segs) for segs in t]
                      for s, t, move in zip(cubics, t_final, t_moves)]
            sans.write_compatible(name, cubics, masters)
            continue
        before = [ink_x(s) for s in cubics]
        if name == "t":
            t_stems = [stem_x(s) for s in cubics]
        sans.edit_glyph(name, cubics, scales, stems[0], metrics, rev, plain_l=False)
        if name in WIDEN:
            sans.widen(cubics, WIDEN[name])
        lower = (rev.get(name) or rev.get(name.split(".")[0], "")).islower()
        if lower:
            sans.shorten_descender(cubics, DESCENDER)
        if sans.JOIN_CUT and lower:
            joins = [(ci, j) for ci, segs in enumerate(cubics[0]) if (j := sans.find_joins(segs))]
            joins and sans.cut_joins(cubics, joins, sans.JOIN_CUT)
        if name == "t" and T_SHAPE:
            sans.shape_t(cubics, T_SHAPE["left"], T_SHAPE["right"])
        if name in RECENTRE:  # back to Geist Mono's middle of the drawing, in the same cell
            for s, (l, r) in zip(cubics, before):
                l2, r2 = ink_x(s)
                shift_x(s, (l + r - l2 - r2) / 2)
        sans.write_compatible(name, cubics, masters)
        if name == "t":
            t_moves = [stem_x(s) - x for s, x in zip(cubics, t_stems)]
            t_final = cubics
            for form, side in TT_FORMS.items():
                for m in masters:
                    m.setGlyphOrder(m.getGlyphOrder() + [form])
                    m["hmtx"][form] = (CELL, 0)
                sans.write_compatible(form, [joined_t(s, side) for s in cubics], masters)
    for m, move in zip(masters, t_moves):
        glyf = m["glyf"]
        for name in m.getGlyphOrder():  # accents on ť, ţ follow the stem
            c = glyf[name]
            if c.isComposite() and c.components[0].glyphName == "t":
                for comp in c.components[1:]:
                    comp.x += round(move)
        notdef = glyf[".notdef"]  # Geist Mono's .notdef is the only glyph not in the cell
        notdef.coordinates.translate(((CELL - m["hmtx"][".notdef"][0]) // 2, 0))
        m["hmtx"][".notdef"] = (CELL, 0)
        sans.add_icon(m, cell=CELL)
        add_spacer(m)
        sans.fix_lsb(m)
        sans.set_line_metrics(m, LINE)
    return masters


def add_calt(font, fea):
    """Append the features in `fea` (GSUB only) to the font's GSUB; see the Sans build's add_features."""
    sans.add_features(font, fea)


SPACER = "LIG"  # the empty cell a ligature puts back for each character it swallowed


def add_spacer(font):
    """An empty, unencoded glyph one cell wide."""
    from fontTools.ttLib.tables._g_l_y_f import Glyph
    font.setGlyphOrder(font.getGlyphOrder() + [SPACER])
    font["glyf"][SPACER] = Glyph()
    font["hmtx"][SPACER] = (CELL, 0)


def ligature_spacing_fea(font):
    """A liga lookup run after Geist Mono's own: each ligature glyph becomes spacers plus itself, one cell for every
    character the ligature replaced. Only the coding ligatures (*.liga), not Geist Mono's accent stacks or №."""
    sizes = {}
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for st in lookup.SubTable:
            st = getattr(st, "ExtSubTable", st)
            for ligs in (getattr(st, "ligatures", None) or {}).values():
                for lig in ligs:
                    if lig.LigGlyph.endswith(".liga"):
                        sizes[lig.LigGlyph] = len(lig.Component) + 1
    rules = "\n".join(f"    sub {g} by {' '.join([SPACER] * (n - 1))} {g};" for g, n in sorted(sizes.items()))
    return f"lookup liga_cells {{\n{rules}\n}} liga_cells;\nfeature liga {{ lookup liga_cells; }} liga;\n"


def check_cells(font):
    """Every glyph is one cell wide, but the zero-width combining marks."""
    marks = {g for g, c in font["GDEF"].table.GlyphClassDef.classDefs.items() if c == 3}
    bad = {g: a for g, (a, _) in font["hmtx"].metrics.items() if a != CELL and not (a == 0 and g in marks)}
    assert not bad, f"glyphs off the {CELL}-unit cell: {bad}"


if __name__ == "__main__":
    # options: a Geist Mono file to build from, --out=DIR (default: this folder, fonts/)
    args = sys.argv[1:]
    paths = [os.path.abspath(a) for a in args if not a.startswith("--")]
    out_dir = next((os.path.abspath(a[6:]) for a in args if a.startswith("--out=")), None)
    os.chdir(sans.ROOT)  # every path below is relative to fonts/, wherever this is run from
    out_dir = out_dir or "."
    var = TTFont(paths[0] if paths else sans.pinned_source(GEIST_MONO_PATH, GEIST_MONO_URL, GEIST_MONO_SHA256))
    for d in ("variable", "static"):
        os.makedirs(os.path.join(out_dir, d), exist_ok=True)
    vf = sans.build_variable(build_masters(var), FAMILY)
    add_calt(vf, TT_FEA + ligature_spacing_fea(vf))
    check_cells(vf)
    out = os.path.join(out_dir, "variable", "LlamaMono[wght].ttf")
    vf.save(out)
    print("wrote", out, [(a.axisTag, a.minValue, a.maxValue) for a in vf["fvar"].axes])
    sans.cut_statics(TTFont(out), FAMILY, out_dir)
