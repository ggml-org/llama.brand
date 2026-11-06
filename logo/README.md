# Llama logo

The Llama icon, the Llama and llama.cpp lockups and the cover images, plus a showcase that takes the icon apart.

```
svg/        the source artwork
  icon/       the icon, light and dark, 600 × 600: transparent, and on its background (-bg)
  lockup/     the icon with the Llama and llama.cpp wordmarks: transparent, and on its background (-bg)
  cover/      7500 × 2500 covers, light and dark
  social/     avatars and banners for X, LinkedIn and YouTube, light and dark, at each platform's size
webp/       every SVG rendered to a lossless WebP, same layout: icons and lockups at 2×, covers at 1×
png/        the same renders as PNG, for tools that don't take WebP
scripts/    build_lockups.py, which draws the lockups and covers from the icon, Llama Sans (Display size) and Llama Mono;
            build_social.py, which lays the icon and lockups out as social avatars and banners;
            render_webp.sh, which rebuilds webp/ and png/ from svg/
showcase/   the icon breakdown page (SvelteKit 3, Svelte 5), built to a single self-contained index.html
```

## Building the lockups and covers

```bash
uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_lockups.py
```

The lockups and covers are generated, not drawn: the icon from `svg/icon/icon-light.svg`, the wordmark: "Llama" in Llama Sans Bold at its Display optical size (`fonts/variable/LlamaSans[opsz,wght].ttf` at wght 700, opsz 40), "llama.cpp" (always lowercase) in Llama Mono Bold (`fonts/variable/LlamaMono[wght].ttf` at wght 700), kerned with HarfBuzz and outlined, in the brand's ink and light, with .cpp in cinder, the brand's accent orange (#EE6C1E, the design system's art-cinder). The proportion comes from the fonts' lockup icon (U+E002, in both): the icon 1.24 times the cap height, centred on the capitals, and the first letter as far after it as the glyph's built-in gap puts it, so a lockup typed as U+E002 and the name matches the logo files. It also writes each icon and lockup on its background (`-bg`): the same canvas, filled with the light or dark field, the mark centred in an even 12% margin of the shorter side, and the icon optically centred, lifted 1/40 of its height and nudged 1/100 of its width left, as in the social avatars and app icons. The plain files stay transparent. Run it after any change to the icon or the fonts, then render the WebP and PNG files.

Grounds: the llama.cpp lockup always sits on a neutral ground (the light #FAFAFA, the dark #111111 or the greys), which is why every llama.cpp file here is neutral. Only the Llama lockup goes on colour: the hero's light blue or its navy, from llama.app.

## Social profile assets

```bash
uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_social.py
```

| Platform | Avatar | Banner |
|----------|--------|--------|
| X | 400 × 400 | header 1500 × 500 |
| LinkedIn | 400 × 400 | cover 1584 × 396, page cover 1128 × 191 |
| YouTube | 800 × 800 | banner 2560 × 1440, logo inside the 1546 × 423 safe area |

Avatars are the icon at 56% of the side, so the circle crop never touches it, optically centred: lifted 1/40 of its height and nudged 1/100 of its width left, since its heavy bottom bar makes it read low when centred exactly; so placed, the circle clears each pair of its outer points (the rounded corners, the sharp corners and the tips at its middle) within 2% of the side of each other; banners are the Llama or llama.cpp lockup centred in the platform's safe area. They render at 1×, so the WebP and PNG files have exactly these sizes.

## App icons

```bash
uvx --with fonttools==4.68.0 --with uharfbuzz --with skia-pathops python logo/scripts/build_app_icons.py
```

| Platform | Files (light and dark) |
|----------|------------------------|
| PWA | round icon 512 × 512 (`any`), maskable 512 × 512 |
| Apple | touch icon 180 × 180, iOS 1024 × 1024, macOS 1024 × 1024 |
| Android | adaptive icon foreground and background 432 × 432 (108 dp at 4×), Play Store 512 × 512, and one monochrome 432 × 432 for themed icons |
| Windows | app icon 256 × 256, tiles 150 × 150 and 310 × 150 |
| Web app | the web UI's own five, in its colours (#111111 on white): favicon and dark favicon (transparent, the icon at 96%), round PWA icon, maskable icon 512 × 512, Apple touch icon 180 × 180 |

Full-bleed squares (maskable, touch, iOS, Play Store), which each platform masks to its own shape, carry the icon at 67.2% of the side, as the web UI's maskable and Apple touch icons do, inside the 80% safe circle; the round PWA icon is that at 85%, cut round. The macOS icon sits on Apple's 824 × 824 rounded square (radius 185.4) on the 1024 canvas; the Android foreground keeps the icon inside the 66 dp circle every launcher shows; the Windows app icon is transparent with a 1/16 margin, and the tiles carry it at half their height. Every icon is lifted 1/40 of its height and nudged 1/100 of its width left, as on its background and in the avatars. They render at 1×.

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
