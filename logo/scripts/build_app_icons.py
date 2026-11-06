"""Builds the app icons in logo/svg/app/: the icon for a PWA, Apple's platforms, Android and Windows, and the web
UI's own five (logo/svg/app/web: its favicons, PWA, maskable and Apple touch icons, in its colours).

Each is the icon from svg/icon/icon-light.svg, light (the dark ink on the light field) and dark (the reverse), at the
size and in the shape each platform asks for, optically centred as in the -bg files and the avatars (lifted
OPTICAL_LIFT of its height and nudged OPTICAL_NUDGE of its width left). Full-bleed squares, which the platform masks to its own shape, carry the icon at SQUARE
of the side, as the web UI's maskable and Apple touch icons do, so it stays inside the 80% safe circle; the round PWA
icon is that at 85%, cut round; transparent icons leave the field out. render_webp.sh renders these at 1×, so the WebP
and PNG files have exactly these sizes.

Run:  uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_app_icons.py
"""
import os
from build_lockups import DARK, LIGHT, OPTICAL_LIFT, OPTICAL_NUDGE, ROOT, icon_paths, svg, write

SQUARE = 0.672  # the icon's share of a full-bleed square: the web UI's favicon (96%) with the generator's 30% padding
ROUND = 0.85 * SQUARE  # the round PWA icon: the maskable one at 85%, cut round
# macOS: Apple's icon grid, a 824 rounded square (radius 185.4) centred on the 1024 canvas, the icon at SQUARE of it
MACOS_BODY, MACOS_RADIUS = 824, 185.4
# Android's adaptive icon: 108 dp layers, of which launchers show at least the 66 dp circle; the icon fills 52% of
# the layer, so its outermost corners stay inside that circle
ADAPTIVE = 0.52
WINDOWS_ICON = 0.875  # the Windows app icon: transparent, a 1/16 margin all round, as Fluent's app icons
WINDOWS_TILE = 0.5  # on the Start and Store tiles, the icon at half the tile's height
FAVICON = 0.96  # the web UI's favicon: the icon with a 2% margin all round (its PWA_ASSET_GENERATOR.FAVICON_PADDING)
# the web UI's own colours (its pwa.constants.ts): the icon in ink on white, the dark favicon in light
WEB = dict(icon="#111111", field="#FFFFFF")
WEB_DARK = dict(icon="#FAFAFA")


def icon(colours, cx, cy, side):
    """The icon, side across, centred on cx cy, lifted OPTICAL_LIFT of its height and nudged OPTICAL_NUDGE left."""
    x, y = cx - side / 2 - side * OPTICAL_NUDGE, cy - side / 2 - side * OPTICAL_LIFT
    paths = "".join(f'<path d="{d}" fill="{colours["icon"]}"/>' for d in icon_paths())
    return f'<g transform="translate({x:.3f} {y:.3f}) scale({side / 600:.6f})">{paths}</g>'


def field(w, h, colours):
    return f'<rect width="{w}" height="{h}" fill="{colours["field"]}"/>\n'


def square(size, colours, share=SQUARE):
    """A full-bleed square, masked by the platform."""
    return svg(size, size, field(size, size, colours) + icon(colours, size / 2, size / 2, size * share))


def transparent(size, colours, share):
    return svg(size, size, icon(colours, size / 2, size / 2, size * share))


def pwa_round(size, colours):
    r = size / 2
    return svg(size, size, f'<circle cx="{r}" cy="{r}" r="{r}" fill="{colours["field"]}"/>\n'
                           + icon(colours, r, r, size * ROUND))


def macos(colours):
    size, body = 1024, MACOS_BODY
    o = (size - body) / 2
    plate = (f'<rect x="{o}" y="{o}" width="{body}" height="{body}" rx="{MACOS_RADIUS}" '
             f'fill="{colours["field"]}"/>\n')
    return svg(size, size, plate + icon(colours, size / 2, size / 2, body * SQUARE))


def tile(w, h, colours):
    return svg(w, h, field(w, h, colours) + icon(colours, w / 2, h / 2, h * WINDOWS_TILE))


# the web UI's five, as it ships them (each once, in its own colours): the favicon for light tabs and for dark ones,
# the round PWA icon, the maskable icon and the Apple touch icon
WEB_APP = [
    ("favicon", lambda: transparent(512, WEB, FAVICON)),
    ("favicon-dark", lambda: transparent(512, WEB_DARK, FAVICON)),
    ("pwa-512x512", lambda: pwa_round(512, WEB)),
    ("maskable-icon-512x512", lambda: square(512, WEB)),
    ("apple-touch-icon-180x180", lambda: square(180, WEB)),
]

# platform: (file name, builder) for each mode
APPS = {
    "pwa": [
        ("pwa-512x512", lambda c: pwa_round(512, c)),
        ("pwa-maskable-512x512", lambda c: square(512, c)),
    ],
    "apple": [
        ("apple-touch-icon-180x180", lambda c: square(180, c)),
        ("ios-1024x1024", lambda c: square(1024, c)),
        ("macos-1024x1024", macos),
    ],
    "android": [
        ("android-adaptive-foreground-432x432", lambda c: transparent(432, c, ADAPTIVE)),
        ("android-adaptive-background-432x432", lambda c: svg(432, 432, field(432, 432, c).rstrip())),
        ("android-play-512x512", lambda c: square(512, c)),
    ],
    "windows": [
        ("windows-app-icon-256x256", lambda c: transparent(256, c, WINDOWS_ICON)),
        ("windows-tile-150x150", lambda c: tile(150, 150, c)),
        ("windows-tile-wide-310x150", lambda c: tile(310, 150, c)),
    ],
}


if __name__ == "__main__":
    for platform, files in APPS.items():
        folder = os.path.join(ROOT, "svg", "app", platform)
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            for name, build in files:
                write(os.path.join(folder, f"{name}-{mode}.svg"), build(colours))
    for name, build in WEB_APP:
        write(os.path.join(ROOT, "svg", "app", "web", f"{name}.svg"), build())
    # Android 13's themed icons: the icon alone in one colour, which the launcher tints, so it comes once
    write(os.path.join(ROOT, "svg", "app", "android", "android-monochrome-432x432.svg"), transparent(432, LIGHT, ADAPTIVE))
