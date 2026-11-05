# Llama logo

The Llama icon, the Llama and Llama.cpp lockups and the cover images, plus a showcase that takes the icon apart.

```
svg/        the source artwork
  icon/       the icon, light and dark, 600 × 600
  lockup/     the icon with the Llama and Llama.cpp wordmarks
  cover/      7500 × 2500 covers, light, dark and alt
webp/       every SVG rendered to a lossless WebP, same layout: icons and lockups at 2×, covers at 1×
png/        the same renders as PNG, for tools that don't take WebP
scripts/    build_lockups.py, which draws the lockups and covers from the icon and Llama Sans Display;
            render_webp.sh, which rebuilds webp/ and png/ from svg/
showcase/   the icon breakdown page (SvelteKit 3, Svelte 5), built to a single self-contained index.html
```

## Building the lockups and covers

```bash
uvx --with fonttools==4.68.0 --with uharfbuzz python logo/scripts/build_lockups.py
```

The lockups and covers are generated, not drawn: the icon from `svg/icon/icon-light.svg`, the wordmark, "Llama" or "Llama.cpp", set in Llama Sans Display Bold (`fonts/static/LlamaSansDisplay-Bold.ttf`), kerned with HarfBuzz and outlined, in the brand's ink, light and orange, its capitals centred on the icon. Run it after any change to the icon or the fonts, then render the WebP and PNG files.

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
