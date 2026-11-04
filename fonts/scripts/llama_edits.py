"""Outline edits shared by the Llama Sans build (see build_llama_sans.py).

Starting from Geist (SIL Open Font License 1.1, no Reserved Font Name), these functions
reshape outlines toward a Swiss neo-grotesk: curved terminals are trimmed back and re-cut
at an angle, quarter curves are eased toward circular, the a and l lose their curled feet,
and the straight-sided ends of r, t and f are angled. The constants below set how far.

Contours are lists of ("L", (a, b)) and ("C", (p0, h1, h2, p3)) segments.
"""
import math
from fontTools.ttLib.tables import ttProgram

OPEN = 4         # how far every curved terminal is trimmed back along the stroke (font units), same for all glyphs
OPEN_BY_GLYPH = {"a": -10, "S": 12, "s": 12}  # a: hook runs past Geist's; S, s: a little more open
TK = 0.2         # cut angle: 0 = square to the stroke, 1 = horizontal
TK_BY_GLYPH = {"a": 1.0, "S": 0.3, "s": 0.3}  # a: top terminal cut flat; S, s: cut a little more toward horizontal
ROUND = 0.55     # 0 = Geist's curve tension, 1 = circular
T_TOP_DROP = 32  # the t's stem top: how far its left corner drops, angling the cut
T_FOOT_SLIDE = 26  # the t's foot end: how far its bottom corner slides in, angling the cut (0 = upright)
CIRCLE = 0.5523  # cubic handle ratio of a circular quarter


# ---------- cubic helpers ----------

def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def split(c, t):
    """De Casteljau split of cubic c at t (t outside 0..1 extrapolates)."""
    p0, p1, p2, p3 = c
    a, b, cc = lerp(p0, p1, t), lerp(p1, p2, t), lerp(p2, p3, t)
    d, e = lerp(a, b, t), lerp(b, cc, t)
    f = lerp(d, e, t)
    return (p0, a, d, f), (f, e, cc, p3)


def point(c, t):
    return split(c, t)[0][3]


def tangent(c, t):
    p0, p1, p2, p3 = c
    u = 1 - t
    x = 3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0])
    y = 3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    l = math.hypot(x, y) or 1
    return (x / l, y / l)


def t_at_length_from_end(c, L, n=200):
    """Parameter whose arc length back from t=1 is L (negative L extends past the end)."""
    if L <= 0:
        # extrapolate along the end tangent's parameter speed
        p0, p1, p2, p3 = c
        speed = 3 * math.hypot(p3[0] - p2[0], p3[1] - p2[1]) or 1
        return 1 - L / speed
    acc, prev = 0.0, point(c, 1)
    for i in range(1, n + 1):
        t = 1 - i / n
        q = point(c, t)
        acc += math.hypot(q[0] - prev[0], q[1] - prev[1])
        if acc >= L:
            return t
        prev = q
    return 0.0


def length(c, n=60):
    pts = [point(c, i / n) for i in range(n + 1)]
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def reverse(c):
    return (c[3], c[2], c[1], c[0])


# ---------- contour model ----------

# ---------- 1. terminals ----------

def is_terminal(segs, i, metrics, stem):
    if segs[i][0] != "L":
        return False
    a, b = segs[i][1]
    prev, nxt = segs[i - 1], segs[(i + 1) % len(segs)]
    if prev[0] != "C" or nxt[0] != "C":
        return False
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(dx, dy)
    # Geist's terminal cuts are near-flat (slope ~0.07); the a's bowl-to-stem join (~0.2) is not one
    if not 0.6 * stem <= l <= 1.5 * stem or abs(dy) > 0.12 * abs(dx):
        return False
    return not any(abs(a[1] - m) < 1 and abs(b[1] - m) < 1 for m in metrics)


def recut(segs, i, open_len, k=TK):
    """Trim the curves either side of terminal segment i and re-cut it at an angle."""
    n = len(segs)
    A = segs[i - 1][1]                 # curve arriving at the cut
    B = reverse(segs[(i + 1) % n][1])  # curve leaving the cut, reversed so it also arrives at the cut

    def at(delta):
        tA = t_at_length_from_end(A, open_len + delta)
        tB = t_at_length_from_end(B, open_len - delta)
        pa, pb = point(A, tA), point(B, tB)
        da, db = tangent(A, tA), tangent(B, tB)
        d = (da[0] + db[0], da[1] + db[1])
        dl = math.hypot(*d) or 1
        d = (d[0] / dl, d[1] / dl)               # stroke heading out through the cut
        cut = (pb[0] - pa[0], pb[1] - pa[1])
        perp = (-d[1], d[0])
        if perp[0] * cut[0] + perp[1] * cut[1] < 0:
            perp = (-perp[0], -perp[1])
        hor = (math.copysign(1, cut[0]), 0)
        tgt = ((1 - k) * perp[0] + k * hor[0], (1 - k) * perp[1] + k * hor[1])
        err = math.atan2(cut[0] * tgt[1] - cut[1] * tgt[0], cut[0] * tgt[0] + cut[1] * tgt[1])
        return err, tA, tB

    # bisection on the tilt: shift trimming from one side to the other until the cut hits its angle.
    # Never trim more than 75% of either curve, or short inner curves (heavy weights) fold over.
    LA, LB = length(A), length(B)
    open_len = min(open_len, 0.45 * min(LA, LB))
    lo = max(-open_len - 60, open_len - 0.75 * LB)
    hi = min(open_len + 60, 0.75 * LA - open_len)
    elo = at(lo)[0]
    for _ in range(40):
        mid = (lo + hi) / 2
        em = at(mid)[0]
        if (em > 0) == (elo > 0):
            lo, elo = mid, em
        else:
            hi = mid
    _, tA, tB = at((lo + hi) / 2)
    newA = split(A, tA)[0]
    newB = reverse(split(B, tB)[0])
    segs[i - 1] = ("C", newA)
    segs[i] = ("L", (newA[3], newB[0]))
    segs[(i + 1) % n] = ("C", newB)


def slide(segs, corner, direction, dist):
    """Move the on-curve point at `corner` along `direction`, carrying its adjacent handles."""
    dx, dy = direction[0] * dist, direction[1] * dist
    near = lambda p: abs(p[0] - corner[0]) < 2 and abs(p[1] - corner[1]) < 2
    mv = lambda p: (p[0] + dx, p[1] + dy)
    hit = False
    for i, (kind, pts) in enumerate(segs):
        pts = list(pts)
        if near(pts[-1]):
            pts[-1] = mv(pts[-1])
            if kind == "C":
                pts[2] = mv(pts[2])
            hit = True
        if near(pts[0]):
            pts[0] = mv(pts[0])
            if kind == "C":
                pts[1] = mv(pts[1])
            hit = True
        segs[i] = (kind, tuple(pts))
    return hit


def find_tailless(segs):
    """Indices of the stem's right edge (i) and of where the foot rejoins the stem (j), or None."""
    ends = [pts[-1] for _, pts in segs]
    # the stem's right edge: the long vertical line furthest right
    stems = [k for k, (kind, pts) in enumerate(segs)
             if kind == "L" and abs(pts[0][0] - pts[1][0]) < 1 and pts[0][1] - pts[1][1] > 100]
    if not stems:
        return None
    i = max(stems, key=lambda k: ends[k][0])
    xr = ends[i][0]
    # where the foot rejoins the stem's left edge, just above the baseline
    try:
        # (y ~77 in Geist's static fonts, ~110 in its variable masters)
        j = next(k for k in range(i + 1, len(segs)) if 60 < ends[k][1] < 130 and ends[k][0] < xr - 50)
    except StopIteration:
        return None
    return i, j


def apply_tailless(segs, i, j, foot=(0, 0, 0)):
    """Straight stem to the baseline. foot=(out, height, lip) adds a small bracketed foot: the stem's
    outer edge curves out concavely by `out`, from `height` down to a short vertical lip of `lip` units.
    (0, 0, 0) keeps it flat. Every segment is always present (collapsed when flat) so masters stay compatible."""
    x0 = segs[i][1][0][0]
    end = segs[j][1][-1]
    out, h, lip = foot
    new = [("L", ((x0, segs[i][1][0][1]), (x0, h))),
           ("C", ((x0, h), (x0, lip + (h - lip) * 0.45), (x0 + out * 0.45, lip), (x0 + out, lip))),
           ("L", ((x0 + out, lip), (x0 + out, 0))),
           ("L", ((x0 + out, 0), (end[0], 0))), ("L", ((end[0], 0), end))]
    segs[i:j + 1] = new


def steeper_bowl(segs_outer, segs_counter, drop):
    """Find the top of the a's bowl, the line running up into the stem, on the outside and on the counter
    (Suisse tilts it more steeply)."""
    outer = next(k for k, (kind, pts) in enumerate(segs_outer)
                 if kind == "L" and pts[1][0] - pts[0][0] > 120 and 0 < pts[1][1] - pts[0][1] < 0.4 * (pts[1][0] - pts[0][0]))
    inner = next(k for k, (kind, pts) in enumerate(segs_counter)
                 if kind == "L" and pts[0][0] - pts[1][0] > 120 and 0 < pts[0][1] - pts[1][1] < 0.4 * (pts[0][0] - pts[1][0]))
    return outer, inner


def plain_l(segs):
    """Swap Geist's curled foot on the l for a plain stem, as in Suisse."""
    tops = [pts[-1] for _, pts in segs if pts[-1][1] > 600]  # the stem's two top corners
    if len(tops) < 2:
        return False
    x0, x1 = min(p[0] for p in tops), max(p[0] for p in tops)
    top = max(p[1] for p in tops)
    segs[:] = [("L", ((x1, 0), (x0, 0))), ("L", ((x0, 0), (x0, top))),
               ("L", ((x0, top), (x1, top))), ("L", ((x1, top), (x1, 0)))]
    return True


def straight_ends(name, segs, scale):
    """Terminals Geist draws with straight sides (no curve to trim), found by shape so it works
    in every weight: returns (corner, direction, distance) slides that angle each cut."""
    ends = [pts[-1] for _, pts in segs]

    def lowest_of_rightmost(pool):
        if not pool:  # e.g. the f's crossbar, a separate contour in variable masters
            return None
        xm = max(p[0] for p in pool)
        col = sorted((p for p in pool if abs(p[0] - xm) < 1), key=lambda p: p[1])
        return col[0] if len(col) >= 2 else None

    out = []
    if name == "r":                                   # arm end: cut leans back at the bottom
        c = lowest_of_rightmost(ends)
        c and out.append((c, (-1, 0), 30 * scale))
    if name == "f":                                   # hook end, above the crossbar
        c = lowest_of_rightmost([p for p in ends if p[1] > 600])
        c and out.append((c, (-1, 0), 30 * scale))
    if name == "t":
        ym = max(p[1] for p in ends)                  # stem top: left corner drops
        top = sorted(p for p in ends if abs(p[1] - ym) < 1)
        # only the stem's top (variable masters draw the crossbar as its own overlapping contour)
        ym > 600 and len(top) >= 2 and out.append((top[0], (0, -1), T_TOP_DROP * scale))
        c = lowest_of_rightmost([p for p in ends if p[1] < 200])  # foot end
        c and T_FOOT_SLIDE and out.append((c, (-1, 0), T_FOOT_SLIDE * scale))
    return out


# ---------- 2. curves ----------

def axis(v):
    return abs(v[0]) < 0.5 or abs(v[1]) < 0.5


def round_curve(c, m=ROUND):
    p0, h1, h2, p3 = c
    v1 = (h1[0] - p0[0], h1[1] - p0[1])
    v2 = (h2[0] - p3[0], h2[1] - p3[1])
    if not (axis(v1) and axis(v2)) or (abs(v1[0]) < 0.5) == (abs(v2[0]) < 0.5):
        return c  # only extreme-to-extreme quarters with perpendicular handles
    if abs(v1[0]) >= 0.5:   # first handle horizontal, second vertical
        corner = (p3[0], p0[1])
    else:
        corner = (p0[0], p3[1])
    L1 = math.hypot(corner[0] - p0[0], corner[1] - p0[1])
    L2 = math.hypot(corner[0] - p3[0], corner[1] - p3[1])
    if L1 < 20 or L2 < 20:
        return c
    t1, t2 = math.hypot(*v1) / L1, math.hypot(*v2) / L2
    if not (CIRCLE < t1 < 0.85 and CIRCLE < t2 < 0.85):
        return c
    n1, n2 = t1 + (CIRCLE - t1) * m, t2 + (CIRCLE - t2) * m
    return (p0, lerp(p0, corner, n1), lerp(p3, corner, n2), p3)


# ---------- build ----------

def track(font, units):
    """Tighten (or loosen) every glyph that has width, half from each side. Every simple
    glyph moves, marks included, so composites and mark anchors keep their relative positions."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    shift = units / 2
    for name in font.getGlyphOrder():
        g = glyf[name]
        if not g.isComposite() and g.numberOfContours > 0:
            g.coordinates.translate((round(shift), 0))
        adv, lsb = hmtx[name]
        if adv > 0:
            hmtx[name] = (adv + units, lsb)


def refit(font, base, new):
    """Set a footless glyph's advance, and move every composite built on it by the same amount."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    delta = new - hmtx[base][0]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if name == base or (g.isComposite() and g.components[0].glyphName == base):
            hmtx[name] = (hmtx[name][0] + delta, hmtx[name][1])


def finish(font, style, family="Llama Sans"):
    # Hinting was written for Geist's points; drop it rather than ship it broken.
    for tag in ("fpgm", "prep", "cvt "):
        if tag in font:
            del font[tag]
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if not g.isComposite() and hasattr(g, "program"):
            g.program = ttProgram.Program()
            g.program.fromBytecode(b"")
    for name in font.getGlyphOrder():
        g = glyf[name]
        g.recalcBounds(glyf)
        adv = font["hmtx"][name][0]
        font["hmtx"][name] = (adv, getattr(g, "xMin", 0) if g.numberOfContours else 0)

    ps = family.replace(" ", "")
    nt = font["name"]
    for nid in (1, 2, 3, 4, 5, 6, 16, 17, 21, 22, 25):
        nt.removeNames(nameID=nid)
    names = {
        0: "Copyright 2024 The Geist Project Authors (https://github.com/vercel/geist-font). "
           "Modifications copyright 2026 the Llama Sans authors.",
        3: f"0.6;{ps}-{style}", 4: f"{family} {style}",
        5: "Version 0.600; draft based on Geist", 6: f"{ps}-{style}",
    }
    if style in ("Regular", "Bold"):   # style-linked pair
        names.update({1: family, 2: style})
    else:                              # other weights get their own legacy family, typographic names group them
        names.update({1: f"{family} {style}", 2: "Regular", 16: family, 17: style})
    for nid, s in names.items():
        nt.setName(s, nid, 3, 1, 0x409)
        nt.setName(s, nid, 1, 0, 0)


