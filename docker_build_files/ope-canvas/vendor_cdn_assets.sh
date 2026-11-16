#!/bin/bash
# OPE: serve the files canvas' compiled JS would load from public CDNs out of the image instead
# (OPE servers are usually offline). Runs at build time, after canvas:compile_assets:
#   1. puts each file under public/ope-vendor/...
#   2. rewrites the CDN url in the compiled chunks (public/dist/webpack-production/*.js) to the local path
#   3. fails the build if a known CDN url is still in the chunks - i.e. a newer canvas release changed a
#      version/url and this script needs updating (see the version variables below)
#
# Left alone on purpose (cloud services that don't work offline anyway, or never loaded): Google Cast sender,
# Immersive Reader icon/polyfill, Ada chat, Pendo, Gravatar, twemoji (parser only - images never loaded).
set -euo pipefail

APP=/usr/src/app
DIST=$APP/public/dist/webpack-production
VENDOR=$APP/public/ope-vendor
TMP=$(mktemp -d)

# Versions the bundled packages ask for (see the CDN urls they contain)
DASHJS_VERSION=4.7.4              # @instructure/studio-player (vidstack) - DASH video streams
HLS_JS_VERSION=1.7.4              # @instructure/studio-player (vidstack) asks for hls.js@^1.5.0 - newest 1.x
MEDIAPIPE_VISION_VERSION=0.10.14  # @instructure/media-capture - webcam background blur
EMOJI_DATASOURCE_VERSION=5.0.1    # emoji-mart 3.x emoji picker sprite sheets
EMOJI_SET=apple                   # emoji-mart defaults (canvas doesn't override set / sheetSize)
EMOJI_SHEET_SIZE=64

mkdir -p "$VENDOR"
cd "$TMP"

npm_extract() {  # package@version dest - unpack an npm package tarball into dest
    local tgz
    tgz=$(npm pack --silent "$1")
    mkdir -p "$2"
    tar xzf "$tgz" -C "$2" --strip-components=1
    rm -f "$tgz"
}

# --- dash.js (already in node_modules at the version vidstack asks for - fall back to npm)
D=$VENDOR/dashjs@$DASHJS_VERSION
mkdir -p "$D"
if grep -q "\"version\": \"$DASHJS_VERSION\"" "$APP/node_modules/dashjs/package.json" 2>/dev/null; then
    cp "$APP/node_modules/dashjs/dist/dash.all.min.js" "$D/"
else
    npm_extract "dashjs@$DASHJS_VERSION" "$TMP/dashjs" && cp "$TMP/dashjs/dist/dash.all.min.js" "$D/"
fi

# --- hls.js
D=$VENDOR/hls.js@$HLS_JS_VERSION
npm_extract "hls.js@$HLS_JS_VERSION" "$TMP/hlsjs"
mkdir -p "$D" && cp "$TMP/hlsjs/dist/hls.min.js" "$D/"

# --- MediaPipe vision wasm runtime + the selfie segmentation model used for background blur
D=$VENDOR/mediapipe/tasks-vision@$MEDIAPIPE_VISION_VERSION
npm_extract "@mediapipe/tasks-vision@$MEDIAPIPE_VISION_VERSION" "$TMP/mediapipe"
mkdir -p "$D" && cp -r "$TMP/mediapipe/wasm" "$D/"
mkdir -p "$VENDOR/mediapipe/models"
curl -fsSL -o "$VENDOR/mediapipe/models/selfie_segmenter.tflite" \
    https://files.instructuremedia.com/mediapipe-models/selfie_segmenter.tflite \
  || curl -fsSL -o "$VENDOR/mediapipe/models/selfie_segmenter.tflite" \
    https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite

# --- emoji-mart sprite sheet (same path layout as unpkg, so emoji-mart's url builder just gets a new prefix)
D=$VENDOR/emoji-datasource-$EMOJI_SET@$EMOJI_DATASOURCE_VERSION/img/$EMOJI_SET/sheets-256
mkdir -p "$D"
curl -fsSL -o "$D/$EMOJI_SHEET_SIZE.png" \
    "https://unpkg.com/emoji-datasource-$EMOJI_SET@$EMOJI_DATASOURCE_VERSION/img/$EMOJI_SET/sheets-256/$EMOJI_SHEET_SIZE.png"

# --- rewrite the urls in the compiled chunks
cd "$DIST"
rewrite() {  # from to
    local files
    files=$(grep -lF -- "$1" ./*.js || true)
    if [ -z "$files" ]; then echo "  (not found - skipped) $1"; return; fi
    # literal (not regex) replace - the urls contain ^ @ . characters
    for f in $files; do FROM="$1" TO="$2" perl -pi -e 's/\Q$ENV{FROM}\E/$ENV{TO}/g' "$f"; done
    echo "  $1 -> $2 ($(echo "$files" | wc -w) file(s))"
}
echo "Rewriting CDN urls in $DIST:"
rewrite "https://cdn.jsdelivr.net/npm/dashjs@$DASHJS_VERSION/dist/dash.all.min.js" "/ope-vendor/dashjs@$DASHJS_VERSION/dash.all.min.js"
rewrite "https://cdn.jsdelivr.net/npm/hls.js@^1.5.0/dist/hls.min.js"              "/ope-vendor/hls.js@$HLS_JS_VERSION/hls.min.js"
rewrite "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@$MEDIAPIPE_VISION_VERSION/wasm" "/ope-vendor/mediapipe/tasks-vision@$MEDIAPIPE_VISION_VERSION/wasm"
rewrite "https://files.instructuremedia.com/mediapipe-models/selfie_segmenter.tflite" "/ope-vendor/mediapipe/models/selfie_segmenter.tflite"
rewrite "https://unpkg.com/emoji-datasource-"                                     "/ope-vendor/emoji-datasource-"

# --- anything left means a new canvas release changed a url/version - update the variables above
left=$(grep -oE "https://(cdn\.jsdelivr\.net/npm/|unpkg\.com/|files\.instructuremedia\.com/mediapipe-models/)[^\"' )\`]*" ./*.js | sort -u || true)
if [ -n "$left" ]; then
    echo "ERROR - compiled JS still loads from a CDN (update vendor_cdn_assets.sh):"
    echo "$left"
    exit 1
fi

rm -rf "$TMP"
npm cache clean --force >/dev/null 2>&1 || true   # npm pack cached the tarballs - keep them out of the layer
du -sh "$VENDOR"
find "$VENDOR" -type f | sed "s#^$APP/public##" | sort
