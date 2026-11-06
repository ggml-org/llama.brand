"""Builds the social profile assets in logo/svg/social/: avatars and banners for X, LinkedIn and YouTube.

Avatars are the icon, optically centred (lifted a little) and small enough to survive the platforms' circle crop; banners are the Llama or
llama.cpp lockup (from build_lockups.py) centred inside each platform's safe area, where nothing gets cropped or sits
under the avatar. Everything comes light and dark, at each platform's recommended size; render_webp.sh renders these
at 1×, so the WebP and PNG files have exactly those sizes.

Run:  uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_social.py
"""
import os
from build_lockups import DARK, LIGHT, LOCKUP_H, OPTICAL_LIFT, ROOT, icon_paths, lockup, svg, write

AVATAR_ICON = 0.56  # the icon's share of the avatar's side, inside the circle crop
BANNER_LOCKUP = 0.3  # the lockup's height as a share of the safe area's height, at most
BANNER_WIDTH = 0.6  # and its width as a share of the safe area's width, at most

# platform: avatar side, and the banners as (name, width, height, safe width, safe height)
PLATFORMS = {
    "x": (400, [("header", 1500, 500, 1500, 360)]),
    "linkedin": (400, [("cover", 1584, 396, 1584, 396), ("page-cover", 1128, 191, 1128, 191)]),
    "youtube": (800, [("banner", 2560, 1440, 1546, 423)]),
}


def avatar(size, colours):
    side = size * AVATAR_ICON
    s, x = side / 600, (size - side) / 2
    y = x - side * OPTICAL_LIFT
    icon = "".join(f'<path d="{d}" fill="{colours["icon"]}"/>' for d in icon_paths())
    return svg(size, size, f'<rect width="{size}" height="{size}" fill="{colours["field"]}"/>\n'
                           f'<g transform="translate({x:.3f} {y:.3f}) scale({s:.6f})">{icon}</g>')


def banner(name, w, h, safe_w, safe_h, colours):
    body, width = lockup(name, colours)
    s = min(safe_h * BANNER_LOCKUP / LOCKUP_H, safe_w * BANNER_WIDTH / width)
    x, y = (w - width * s) / 2, (h - LOCKUP_H * s) / 2
    return svg(w, h, f'<rect width="{w}" height="{h}" fill="{colours["field"]}"/>\n'
                     f'<g transform="translate({x:.3f} {y:.3f}) scale({s:.6f})">{body}</g>')


if __name__ == "__main__":
    for platform, (size, banners) in PLATFORMS.items():
        folder = os.path.join(ROOT, "svg", "social", platform)
        for mode, colours in (("light", LIGHT), ("dark", DARK)):
            write(os.path.join(folder, f"{platform}-avatar-{mode}.svg"), avatar(size, colours))
            for kind, w, h, safe_w, safe_h in banners:
                for name in ("llama", "llama-cpp"):
                    write(os.path.join(folder, f"{platform}-{kind}-{name}-{mode}.svg"),
                          banner(name, w, h, safe_w, safe_h, colours))
