# Llama fonts

The Llama type family. **Llama Sans** and **Llama Mono** are here now; Llama Serif will follow. Every path below is relative to this `fonts/` folder.

Llama Sans is a neo-grotesk with an even stroke, round bowls and open, angle-cut terminals. It comes in two versions with the same outlines, apart from UI's deeper descenders (155 units, against Display's 140), each a variable font from 400 to 700 (Regular, Medium, SemiBold and Bold at 400, 500, 600 and 700):

| | Tracking | Kerning | Line spacing | For |
|---|---|---|---|---|
| **Llama Sans Display** | −26 | 115%, pair corrections at 100% | 1.15 em | Headlines, large sizes |
| **Llama Sans UI** | 0 | 105%, pair corrections at 75%, then matched to SF Pro's text sizes | 1.25 em | Buttons, cards, labels, interface and running text |

Line spacing is built into the fonts, so `line-height: normal` gives each version its intended leading; for prose in UI, set `line-height: 1.5`. In every version the line box is centred on the cap height, so capitals and cap-height icons sit exactly in the middle of a button or chip with equal top and bottom padding. UI's 1.25 em gives whole-pixel lines at 12, 16 and 20 px (15, 20 and 25 px).

Every version also carries the Llama icon at U+E000, sitting on the baseline and reaching exactly the cap height, so it lines up with capitals in running text.

## Llama Mono

Llama Mono is the monospaced member, built from Geist Mono with Llama Sans's changes: the same weights (400–700, the design's 400–640), the tailless a, the narrow t, angle-cut terminals, rounder curves, deeper stem joins and UI's descenders (155) and line box. Every glyph keeps Geist Mono's 600-unit cell: where a change makes a drawing narrower or wider (a, t, s), it is moved back to where Geist Mono centred it rather than changing the advance. Some Sans changes don't carry over:

- No tracking or kerning: every character takes one cell.
- The l keeps its serifs, so l, 1, I and | stay apart in code; G and S keep Geist Mono's width, which already fills the cell.
- tt joins its crossbars with contextual alternates (`calt`) instead of kerning: a t before a t runs its bar to the cell's right edge, a t after one to its left edge.
- The Llama icon at U+E000 fits the cell (480 units) and centres on half the cap height.

Geist Mono's coding ligatures (`->`, `=>`, `!==` …) stay as they are, under `liga`.

## Files

```
variable/   LlamaSansUI[wght].ttf, LlamaSansDisplay[wght].ttf, LlamaMono[wght].ttf   (wght 400–700)
static/     Regular, Medium, SemiBold and Bold of each, cut from the variable fonts
scripts/    the font builds (build_llama_sans.py, build_llama_mono.py, llama_edits.py), the specimen export, requirements.txt
specimen/   the specimen site (SvelteKit 3, Svelte 5), built to a single self-contained index.html
sources/    not in the repo: the builds download the Geist and Geist Mono outlines they start from into here
```

## Building

Requires Python 3.9+ for the fonts, and Node 22+ for the specimen.

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
```

```bash
.venv/bin/python scripts/build_llama_sans.py
```

```bash
.venv/bin/python scripts/build_llama_mono.py
```

```bash
.venv/bin/python scripts/build_specimen.py
```

```bash
cd specimen && npm install && npm run build
```

`build_llama_sans.py` starts from Geist's variable font, which isn't stored in the repo: the first build downloads the pinned version into `sources/geist/` and checks its SHA-256. It takes three masters from it (400, 500, and 650 for the design's 700), applies the edits in `llama_edits.py` to all of them identically so they stay compatible, and writes both variable fonts plus their statics. The wght axis shows the design from 400 to `TOP_WEIGHT` (640) stretched over 400–700, so Medium (500), SemiBold (600) and Bold (700) are the design's 480, 560 and 640. The design settings are constants at the top of both scripts: terminal trim and angle (`OPEN`, `TK`), curve rounding (`ROUND`, `ROUND_BY_GLYPH`), widths (`WIDEN`), descender depth (`DESCENDER`, and UI's own `descender` in `FAMILIES`), the a's bowl and Bold foot (`A_BOWL_DROP`, `A_FOOT`), the t's arms and cuts (`T_SHAPE`, `T_TOP_DROP`, `T_FOOT_SLIDE`), how deep the notches cut where bowls and arms leave a stem (`JOIN_CUT`, or `--join-cut=N` to try another depth), an optional cap-height raise (`CAP_RAISE`), the UI and Display settings (`FAMILIES`) and the kerning matched to SF Pro (`UI_KERN`, `DISPLAY_KERN`).

`build_llama_mono.py` does the same from Geist Mono (pinned to the same Geist commit, downloaded into `sources/geist-mono/`), reusing the Sans build's functions; it fails if any glyph but the zero-width marks leaves the 600-unit cell.

`build_specimen.py` exports what the specimen needs from the fonts: glyph outlines and metrics as `specimen/src/lib/data/specimen.json`, plus copies of the variable fonts and their `@font-face` rules in `specimen/src/lib/fonts/`. Pass `--prev-fonts=DIR` (a folder laid out like this one) to add a Before/After switch comparing against an earlier build.

`npm run build` in `specimen/` then writes `specimen/build/index.html`: one file with the scripts, styles and fonts inlined, which you can open directly in a browser or publish anywhere. For live editing, `npm run dev` serves it with hot reload.

The scripts work from any folder; they find `fonts/` themselves.

## Licence

Llama Sans and Llama Mono are derived from [Geist and Geist Mono](https://github.com/vercel/geist-font), © 2024 The Geist Project Authors, and are released under the SIL Open Font License 1.1, like Geist. See [OFL.txt](OFL.txt).

The Llama icon glyph at U+E000 is the ggml-org mark, not part of the OFL grant: it is licensed under CC BY-NC 4.0 with the permissions in [`BRAND-USAGE.md`](../BRAND-USAGE.md), which cover embedding the mark into fonts to refer to Llama.app and Llama.cpp.
