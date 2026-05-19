#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist/appimage"
BUILD_DIR="$PROJECT_ROOT/dist/appimage-build"
APPDIR="$PROJECT_ROOT/dist/AppDir"
APPIMAGETOOL="$SCRIPT_DIR/appimagetool-x86_64.AppImage"
VENDOR_DIR="$APPDIR/usr/share/zt-manager/vendor"

[ -f "$PROJECT_ROOT/.venv/bin/activate" ] && source "$PROJECT_ROOT/.venv/bin/activate"
export PATH="/usr/bin:$PATH"

VERSION=$(python3 -c "import re; print(re.search(r\"version: '([^']+)'\", open('$PROJECT_ROOT/meson.build').read()).group(1))")
echo "Building AppImage for zt-manager $VERSION"

mkdir -p "$DIST_DIR" "$APPDIR"
rm -rf "$APPDIR"/*

echo "Configuring with meson..."
meson setup "$BUILD_DIR" "$PROJECT_ROOT" --prefix=/usr \
  --wipe 2>/dev/null || meson setup "$BUILD_DIR" "$PROJECT_ROOT" --prefix=/usr

echo "Compiling..."
ninja -C "$BUILD_DIR"

echo "Installing into AppDir..."
DESTDIR="$APPDIR" ninja -C "$BUILD_DIR" install

echo "Bundling Python deps..."
mkdir -p "$VENDOR_DIR"
/usr/bin/python3 -m pip install \
  --target="$VENDOR_DIR" \
  --no-deps \
  pydbus requests
/usr/bin/python3 -m pip install \
  --target="$VENDOR_DIR" \
  --only-binary=:all: \
  psutil
find "$VENDOR_DIR" -maxdepth 1 -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true

echo "Creating AppRun..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
export APPDIR
export PYTHONPATH="${APPDIR}/usr/share/zt-manager/vendor:${PYTHONPATH}"
exec /usr/bin/python3 "${APPDIR}/usr/bin/ztmanager" "$@"
EOF
chmod +x "$APPDIR/AppRun"

echo "Copying desktop and icon into AppDir root..."
cp "$APPDIR/usr/share/applications/io.github.riemarukarurosu.ZTManager.desktop" "$APPDIR/"

SVG=$(find "$APPDIR/usr/share/icons" -name "io.github.riemarukarurosu.ZTManager.svg" | head -1)
[ -n "$SVG" ] && cp "$SVG" "$APPDIR/io.github.riemarukarurosu.ZTManager.svg"

PNG=$(find "$APPDIR/usr/share/icons" -name "*.png" | grep apps | head -1)
[ -n "$PNG" ] && cp "$PNG" "$APPDIR/io.github.riemarukarurosu.ZTManager.png"

echo "Downloading appimagetool..."
if [ ! -f "$APPIMAGETOOL" ]; then
    curl -fsSL -o "$APPIMAGETOOL" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

OUTPUT="$DIST_DIR/ZTManager-$VERSION-appimage-x86_64.AppImage"
echo "Building AppImage..."
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 \
  "$APPIMAGETOOL" "$APPDIR" "$OUTPUT"

echo ""
echo "Done! AppImage at $OUTPUT"
ls -lh "$OUTPUT"
