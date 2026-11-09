# llama-brand

Official brand assets for **Llama.app** and **llama.cpp**: the logo, the Llama type family, and the colours and core CSS that everything the brand makes is built on.

```
logo/    the icon, the lockups and the covers as SVG and WebP, plus the logo showcase
fonts/   Llama Sans (one font over weight and optical size) and Llama Mono, their build scripts and the specimen
css/     the brand's colours, its font faces, and communications' grounds and type scale
```

---

## Logos

### Llama

| Light | Dark |
|-------|------|
| ![Llama Light](./logo/svg/lockup/llama/logo-llama-light.svg) | ![Llama Dark](./logo/svg/lockup/llama/logo-llama-dark.svg) |

### llama.cpp

| Light | Dark |
|-------|------|
| ![llama.cpp Light](./logo/svg/lockup/llama-cpp/logo-llama-cpp-light.svg) | ![llama.cpp Dark](./logo/svg/lockup/llama-cpp/logo-llama-cpp-dark.svg) |

---

## Icons

| Light | Dark |
|-------|------|
| ![Icon Light](./logo/svg/icon/icon-light.svg) | ![Icon Dark](./logo/svg/icon/icon-dark.svg) |

---

## Cover Images

### Llama

| Light | Dark |
|-------|------|
| ![Llama Cover Light](./logo/svg/cover/llama/cover-llama-light.svg) | ![Llama Cover Dark](./logo/svg/cover/llama/cover-llama-dark.svg) |

### llama.cpp

| Light | Dark |
|-------|------|
| ![llama.cpp Cover Light](./logo/svg/cover/llama-cpp/cover-llama-cpp-light.svg) | ![llama.cpp Cover Dark](./logo/svg/cover/llama-cpp/cover-llama-cpp-dark.svg) |

Every SVG also comes as a lossless WebP under [`logo/webp/`](./logo/webp) and a PNG under [`logo/png/`](./logo/png), in the same layout. See [`logo/`](./logo) for the showcase that takes the icon apart.

---

## Fonts

**Llama Sans** is the sans of the Llama type family, with Mono and Serif to follow: one variable font from 400 to 700 with an optical size axis from 16 to 40, spaced for interfaces (UI) at its small end and for headlines (Display) at its large end, which browsers pick from the font-size. See [`fonts/`](./fonts).

---

## Colours

Grounds stay neutral as a rule: the logo's ink and light, paper and sand. Cinder is the one accent: the `.cpp` of the llama.cpp logotype, and a mark on a detail. The colours are for shapes, figures and accents, never for status.

| Name | Token | Value |
|---|---|---|
| Ink | `--brand-ink` | `#111111` |
| Light | `--brand-light` | `#fafafa` |
| Sand 50 | `--sand-50` | `#f7f3ec` |
| Sand 100 | `--sand-100` | `#efe9df` |
| Sand ink | `--sand-900` | `#2b2620` |
| Cinder | `--art-cinder` | `#ee6c1e` |
| Cinder light | `--art-cinder-light` | `#f3c1ab` |
| Day sky | `--art-day-sky` | `#8fbde5` |
| Night sky | `--art-night-sky` | `#1b3659` |

The day sky and the night sky also come as gradient grounds (`--gradient-day-sky`, `--gradient-night-sky`), from llama.app's light and dark hero. The greys are Tailwind's neutral scale plus four in-between steps (`--neutral-0` to `--neutral-950`). [`css/colors.css`](./css/colors.css) has every value, in OKLCH.

---

## CSS

```
css/brand.css            everything below, in one import
css/colors.css           the colours above, as custom properties on :root
css/fonts.css            @font-face for Llama Sans and Llama Mono, and --font-sans and --font-mono
css/communications.css   the grounds and the type scale for posts, posters, boards and other visual assets
```

```css
@import 'llama-brand/css/brand.css';
```

Communications measure everything in `--u`, a 24th of the format's short side (45px on a 1080 × 1080 post), which the layout sets. A piece takes `.ground` and one of `.ground-light`, `.ground-dark`, `.ground-sand`, `.ground-day` or `.ground-night`, which set its background and inks (`--p-ink`, `--p-muted`, `--p-line` and the rest). Its text takes the type scale: `.t-label`, `.t-body`, `.t-lede`, `.t-headline`, `.t-display`, `.t-figure` and `.t-mono`.

The llama.cpp web UI's design system builds on the same colours, with the same names, and adds what only an interface needs: status colours, translucent whites and blacks, and its type, length and radius scales.

---

## License

The logo assets are licensed under CC BY-NC 4.0, see [`LICENSE`](./LICENSE).

Distributions, packagers, and anyone referring to the project should read [`BRAND-USAGE.md`](./BRAND-USAGE.md), which grants the permissions that use needs.

The CSS is under the same licence as the logo assets. The fonts are released under the SIL Open Font License 1.1, see [`fonts/OFL.txt`](./fonts/OFL.txt). The Llama icon they carry at U+E000, U+E001 and U+E002 stays under the logo licence above.
