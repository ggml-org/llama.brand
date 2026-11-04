# Llama fonts

The Llama type family. **Llama Sans** is here now; Llama Mono and Llama Serif will follow. Every path below is relative to this `fonts/` folder.

Llama Sans is a neo-grotesk with an even stroke, round bowls and open, angle-cut terminals. It comes in three versions with identical outlines, each a variable font from 400 to 700:

| | Tracking | Kerning | Line spacing | For |
|---|---|---|---|---|
| **Llama Sans Display** | −26 | 115%, pair corrections at 100% | 1.15 em | Headlines, large sizes |
| **Llama Sans UI** | −4 | 105%, pair corrections at 75% | 1.25 em | Buttons, cards, labels, small interface text |
| **Llama Sans Text** | +10 | 85%, pair corrections at 50% | 1.5 em | Long prose, small sizes |

Line spacing is built into the fonts, so `line-height: normal` gives each version its intended leading. In every version the line box is centred on the cap height, so capitals and cap-height icons sit exactly in the middle of a button or chip with equal top and bottom padding. UI's 1.25 em gives whole-pixel lines at 12, 16 and 20 px (15, 20 and 25 px).

Every version also carries the Llama icon at U+E000, sitting on the baseline and reaching exactly the cap height, so it lines up with capitals in running text.

## Files

```
variable/   LlamaSansText[wght].ttf, LlamaSansUI[wght].ttf, LlamaSansDisplay[wght].ttf   (wght 400–700)
static/     Regular, Medium and Bold of each, cut from the variable fonts
scripts/    the font build (build_llama_sans.py, llama_edits.py), the specimen export, requirements.txt
specimen/   the specimen site (SvelteKit 3, Svelte 5), built to a single self-contained index.html
sources/    not in the repo: the build downloads the Geist outlines it starts from into here
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
.venv/bin/python scripts/build_specimen.py
```

```bash
cd specimen && npm install && npm run build
```

`build_llama_sans.py` starts from Geist's variable font, which isn't stored in the repo: the first build downloads the pinned version into `sources/geist/` and checks its SHA-256. It takes three masters from it (400, 500, and 650 for our 700), applies the edits in `llama_edits.py` to all of them identically so they stay compatible, and writes all three variable fonts plus their statics. The design settings are constants at the top of both scripts: terminal trim and angle (`OPEN`, `TK`), curve rounding (`ROUND`, `ROUND_BY_GLYPH`), widths (`WIDEN`), the a's bowl and Bold foot (`A_BOWL_DROP`, `A_FOOT`), the t's proportions (`T_SHAPE`, `T_TOP_DROP`, `T_FOOT_SLIDE`), an optional cap-height raise (`CAP_RAISE`), and the Text, UI and Display settings (`FAMILIES`).

`build_specimen.py` exports what the specimen needs from the fonts: glyph outlines and metrics as `specimen/src/lib/data/specimen.json`, plus copies of the variable fonts and their `@font-face` rules in `specimen/src/lib/fonts/`. Pass `--prev-fonts=DIR` (a folder laid out like this one) to add a Before/After switch comparing against an earlier build.

`npm run build` in `specimen/` then writes `specimen/build/index.html`: one file with the scripts, styles and fonts inlined, which you can open directly in a browser or publish anywhere. For live editing, `npm run dev` serves it with hot reload.

The scripts work from any folder; they find `fonts/` themselves.

## Licence

Llama Sans is derived from [Geist](https://github.com/vercel/geist-font), © 2024 The Geist Project Authors, and is released under the SIL Open Font License 1.1, like Geist. See [OFL.txt](OFL.txt).

The Llama icon glyph at U+E000 is the ggml-org mark, not part of the OFL grant: it is licensed under CC BY-NC 4.0 with the permissions in [`BRAND-USAGE.md`](../BRAND-USAGE.md), which cover embedding the mark into fonts to refer to Llama.app and Llama.cpp.
