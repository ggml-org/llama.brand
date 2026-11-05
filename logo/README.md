# Llama logo

The Llama icon, the Llama and Llama.cpp lockups and the cover images, plus a showcase that takes the icon apart.

```
svg/        the source artwork
  icon/       the icon, light and dark, 600 × 600: transparent, and on its background (-bg)
  lockup/     the icon with the Llama and Llama.cpp wordmarks: transparent, and on its background (-bg)
  cover/      7500 × 2500 covers, light and dark
  social/     avatars and banners for X, LinkedIn and YouTube, light and dark, at each platform's size
webp/       every SVG rendered to a lossless WebP, same layout: icons and lockups at 2×, covers at 1×
png/        the same renders as PNG, for tools that don't take WebP
scripts/    build_lockups.py, which draws the lockups and covers from the icon and Llama Sans (Display size);
            build_social.py, which lays the icon and lockups out as social avatars and banners;
            render_webp.sh, which rebuilds webp/ and png/ from svg/
showcase/   the icon breakdown page (SvelteKit 3, Svelte 5), built to a single self-contained index.html
```

## Building the lockups and covers

```bash
uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_lockups.py
```

The lockups and covers are generated, not drawn: the icon from `svg/icon/icon-light.svg`, the wordmark, "Llama" or "llama.cpp" (always lowercase), set in Llama Sans Bold at its Display optical size (`fonts/variable/LlamaSans[opsz,wght].ttf` at wght 700, opsz 40), kerned with HarfBuzz and outlined, in the brand's ink and light, with .cpp in cinder, the brand's accent orange (#E9712E, the design system's art-cinder), its capitals centred on the icon. It also writes each icon and lockup on its background (`-bg`): the same canvas, filled with the light or dark field, the mark centred in an even 12% margin of the shorter side, and the icon lifted 1/60 of its height above centre, as in the Llama app icon and the social avatars. The plain files stay transparent. Run it after any change to the icon or the fonts, then render the WebP and PNG files.

## Social profile assets

```bash
uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_social.py
```

| Platform | Avatar | Banner |
|----------|--------|--------|
| X | 400 × 400 | header 1500 × 500 |
| LinkedIn | 400 × 400 | cover 1584 × 396, page cover 1128 × 191 |
| YouTube | 800 × 800 | banner 2560 × 1440, logo inside the 1546 × 423 safe area |

Avatars are the icon at 56% of the side, so the circle crop never touches it, optically centred: lifted 1/60 of its height above centre, as in the Llama app icon, since its heavy bottom bar makes it read low when centred exactly; banners are the Llama or llama.cpp lockup centred in the platform's safe area. They render at 1×, so the WebP and PNG files have exactly these sizes.

## Rendering the WebP and PNG files

```bash
logo/scripts/render_webp.sh
```

Needs ImageMagick and libwebp (`brew install imagemagick webp`). Run it after any change in `svg/`.

## The showcase

The showcase draws the icon's construction as a blueprint, then shows where the mark comes from (a plus and an L, given a bolt's slant), each rule that shapes it, and the icon set in Llama Sans. It follows the system's light and dark mode.

```bash
cd logo/showcase && npm install && npm run build
```

That writes `logo/showcase/build/index.html`, one file with the scripts, styles and fonts inlined. `npm run dev` serves it with hot reload. Both take Llama Sans from `fonts/variable/` (copied in by `scripts/fonts.js`).

The original pencil sketch is `showcase/src/lib/assets/sketch.webp`, opened from the "View the original sketch" button in the origin section.
