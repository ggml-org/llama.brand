"""Llama Sans, one variable font over weight (wght 400–700) and optical size (opsz 16–40), built from Geist's
variable font.

Geist (SIL Open Font License 1.1, no Reserved Font Name) supplies three masters: design weights 400
and 500 are Geist's 400 and 500, and design 700 is Geist at 650. The wght axis shows the design from 400
to TOP_WEIGHT (640), stretched over 400–700, so 500, 600 and 700 are the design's 480, 560 and 640.
Every change from llama_edits.py (angled terminals, rounder curves, the a and l,
angled r/t/f ends, tighter tracking) is decided once on the 400 master and applied to all
three, so the masters stay point-compatible and interpolate cleanly.

Geist's variable font is not stored in this repo: the first build downloads the pinned version
(GEIST_COMMIT) into sources/geist/ and checks its SHA-256 before using it.

Run:  python scripts/build_llama_sans.py
      -> variable/LlamaSans[opsz,wght].ttf
         static/LlamaSans-{Regular,Medium,SemiBold,Bold}.ttf, cut from it at opsz 16

The optical size axis runs between two settings of the same outlines (SIZES). At opsz 16, "UI", it is for
interfaces and running text: spaced and kerned after SF Pro's text sizes, with slightly deeper descenders. At opsz
40, "Display", it is for headlines: tight tracking and stronger kerning. Sizes in between blend, and browsers set
opsz from font-size on their own (font-optical-sizing: auto). Line spacing can't vary with opsz, so the whole axis
has UI's line box, centred on the cap height for buttons and cards; headlines and prose set their own line-height.
"""
import hashlib
import math
import os
import sys
import urllib.request
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.cu2qu import curves_to_quadratic
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, AxisDescriptor, InstanceDescriptor
from fontTools import varLib
from fontTools.otlLib.builder import buildStatTable
import llama_edits as bg

GEIST_COMMIT = "a0a06a3d916dcf92fe96f12051a124f89056b36a"  # vercel/geist-font, 2026-04-02
GEIST_URL = f"https://raw.githubusercontent.com/vercel/geist-font/{GEIST_COMMIT}/fonts/Geist/variable/Geist%5Bwght%5D.ttf"
GEIST_SHA256 = "73894e0448cae90a92b6c2f8732b7bb9acb7b94c418bff559dad4a18e1de9659"
GEIST_PATH = os.path.join("sources", "geist", "Geist[wght].ttf")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # fonts/, one level above scripts/

MASTERS = [(400, 400), (500, 500), (700, 650)]  # (design weight, Geist weight it is cut from)
# The axis: design weights 400–TOP_WEIGHT, stretched over wght 400–700, so wght 500, 600 and 700 are the design's
# 480, 560 and 640 (every 100 on the axis is 80 of the design). The design above TOP_WEIGHT is dropped.
TOP_WEIGHT = 640
# The optical size axis's two ends, by opsz (CSS px): tracking (units added to every advance), kerning (scale of
# Geist's pair kerning), the pair corrections and their size-specific fixes, and the descender depth.
SIZES = {
    # UI: interfaces and running text, spaced like SF Pro at 14–15 pt. Geist's kerning at 105% and the pair
    # corrections at 75%, then UI_KERN brings it to SF Pro's text kerning. A slight +3 tracking opens running text a
    # touch at small sizes, and its descenders run deeper, to `descender` units below the baseline.
    16: dict(name="UI", track=3, kern=1.05, pairs=0.75, fixes="UI_KERN", descender=155),
    # Display: headlines and big sizes, with tight tracking and stronger kerning.
    40: dict(name="Display", track=-22, kern=1.15, pairs=1.00, fixes="DISPLAY_KERN"),
}
# The line metrics for the whole axis (typo ascender, descender, line gap; win metrics stay at full height so
# nothing clips): a 1.25 em line box whose midline sits exactly at half the cap height ((980 - 270) / 2 = 355 =
# 710 / 2), so capitals and cap-height icons centre in buttons and chips with even padding; 12/16/20 px give
# whole-pixel 15/20/25 px lines. Headlines set a tighter line-height (1.15) in CSS.
LINE = (980, -270, 0)
NAMED = [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")]
STATICS = [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")]
A_FOOT = {700: (24, 72, 20)}  # per master: the a's bracketed foot (out, height, lip) — only near Bold
A_BOWL_DROP = 5               # units the a's bowl top rises where it meets the stem (negative: flatter than Geist)
A_BOWL_FILLET = 0             # radius rounding the corners where the bowl top meets the stem (0 = sharp)
ROUND_BY_GLYPH = {"G": 1.0, "S": 1.0, "s": 1.0}   # curve easing toward circular (default bg.ROUND = 0.55)
WIDEN = {"G": 1.05, "S": 1.07, "s": 1.03}         # horizontal stretch of the drawing, sidebearings kept
# The Llama icon (ggml-org/llama.brand, icon/icon-light.svg, 600 x 600), drawn into the font at U+E000.
# The brand assets are CC BY-NC 4.0: the font may only ship with this glyph once ggml-org allows it.
ICON_CODEPOINT = 0xE000
ICON_PATHS = [
    "M600 392L504.249 558L504.137 557.929C487.252 584.069 458.193 600 426.864 600H120L240 392H600Z",
    "M240 392H0L199.602 46.0254C216.032 17.5463 246.411 3.25756e-05 279.29 0H466.154L240 392Z",
]
ICON_SIDE = 60   # space either side of the icon, font units
CAP_RAISE = 0    # units added to the cap height (capitals scale up from the baseline; accents above them follow)
DESCENDER = 140  # how deep lowercase descenders reach (Geist's 150): p, q, j, y, and g's bowl in proportion;
                 # a version can set its own (FAMILIES' descender)
JOIN_CUT = 15    # how much deeper the notch where a bowl, arm or shoulder leaves a stem cuts into the joint (0 = Geist's)
T_SHAPE = dict(left=0.85, right=0.85)  # the t's arms, as a share of Geist's: crossbar left, crossbar and foot right (None = Geist's)
FIT_ERR = 1.5  # max deviation (font units) when a TrueType spline is refit as one cubic


# ---------- reading TrueType outlines with a structure every master shares ----------

def read_contours(glyph, glyf):
    """Contours as ("L", (a, b)) and ("Q", (p0, [offs], p1)) segments, starting on an on-curve point."""
    coords, ends, flags = glyph.getCoordinates(glyf)
    out, start = [], 0
    for end in ends:
        pts = [(tuple(coords[i]), bool(flags[i] & 1)) for i in range(start, end + 1)]
        start = end + 1
        if not any(on for _, on in pts):  # all off-curve: start on an implied point
            (a, _), (b, _) = pts[-1], pts[0]
            pts.insert(0, (((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), True))
        k = next(i for i, (_, on) in enumerate(pts) if on)
        pts = pts[k:] + pts[:k]
        segs, cur, offs = [], pts[0][0], []
        for p, on in pts[1:] + [pts[0]]:
            if on:
                segs.append(("L", (cur, p)) if not offs else ("Q", (cur, offs, p)))
                cur, offs = p, []
            else:
                offs.append(p)
        out.append(segs)
    return out


def quad_pieces(p0, offs, p1):
    """Split a TrueType spline into its quadratic pieces (implied on-curve points between offs)."""
    ons = [p0] + [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(offs, offs[1:])] + [p1]
    return [(ons[i], offs[i], ons[i + 1]) for i in range(len(offs))]


def sample(p0, offs, p1, n=8):
    pts = []
    for a, q, b in quad_pieces(p0, offs, p1):
        for i in range(n):
            t = i / n
            u = 1 - t
            pts.append((u * u * a[0] + 2 * u * t * q[0] + t * t * b[0], u * u * a[1] + 2 * u * t * q[1] + t * t * b[1]))
    pts.append(p1)
    return pts


def fit_cubic(p0, offs, p1):
    """One cubic through the spline's ends with its end tangents; returns (cubic, max error)."""
    if len(offs) == 1:  # a single quadratic raises to a cubic exactly
        q = offs[0]
        return (p0, bg.lerp(p0, q, 2 / 3), bg.lerp(p1, q, 2 / 3), p1), 0.0
    u = (offs[0][0] - p0[0], offs[0][1] - p0[1])
    v = (offs[-1][0] - p1[0], offs[-1][1] - p1[1])
    lu, lv = math.hypot(*u) or 1, math.hypot(*v) or 1
    u, v = (u[0] / lu, u[1] / lu), (v[0] / lv, v[1] / lv)
    pts = sample(p0, offs, p1)
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    ts = [x / d[-1] for x in d]
    # least squares for the two handle lengths
    a11 = a12 = a22 = b1 = b2 = 0.0
    for t, s in zip(ts, pts):
        m = 1 - t
        B0, B1, B2, B3 = m ** 3, 3 * m * m * t, 3 * m * t * t, t ** 3
        r = (s[0] - (B0 + B1) * p0[0] - (B2 + B3) * p1[0], s[1] - (B0 + B1) * p0[1] - (B2 + B3) * p1[1])
        uv = u[0] * v[0] + u[1] * v[1]
        a11 += B1 * B1; a12 += B1 * B2 * uv; a22 += B2 * B2
        b1 += B1 * (u[0] * r[0] + u[1] * r[1]); b2 += B2 * (v[0] * r[0] + v[1] * r[1])
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-9:
        return None, math.inf
    al, be = (b1 * a22 - b2 * a12) / det, (a11 * b2 - a12 * b1) / det
    if al <= 0 or be <= 0:
        return None, math.inf
    c = (p0, (p0[0] + u[0] * al, p0[1] + u[1] * al), (p1[0] + v[0] * be, p1[1] + v[1] * be), p1)
    err = max(math.hypot(bg.point(c, t)[0] - s[0], bg.point(c, t)[1] - s[1]) for t, s in zip(ts, pts))
    return c, err


def plan_spline(p0, offs, p1):
    """On the reference master: how to group the spline's off-curves so each group fits one cubic."""
    c, err = fit_cubic(p0, offs, p1)
    if err <= FIT_ERR or len(offs) == 1:
        return [len(offs)]
    k = len(offs) // 2
    mid = ((offs[k - 1][0] + offs[k][0]) / 2, (offs[k - 1][1] + offs[k][1]) / 2)
    return plan_spline(p0, offs[:k], mid) + plan_spline(mid, offs[k:], p1)


def to_cubic(contours, plans):
    """Turn every master's splines into cubics using the reference master's grouping."""
    out = []
    for ci, segs in enumerate(contours):
        new = []
        for si, (kind, pts) in enumerate(segs):
            if kind == "L":
                new.append(("L", pts))
                continue
            p0, offs, p1 = pts
            groups, k, start = plans[(ci, si)], 0, p0
            for gi, g in enumerate(groups):
                part = offs[k:k + g]
                k += g
                end = p1 if gi == len(groups) - 1 else ((offs[k - 1][0] + offs[k][0]) / 2, (offs[k - 1][1] + offs[k][1]) / 2)
                c, _ = fit_cubic(start, part, end)
                if c is None:  # degenerate in this master: straight-ish cubic along the chord
                    c = (start, bg.lerp(start, end, 1 / 3), bg.lerp(start, end, 2 / 3), end)
                new.append(("C", c))
                start = end
        out.append(new)
    return out


# ---------- edits: decided on the reference master, applied to all ----------

def stem_of(font):
    g = font["glyf"]["I"]
    g.recalcBounds(font["glyf"])
    return g.xMax - g.xMin


def edit_glyph(name, segs_by_master, scales, ref_stem, metrics, rev, plain_l=True):
    ref = segs_by_master[0]
    if name == "a":
        ij = bg.find_tailless(ref[0])
        assert ij, "the a's foot was not found; its outline structure changed"
        for s, (w, _) in zip(segs_by_master, MASTERS):
            bg.apply_tailless(s[0], *ij, A_FOOT.get(w, (0, 0, 0)))
        oi, ii = bg.steeper_bowl(ref[0], ref[1], A_BOWL_DROP)
        for s in segs_by_master:   # raise the ends at the stem: sharp corners, so nothing kinks
            bg.slide(s[0], s[0][oi][1][1], (0, 1), A_BOWL_DROP)   # outer bowl top meets the stem
            bg.slide(s[1], s[1][ii][1][0], (0, 1), A_BOWL_DROP)   # counter top meets the stem
        if A_BOWL_FILLET:
            for s, sc in zip(segs_by_master, scales):
                fillet(s[0], oi, A_BOWL_FILLET * sc ** 0.5)       # under the hat
                fillet(s[1], ii - 1, A_BOWL_FILLET * sc ** 0.5)   # inside the counter
    if name == "l" and plain_l:
        for s in segs_by_master:
            bg.plain_l(s[0])
    for ci, segs in enumerate(ref):
        # curves eased toward circular, where the reference master has a squared quarter
        for si, (kind, pts) in enumerate(segs):
            m = ROUND_BY_GLYPH.get(name, bg.ROUND)
            if kind == "C" and bg.round_curve(pts, m) != pts:
                for s in segs_by_master:
                    s[ci][si] = ("C", bg.round_curve(s[ci][si][1], m))
        # curved terminals: trimmed and re-cut
        for si in [j for j in range(len(segs)) if bg.is_terminal(segs, j, metrics, ref_stem)]:
            base = bg.OPEN_BY_GLYPH.get(name, bg.OPEN_BY_GLYPH.get(rev.get(name), bg.OPEN))
            k = bg.TK_BY_GLYPH.get(name, bg.TK)
            for s, sc in zip(segs_by_master, scales):
                bg.recut(s[ci], si, base * min(sc, 1.3), k)
        # straight-sided terminals: one corner slides along its edge
        ends = [pts[-1] for _, pts in segs]
        for corner, direction, dist in bg.straight_ends(name, segs, scales[0]):
            vi = min(range(len(ends)), key=lambda k: math.hypot(ends[k][0] - corner[0], ends[k][1] - corner[1]))
            for s, sc in zip(segs_by_master, scales):
                bg.slide(s[ci], s[ci][vi][1][-1], direction, dist / scales[0] * sc)


def _trim_end(seg, r):
    """Shorten a segment by r at its end; returns (new segment, new end point, heading there)."""
    kind, pts = seg
    if kind == "L":
        a, b = pts
        l = math.hypot(b[0] - a[0], b[1] - a[1])
        u = ((b[0] - a[0]) / l, (b[1] - a[1]) / l)
        e = (b[0] - u[0] * r, b[1] - u[1] * r)
        return ("L", (a, e)), e, u
    c = bg.split(pts, bg.t_at_length_from_end(pts, r))[0]
    return ("C", c), c[3], bg.tangent(c, 1)


def fillet(segs, k, r, handle=0.55):
    """Round the corner where segment k ends and the next begins, with a curve cutting r off each side."""
    n = len(segs)
    a_seg, a, u_in = _trim_end(segs[k], r)
    kind, pts = segs[(k + 1) % n]
    rev = ("L", (pts[1], pts[0])) if kind == "L" else ("C", bg.reverse(pts))
    b_rev, b, u_back = _trim_end(rev, r)
    b_seg = ("L", (b_rev[1][1], b_rev[1][0])) if kind == "L" else ("C", bg.reverse(b_rev[1]))
    h = handle * r
    corner = ("C", (a, (a[0] + u_in[0] * h, a[1] + u_in[1] * h), (b[0] + u_back[0] * h, b[1] + u_back[1] * h), b))
    segs[k] = a_seg
    segs[(k + 1) % n] = b_seg
    segs.insert(k + 1, corner)


def widen(segs_by_master, f):
    """Stretch every master's drawing horizontally by f from its left edge (the advance follows later)."""
    for s in segs_by_master:
        x0 = min(p[0] for segs in s for _, pts in segs for p in pts)
        for segs in s:
            for i, (kind, pts) in enumerate(segs):
                segs[i] = (kind, tuple((x0 + (p[0] - x0) * f, p[1]) for p in pts))


def shorten_descender(segs_by_master, depth, start=20):
    """Squeeze (or stretch) everything more than `start` units below the baseline, so a 150-unit descender reaches
    `depth`. The overshoot of rounds on the baseline sits above `start`, so it stays as drawn."""
    k = (depth - start) / (150 - start)
    for s in segs_by_master:
        for segs in s:
            for i, (kind, pts) in enumerate(segs):
                segs[i] = (kind, tuple((x, y if y >= -start else -start + (y + start) * k) for x, y in pts))


def find_joins(segs):
    """The notches where a bowl, arm or shoulder leaves a straight stem edge: a vertex where a long vertical line
    meets a curve at a sharp angle, directly or through a short step (n, h, r). Returns (vertices, handle, away):
    the vertex indices to move, the curve handle next to them, and the unit direction along the stem away from it."""
    def unit(a, b):
        d = math.dist(a, b)
        return ((b[0] - a[0]) / d, (b[1] - a[1]) / d) if d else (0, 0)

    def stem(seg):
        kind, pts = seg
        return kind == "L" and abs(pts[0][0] - pts[1][0]) <= 6 and abs(pts[0][1] - pts[1][1]) > 80

    out, n = [], len(segs)
    for k in range(n):  # vertex k joins segs[k] (ending there) and segs[k + 1] (starting there)
        a, b = segs[k], segs[(k + 1) % n]
        step = lambda seg: seg[0] == "L" and math.dist(*seg[1]) < 30
        if stem(a) and b[0] == "C":                                  # stem, then a curve
            v, line_end, vs, h = a[1][1], a[1][0], [k], ((k + 1) % n, 1)
        elif a[0] == "C" and stem(b):                                # a curve, then a stem
            v, line_end, vs, h = b[1][0], b[1][1], [k], (k, 2)
        elif stem(a) and step(b) and segs[(k + 2) % n][0] == "C":    # stem, a short step, then a curve
            v, line_end, vs, h = a[1][1], a[1][0], [k, (k + 1) % n], ((k + 2) % n, 1)
        elif a[0] == "C" and step(b) and stem(segs[(k + 2) % n]):    # a curve, a short step, then a stem
            nxt = segs[(k + 2) % n]
            v, line_end, vs, h = nxt[1][0], nxt[1][1], [k, (k + 1) % n], (k, 2)
        else:
            continue
        along = unit(v, line_end)                                    # from the joint up (or down) the stem
        tip = segs[h[0]][1][0 if h[1] == 1 else 3]
        if math.degrees(math.acos(max(-1, min(1, sum(x * y for x, y in zip(along, unit(tip, segs[h[0]][1][h[1]]))))))) < 60:
            out.append((vs, h, (-along[0], -along[1])))
    return out


def cut_joins(segs_by_master, joins, depth):
    """Slide each notch's vertices `depth` units deeper into the joint, and the curve's handle half as far."""
    for s in segs_by_master:
        for ci, found in joins:
            segs, n = s[ci], len(s[ci])

            def shift(si, idx, d):
                kind, pts = segs[si]
                pts = list(pts)
                pts[idx] = (pts[idx][0] + d[0], pts[idx][1] + d[1])
                segs[si] = (kind, tuple(pts))
            for vs, (hs, hi), away in found:
                d = (away[0] * depth, away[1] * depth)
                for k in vs:
                    shift(k, -1, d)
                    shift((k + 1) % n, 0, d)
                shift(hs, hi, (d[0] / 2, d[1] / 2))


def shape_t(segs_by_master, left, right):
    """Narrow the t: its arms (left of the stem, and right of it: crossbar and foot) cut to `left`/`right` of their
    length. The outer half of each arm moves as one piece, so the angled foot end and the hook keep their exact
    shape, and only the half next to the stem closes up. Returns per-master (left shift, total width removed)."""
    out = []
    for s in segs_by_master:
        stem_ci = max(range(len(s)), key=lambda ci: max(p[1] for _, pts in s[ci] for p in pts))
        xs = sorted({round(pts[0][0]) for kind, pts in s[stem_ci]   # the stem's two long vertical edges
                     if kind == "L" and abs(pts[0][0] - pts[1][0]) < 1 and abs(pts[0][1] - pts[1][1]) > 200})
        xl, xr = xs[0], xs[-1]
        old_l = min(p[0] for segs in s for _, pts in segs for p in pts)
        old_r = max(p[0] for segs in s for _, pts in segs for p in pts)
        dl, dr = (xl - old_l) * (1 - left), (old_r - xr) * (1 - right)  # what each side gives up
        zl, zr = (xl - old_l) / 2, (old_r - xr) / 2                      # the inner halves that take it

        def mv(p):
            x = p[0]
            if x > xr:
                x = xr + (x - xr) * (zr - dr) / zr if x - xr < zr else x - dr
            elif x < xl:
                x = xl - (xl - x) * (zl - dl) / zl if xl - x < zl else x + dl
            return (x - dl, p[1])  # keep the left sidebearing
        for segs in s:
            for i, (kind, pts) in enumerate(segs):
                segs[i] = (kind, tuple(mv(p) for p in pts))
        out.append((dl, dl + dr))
    return out


def add_icon(font, cell=None):
    """Draw the Llama icon in at U+E000: cap-height tall on the baseline, the same in every weight. With `cell`
    (a monospace advance), it shrinks to fit the cell with ICON_SIDE either side, centred on half the cap height."""
    from fontTools.svgLib.path import parse_path
    from fontTools.pens.transformPen import TransformPen
    cap = font["OS/2"].sCapHeight
    size = min(cap, cell - 2 * ICON_SIDE) if cell else cap
    k = size / 600
    top = (cap + size) / 2
    tt = TTGlyphPen(None)
    pen = TransformPen(Cu2QuPen(tt, max_err=0.5, reverse_direction=True), (k, 0, 0, -k, (cell - size) / 2 if cell else ICON_SIDE, top))
    for d in ICON_PATHS:
        parse_path(d, pen)
    g = tt.glyph()
    name = "uniE000"
    font.setGlyphOrder(font.getGlyphOrder() + [name])
    font["glyf"][name] = g
    g.recalcBounds(font["glyf"])
    font["hmtx"][name] = (cell or round(600 * k) + 2 * ICON_SIDE, g.xMin)
    for t in font["cmap"].tables:
        t.cmap[ICON_CODEPOINT] = name


def write_compatible(name, segs_by_master, masters):
    """Back to TrueType quadratics, converting each cubic in all masters at once so point counts match."""
    pens = [TTGlyphPen(None) for _ in masters]
    for ci in range(len(segs_by_master[0])):
        for pen, s in zip(pens, segs_by_master):
            pen.moveTo(s[ci][0][1][0])
        for si in range(len(segs_by_master[0][ci])):
            kinds = {s[ci][si][0] for s in segs_by_master}
            assert len(kinds) == 1, (name, ci, si, kinds)
            if kinds == {"L"}:
                for pen, s in zip(pens, segs_by_master):
                    pen.lineTo(s[ci][si][1][1])
            else:
                splines = curves_to_quadratic([list(s[ci][si][1]) for s in segs_by_master], [0.6] * len(masters))
                for pen, sp in zip(pens, splines):
                    pen.qCurveTo(*sp[1:])
        for pen in pens:
            pen.closePath()
    for pen, m in zip(pens, masters):
        g = pen.glyph()
        g.program = ttProgram.Program()
        g.program.fromBytecode(b"")
        if g.numberOfContours > 0:
            g.flags[0] |= 0x40  # OVERLAP_SIMPLE: masters keep Geist's overlapping contours
        m["glyf"][name] = g


def strip_hinting(font):
    for tag in ("fpgm", "prep", "cvt ", "STAT"):
        if tag in font:
            del font[tag]
    for name in font.getGlyphOrder():
        g = font["glyf"][name]
        if not g.isComposite() and hasattr(g, "program"):
            g.program = ttProgram.Program()
            g.program.fromBytecode(b"")


def fix_lsb(font):
    glyf, hmtx = font["glyf"], font["hmtx"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        g.recalcBounds(glyf)
        hmtx[name] = (hmtx[name][0], getattr(g, "xMin", 0) if g.numberOfContours else 0)


def pinned_source(path, url, sha256):
    """Path to a pinned source font, downloading it on first use and checking its SHA-256."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print("downloading", os.path.basename(path), "from vercel/geist-font @", GEIST_COMMIT[:7])
        with urllib.request.urlopen(url) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest != sha256:
        sys.exit(f"{path} does not match the pinned version (sha256 {digest}); delete it to re-download")
    return path


def geist_source():
    """Path to Geist's variable font, downloading the pinned version on first use."""
    return pinned_source(GEIST_PATH, GEIST_URL, GEIST_SHA256)


def build_masters(var, track, descender=DESCENDER):
    masters = [instantiateVariableFont(var, {"wght": g}, inplace=False, overlap=OverlapMode.KEEP_AND_SET_FLAGS,
                                       updateFontNames=False) for _, g in MASTERS]
    for m in masters:
        strip_hinting(m)
    ref = masters[0]
    os2 = ref["OS/2"]
    metrics = [0, os2.sxHeight, os2.sCapHeight]
    stems = [stem_of(m) for m in masters]
    scales = [s / 86 for s in stems]  # tuned on Regular's 86-unit I
    rev = {g: chr(u) for u, g in ref.getBestCmap().items()}
    for name in ref.getGlyphOrder():
        if any(m["glyf"][name].isComposite() or m["glyf"][name].numberOfContours <= 0 for m in masters):
            continue
        quads = [read_contours(m["glyf"][name], m["glyf"]) for m in masters]
        plans = {(ci, si): plan_spline(*pts) for ci, segs in enumerate(quads[0])
                 for si, (kind, pts) in enumerate(segs) if kind == "Q"}
        cubics = [to_cubic(q, plans) for q in quads]
        edit_glyph(name, cubics, scales, stems[0], metrics, rev)
        if name in WIDEN:
            widen(cubics, WIDEN[name])
        if descender != 150 and (rev.get(name) or rev.get(name.split(".")[0], "")).islower():
            shorten_descender(cubics, descender)
        if JOIN_CUT and (rev.get(name) or rev.get(name.split(".")[0], "")).islower():
            joins = [(ci, j) for ci, segs in enumerate(cubics[0]) if (j := find_joins(segs))]
            joins and cut_joins(cubics, joins, JOIN_CUT)
        if name == "t" and T_SHAPE:
            t_deltas = shape_t(cubics, T_SHAPE["left"], T_SHAPE["right"])
        write_compatible(name, cubics, masters)
    for m in masters:
        add_icon(m)
    for mi, ((w, _), m) in enumerate(zip(MASTERS, masters)):
        glyf = m["glyf"]
        for n in ("a", "u", "l"):
            glyf[n].recalcBounds(glyf)
        flare = A_FOOT.get(w, (0, 0, 0))[0]  # the foot may reach into the sidebearing; space from the stem
        bg.refit(m, "a", round(glyf["a"].xMax - flare + m["hmtx"]["u"][0] - glyf["u"].xMax))
        bg.refit(m, "l", m["hmtx"]["i"][0])
        for n, f in WIDEN.items():  # the stretched ink gets the extra width; marks on its composites re-centre
            g = glyf[n]
            g.recalcBounds(glyf)
            delta = round((g.xMax - g.xMin) * (1 - 1 / f))
            bg.refit(m, n, m["hmtx"][n][0] + delta)
            for name in m.getGlyphOrder():
                c = glyf[name]
                if c.isComposite() and c.components[0].glyphName == n:
                    for comp in c.components[1:]:
                        comp.x += delta // 2
        if T_SHAPE:  # the narrower t gives back its width; marks on ţ, ť follow the stem
            shift, removed = t_deltas[mi]
            bg.refit(m, "t", m["hmtx"]["t"][0] - round(removed))
            for name in m.getGlyphOrder():
                c = glyf[name]
                if c.isComposite() and c.components[0].glyphName == "t":
                    for comp in c.components[1:]:
                        comp.x -= round(shift)
        raise_caps(m, CAP_RAISE)
        bg.track(m, track)
        fix_lsb(m)
    return masters


def scale_kerning(font, k):
    """Scale every pair-kerning value (GPOS lookup type 2) by k."""
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType != 2:
            continue
        for st in lookup.SubTable:
            recs = []
            if st.Format == 1:
                recs = [r for ps in st.PairSet for r in ps.PairValueRecord]
                vals = [r.Value1 for r in recs] + [r.Value2 for r in recs]
            else:
                vals = [c2.Value1 for c1 in st.Class1Record for c2 in c1.Class2Record] + \
                       [c2.Value2 for c1 in st.Class1Record for c2 in c1.Class2Record]
            for v in vals:
                if v is not None and getattr(v, "XAdvance", None):
                    v.XAdvance = round(v.XAdvance * k)


def raise_caps(font, d):
    """Scale capital letters up from the baseline by d units at cap height, and move accents and
    mark anchors above them by d, so accented capitals keep their spacing."""
    if not d:
        return
    glyf, os2 = font["glyf"], font["OS/2"]
    cap = os2.sCapHeight
    f = (cap + d) / cap
    caps = {g for u, g in font.getBestCmap().items() if chr(u).isupper()}
    for name in caps:
        g = glyf[name]
        if not g.isComposite() and g.numberOfContours > 0:
            g.coordinates.scale((1, f))
    for name in caps:
        g = glyf[name]
        if g.isComposite():
            for comp in g.components[1:]:
                mark = glyf[comp.glyphName]
                mark.recalcBounds(glyf)
                if getattr(mark, "yMin", 0) + comp.y > cap / 2:   # marks above the capital
                    comp.y += d
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType != 4:  # mark-to-base: lift the anchors on capitals
            continue
        for st in lookup.SubTable:
            for gname, rec in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                if gname in caps:
                    for a in rec.BaseAnchor:
                        if a is not None and a.YCoordinate > cap / 2:
                            a.YCoordinate += d
    os2.sCapHeight = cap + d


# Optical pair corrections on top of Geist's kerning, measured on Display against nn (font units).
# Each group is (left letters, right letters, value); accented forms of each letter are included.
# Every version applies them, scaled by its "pairs" setting.
PAIR_KERN = [
    ("a", "nmrp", -19), ("a", "bhklij", -12), ("a", "u", -14), ("a", "s", -14),  # a's straight stem sits loose
    ("id", "nmrp", -18), ("nmh", "ij", -12),                                      # i, d and stems before n / i
    ("u", "nmrpu", -15), ("ug", "a", -16),
    ("S", "a", -12),
    ("L", "l", 12),                                                               # L|l a little more room
    ("nmh", "bhkl", -12),                                                         # stems before ascenders
    ("HIMN", "nmrp", -20),                                                        # straight capitals, then n
    ("HIMN", "K", -16),
    ("OQD", "HIMNBEFLPR", -20),                                                   # round capitals, then stems
]

# Kerning measured against SF Pro (macOS's SFNS.ttf, at 400) and fixed in here, so the build doesn't need it: for each
# group, the mean gap between SF's pair kerning and ours, added on top of everything above (1000-unit em). UI follows
# SF at its text size (opsz 17): harder after T, V, W, Y and around quotes, softer on L·V, A·V, F·A and r, k, x, f
# before rounds. Display keeps its own stronger kerning and only gains the pairs it had none for.
Q_OPEN, Q_CLOSE = "\u2018\u201c'\"", "\u2019\u201d'\""
UI_KERN = [
    ('T', 'a', -29), ('T', 'cdegoqs', -10), ('T', 'mnpr', -21), ('T', 'vwxyz', -7), ('T', '.,', 22),
    ('T', '-', -31), ('VW', 'cdegoqs', -5), ('VW', 'mnpru', 8), ('VW', '.,', -14), ('VW', '-', -49),
    ('Y', 'a', -15), ('Y', 'cdegoqs', -8), ('Y', 'mnpru', 8), ('Y', '.,', -98), ('Y', '-', -78), ('P', '.,', 18),
    ('F', 'a', -13), ('F', 'A', 50), ('P', 'A', 30), ('A', 'vwy', -5), ('A', 'VW', 52), ('VW', 'A', 52),
    ('A', 'T', 11), ('T', 'A', 11), ('L', 'VW', 100), ('L', 'Y', 75), ('L', 'T', 54), ('L', 'y', 16),
    ('L', Q_CLOSE, -26), ('A', Q_CLOSE, -62), (Q_OPEN, 'A', -62), (Q_CLOSE, 's', -27), (Q_OPEN, 's', -15),
    ('rvwy', '.,', -8), ('r', 'a', -2), ('r', 'cdoq', 15), ('r', 'e', 2), ('e', 'vwy', 19), ('vwy', 'eo', 7), ('y', 't', 8), ('a', 'vwy', 4),
    ('o', 'vwxy', 12), ('xk', 'ceo', 28), ('f', 'ceo', 24), ('r', 'vw', 29), ('r', 'y', 37), ('vwy', 'a', 5),
]
# In both versions r·e and r·a close up by hand, r·a the most: the open space under r's arm reads loose before
# them, and widest before a's low bowl (UI's ('r', 'e', 2) and ('r', 'a', -2) above, Display's here). UI's r·c, r·d,
# r·o and r·q sit a little closer than SF's too (15 rather than 27), so the slight tracking doesn't open them up.
# r·y opens a little the other way: r's arm and y's top sat almost touching. In Display, t before a tall stem
# (b, h, k, l) opens up a touch too: the crossbar and the stem read crowded at headline sizes.
TT_OVERLAP = 1   # t·t: how far the crossbars of a double t overlap, so they read as one bar (tt_join)
DISPLAY_KERN = [  # the first three: SF at opsz 28
    ("VW", "-", -29), ("Y", ".,", -88), ("Y", "-", -73), ("r", "e", -15), ("r", "a", -21), ("r", "y", 16), ("y", "t", 8),
    ("t", "bhkl", 10),
]


def add_kerning(font, groups, scale=1.0, composites=True):
    """Add pair kerning (values times scale) in its own lookup, appended to every 'kern' feature. With composites,
    each pair also covers the accented letters built on it."""
    from fontTools.otlLib.builder import buildPairPosGlyphs, buildLookup
    from fontTools.ttLib.tables import otTables
    cmap, glyf = font.getBestCmap(), font["glyf"]

    def forms(chars):  # each letter plus every composite built on it (á, ä, ň …)
        out = set()
        for ch in chars:
            base = cmap[ord(ch)]
            out.add(base)
            if composites:
                out.update(n for n in font.getGlyphOrder()
                           if glyf[n].isComposite() and glyf[n].components[0].glyphName == base)
        return out
    pairs = {}
    for left, right, v in groups:
        rec = otTables.ValueRecord()
        rec.XAdvance = round(v * scale)
        for a in forms(left):
            for b in forms(right):
                pairs[(a, b)] = (rec, None)
    gpos = font["GPOS"].table
    lookup = buildLookup(buildPairPosGlyphs(pairs, font.getReverseGlyphMap()))
    gpos.LookupList.Lookup.append(lookup)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    idx = gpos.LookupList.LookupCount - 1
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            fr.Feature.LookupListIndex.append(idx)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)


def tt_join(font, overlap=TT_OVERLAP):
    """The t·t kerning that butts one t's crossbar against the next's, `overlap` units over so no seam shows.
    Measured on this master's own outline: the crossbar is what lies in the band just under the x-height."""
    xh, glyf = font["OS/2"].sxHeight, font["glyf"]
    coords = [(x, y) for x, y in glyf["t"].getCoordinates(glyf)[0] if xh - 100 <= y <= xh + 1]
    left, right = min(x for x, _ in coords), max(x for x, _ in coords)
    return -round(font["hmtx"]["t"][0] - right + left) - overlap


def pair_kern(font, left, right):
    """The kerning `font` already gives left·right: every pair lookup in 'kern', by glyph or by class, summed."""
    gpos = font["GPOS"].table
    idx = {i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == "kern" for i in fr.Feature.LookupListIndex}
    total = 0
    for i in sorted(idx):
        for st in gpos.LookupList.Lookup[i].SubTable:
            st = getattr(st, "ExtSubTable", st)
            if getattr(st, "Format", 0) == 1 and hasattr(st, "PairSet") and left in st.Coverage.glyphs:
                recs = st.PairSet[st.Coverage.glyphs.index(left)].PairValueRecord
                total += sum(getattr(r.Value1, "XAdvance", 0) or 0 for r in recs if r.SecondGlyph == right)
            elif getattr(st, "Format", 0) == 2 and left in st.Coverage.glyphs:
                c1, c2 = st.ClassDef1.classDefs.get(left, 0), st.ClassDef2.classDefs.get(right, 0)
                total += getattr(st.Class1Record[c1].Class2Record[c2].Value1, "XAdvance", 0) or 0
    return total


def join_tt_liga(font, kern):
    """Set Geist's tt ligature (two t components) so its second t sits `kern` from the first: the crossbars then
    butt together exactly as the t·t kerning sets them, whether or not ligatures are on."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    g, adv = glyf["t_t.liga"], hmtx["t"][0]
    first, second = g.components
    assert first.glyphName == second.glyphName == "t", [c.glyphName for c in g.components]
    first.x, first.y, second.x, second.y = 0, 0, adv + kern, 0
    g.recalcBounds(glyf)
    hmtx["t_t.liga"] = (second.x + adv, g.xMin)


def set_line_metrics(font, line):
    asc, desc, gap = line
    # keep the line box's midline at half the (possibly raised) cap height
    shift = round(font["OS/2"].sCapHeight / 2 - (asc + desc) / 2)
    asc, desc = asc + shift, desc + shift
    os2, hhea = font["OS/2"], font["hhea"]
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = asc, desc, gap
    hhea.ascent, hhea.descent, hhea.lineGap = asc, desc, gap
    os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS: browsers and apps use the typo line spacing


def name_variable(vf, family, axes="wght"):
    nt = vf["name"]
    ps = family.replace(" ", "")
    for nid in (1, 2, 3, 4, 5, 6, 16, 17, 21, 22, 25):
        nt.removeNames(nameID=nid)
    for nid, s in {0: bg.COPYRIGHT,
                   1: family, 2: "Regular", 3: f"0.6;{ps}[{axes}]", 4: f"{family} Regular",
                   5: "Version 0.600; draft based on Geist", 6: f"{ps}-Regular", 25: ps}.items():
        nt.setName(s, nid, 3, 1, 0x409)
        nt.setName(s, nid, 1, 0, 0)


def axis_weight(w):
    """A design weight's place on the wght axis: 400 stays, TOP_WEIGHT lands on 700."""
    return 400 + (w - 400) * 300 / (TOP_WEIGHT - 400)


def build_variable(masters_by_size, family="Llama Sans"):
    """One variable font over wght and opsz from {opsz: masters}; the smallest opsz is the default."""
    ps = family.replace(" ", "")
    sizes = sorted(masters_by_size)
    ds = DesignSpaceDocument()
    # the weight masters go where the stretched axis puts them (700's beyond 700), then the axis is cut back to 400–700
    top = axis_weight(MASTERS[-1][0])
    for tag, name, lo, hi in (("wght", "Weight", 400, top), ("opsz", "Optical size", sizes[0], sizes[-1])):
        ax = AxisDescriptor()
        ax.tag, ax.name, ax.minimum, ax.default, ax.maximum = tag, name, lo, lo, hi
        ds.addAxis(ax)
    for size in sizes:
        for (w, _), m in zip(MASTERS, masters_by_size[size]):
            src = SourceDescriptor()
            src.font, src.location, src.familyName = m, {"Weight": axis_weight(w), "Optical size": size}, family
            src.styleName = f"{dict(NAMED)[w]} {SIZES[size]['name']}"
            ds.addSource(src)
    for w, style in NAMED:
        ins = InstanceDescriptor()
        ins.familyName, ins.styleName, ins.location = family, style, {"Weight": w, "Optical size": sizes[0]}
        ins.postScriptFontName = f"{ps}-{style}"
        ds.addInstance(ins)
    vf, _, _ = varLib.build(ds)
    if top > 700:
        vf = instantiateVariableFont(vf, {"wght": (400, 400, 700)}, inplace=False)
    name_variable(vf, family, "opsz,wght")
    buildStatTable(vf, [
        dict(tag="wght", name="Weight", values=[
            dict(value=w, name=s, flags=0x2 if w == 400 else 0, **({"linkedValue": 700} if w == 400 else {}))
            for w, s in NAMED]),
        dict(tag="opsz", name="Optical size", values=[
            dict(value=size, name=SIZES[size]["name"], flags=0x2 if size == sizes[0] else 0) for size in sizes]),
    ])
    vf["OS/2"].usWeightClass = 400
    return vf


def cut_statics(vf, family="Llama Sans", out_dir="."):
    ps = family.replace(" ", "")
    for w, style in STATICS:
        f = instantiateVariableFont(vf, {"wght": w, "opsz": min(SIZES)}, inplace=False, overlap=OverlapMode.REMOVE,
                                    updateFontNames=False)
        for tag in ("STAT",):
            if tag in f:
                del f[tag]
        os2 = f["OS/2"]
        os2.usWeightClass = w
        bold = style == "Bold"
        os2.fsSelection = (os2.fsSelection & ~0x61) | (0x20 if bold else 0x40)  # BOLD or REGULAR bit
        f["head"].macStyle = 1 if bold else 0
        bg.finish(f, style, family)
        out = os.path.join(out_dir, "static", f"{ps}-{style}.ttf")
        f.save(out)
        print("wrote", out)


if __name__ == "__main__":
    # options: a Geist file to build from, --out=DIR (default: this folder, fonts/)
    args = sys.argv[1:]
    paths = [os.path.abspath(a) for a in args if not a.startswith("--")]
    out_dir = next((os.path.abspath(a[6:]) for a in args if a.startswith("--out=")), None)
    JOIN_CUT = next((float(a[11:]) for a in args if a.startswith("--join-cut=")), JOIN_CUT)  # try another depth
    os.chdir(ROOT)  # every path below is relative to fonts/, wherever this is run from
    out_dir = out_dir or "."
    var = TTFont(paths[0] if paths else geist_source())
    for d in ("variable", "static"):
        os.makedirs(os.path.join(out_dir, d), exist_ok=True)
    masters_by_size = {}
    for size, cfg in SIZES.items():
        masters = build_masters(var, cfg["track"], cfg.get("descender", DESCENDER))
        for m in masters:
            scale_kerning(m, cfg["kern"])
            if cfg.get("pairs"):
                add_kerning(m, PAIR_KERN, cfg["pairs"])
            if cfg.get("fixes"):
                add_kerning(m, globals()[cfg["fixes"]])
            tt = tt_join(m)  # the whole t·t spacing; Geist's own t·t kerning is already part of it
            add_kerning(m, [("t", "t", tt - pair_kern(m, "t", "t"))], composites=False)  # ť and ţ keep their room
            join_tt_liga(m, tt)  # and the tt ligature, which liga turns "tt" into, matches it
            set_line_metrics(m, LINE)
        masters_by_size[size] = masters
    vf = build_variable(masters_by_size)
    out = os.path.join(out_dir, "variable", "LlamaSans[opsz,wght].ttf")
    vf.save(out)
    print("wrote", out, [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in vf["fvar"].axes])
    cut_statics(TTFont(out), "Llama Sans", out_dir)
