# Llama logo

The Llama icon, the Llama and Llama.cpp lockups and the cover images, plus a showcase that takes the icon apart.

```
svg/        the source artwork
  icon/       the icon, light and dark, 600 × 600
  lockup/     the icon with the Llama and Llama.cpp wordmarks
  cover/      7500 × 2500 covers, light, dark and alt
webp/       every SVG rendered to a lossless WebP, same layout: icons and lockups at 2×, covers at 1×
scripts/    render_webp.sh, which rebuilds webp/ from svg/
showcase/   the icon breakdown page (SvelteKit 3, Svelte 5), built to a single self-contained index.html
```

## Rendering the WebP files

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
