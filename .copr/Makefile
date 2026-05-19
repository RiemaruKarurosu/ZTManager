srpm:
	dnf install -q -y rpm-build curl
	@set -e; \
	  VERSION=$$(python3 -c "import re; print(re.search(r\"version: '([^']+)'\", open('meson.build').read()).group(1))"); \
	  mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}; \
	  curl -fsSL \
	    "https://github.com/RiemaruKarurosu/ZTManager/archive/refs/tags/v$${VERSION}.tar.gz" \
	    -o ~/rpmbuild/SOURCES/v$${VERSION}.tar.gz; \
	  cp packaging/ztmanager.spec ~/rpmbuild/SPECS/ztmanager.spec; \
	  rpmbuild -bs ~/rpmbuild/SPECS/ztmanager.spec \
	    --define "app_version $${VERSION}" \
	    --define "_topdir $${HOME}/rpmbuild"; \
	  cp ~/rpmbuild/SRPMS/*.src.rpm $(outdir)/
