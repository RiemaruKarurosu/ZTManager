#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist/rpm"

[ -f "$PROJECT_ROOT/.venv/bin/activate" ] && source "$PROJECT_ROOT/.venv/bin/activate"
export PATH="/usr/bin:$PATH"

VERSION=$(python3 -c "import re; print(re.search(r\"version: '([^']+)'\", open('$PROJECT_ROOT/meson.build').read()).group(1))")
echo "Building RPM for zt-manager $VERSION"

mkdir -p "$HOME/rpmbuild"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
mkdir -p "$DIST_DIR"

echo "Creating source tarball..."
cd "$PROJECT_ROOT"
tar --exclude='.git' \
    --exclude='.venv' \
    --exclude='dist' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    -czf "$HOME/rpmbuild/SOURCES/v$VERSION.tar.gz" \
    --transform "s|^\.|ZT-Manager-$VERSION|" \
    .

cp "$SCRIPT_DIR/ztmanager.spec" "$HOME/rpmbuild/SPECS/ztmanager.spec"

echo "Running rpmbuild..."
rpmbuild -ba "$HOME/rpmbuild/SPECS/ztmanager.spec" \
  --define "app_version $VERSION" \
  --define "_topdir $HOME/rpmbuild" \
  --nodeps

echo "Copying RPM to dist/rpm/..."
find "$HOME/rpmbuild/RPMS" -name "*.rpm" | while read -r f; do
    base=$(basename "$f")
    newbase=$(echo "$base" | sed "s/-${VERSION}-/-${VERSION}-rpm-/")
    cp -v "$f" "$DIST_DIR/$newbase"
done
echo ""
echo "Done! RPM packages in $DIST_DIR/"
ls -lh "$DIST_DIR/"
