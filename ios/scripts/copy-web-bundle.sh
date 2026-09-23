#!/bin/sh
# Copy dist/ into the app bundle, preserving paths. Xcode's Copy Bundle
# Resources phase flattens groups, which would break the game's relative URLs.
set -eu

if [ -z "${SRCROOT:-}" ] || [ -z "${TARGET_BUILD_DIR:-}" ] || [ -z "${UNLOCALIZED_RESOURCES_FOLDER_PATH:-}" ]; then
  echo "copy-web-bundle.sh must be run from an Xcode build" >&2
  exit 1
fi

SRC="${SRCROOT}/../dist"
DEST="${TARGET_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/dist"

copy_file() {
  rel="$1"
  src="${SRC}/${rel}"
  dest="${DEST}/${rel}"
  if [ ! -f "${src}" ]; then
    echo "Missing web bundle file: ${src}" >&2
    exit 1
  fi
  mkdir -p "$(dirname "${dest}")"
  cp "${src}" "${dest}"
}

copy_file "arcade.css"
copy_file "assets/ink-crew.webp"
copy_file "assets/ink-scenes.webp"
copy_file "engine.mjs"
copy_file "index.html"
copy_file "pieces.mjs"
copy_file "rpg-model.mjs"
copy_file "rpg.css"
copy_file "rpg.mjs"
