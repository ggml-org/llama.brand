#!/bin/sh
# Renders every SVG in logo/svg/ to a lossless WebP in logo/webp/ and a PNG in logo/png/, keeping the folder layout.
# Icons and lockups render at 2x their SVG size; the covers, already 7500 wide, and the social and app icons, drawn at the
# platforms' exact sizes, at 1x.
# Needs ImageMagick (magick) and libwebp (cwebp): brew install imagemagick webp
set -eu
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

find svg -name '*.svg' | sort | while read -r src; do
	out="webp/${src#svg/}"
	out="${out%.svg}.webp"
	png="png/${src#svg/}"
	png="${png%.svg}.png"
	mkdir -p "$(dirname "$out")" "$(dirname "$png")"
	case "$src" in
		svg/social/* | svg/cover/* | svg/app/*) density=96 ;; # 96 dpi is 1 SVG unit per pixel
		*) density=192 ;;
	esac
	magick -background none -density "$density" "$src" "$tmp/frame.png"
	cwebp -quiet -lossless -z 9 -exact "$tmp/frame.png" -o "$out"
	magick "$tmp/frame.png" -strip -define png:compression-level=9 "$png"
	echo "$out $png $(magick identify -format '%wx%h' "$out")"
done
