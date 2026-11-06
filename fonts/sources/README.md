# Sources

The two fonts Llama Sans and Llama Mono are built from, committed so the build needs no network and keeps working
if the upstream repository moves or goes away:

- `geist/Geist[wght].ttf`: Geist's variable font
- `geist-mono/GeistMono[wght].ttf`: Geist Mono's variable font

Both are unchanged copies from [vercel/geist-font](https://github.com/vercel/geist-font) at commit
`a0a06a3d916dcf92fe96f12051a124f89056b36a` (2026-04-02), from `fonts/Geist/variable/` and `fonts/GeistMono/variable/`.
They're © 2024 The Geist Project Authors, under the SIL Open Font License 1.1 (`../OFL.txt`).

The builds check each file's SHA-256 (`GEIST_SHA256` in `scripts/build_llama_sans.py`, `GEIST_MONO_SHA256` in
`scripts/build_llama_mono.py`) and stop if it doesn't match, so a changed source never slips into a build.

## Updating Geist

1. Download both files from the new commit (or release) of vercel/geist-font into these folders, under the same names.
2. Set `GEIST_COMMIT` and the two SHA-256s in the build scripts (`shasum -a 256 sources/*/*.ttf`), and the commit
   above.
3. Rebuild both fonts and the specimen, and compare the results with the previous ones before committing: a new
   Geist can move outlines the edits in `llama_edits.py` depend on.
