#!/bin/sh
# Renders every SVG in logo/svg/ to a lossless WebP in logo/webp/, keeping the folder layout.
# Icons and lockups render at 2x their SVG size; the covers, already 7500 wide, at 1x.
# Needs ImageMagick (magick) and libwebp (cwebp): brew install imagemagick webp
set -eu
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

find svg -name '*.svg' | sort | while read -r src; do
	out="webp/${src#svg/}"
	out="${out%.svg}.webp"
	mkdir -p "$(dirname "$out")"
	width=$(magick identify -format '%w' "$src")
	density=$([ "$width" -le 3000 ] && echo 192 || echo 96) # 96 dpi is 1 SVG unit per pixel
	magick -background none -density "$density" "$src" "$tmp/frame.png"
	cwebp -quiet -lossless -z 9 -exact "$tmp/frame.png" -o "$out"
	echo "$out $(magick identify -format '%wx%h' "$out")"
done
