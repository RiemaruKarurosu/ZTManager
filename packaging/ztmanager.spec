%global app_version 2.0.2

Name:           zt-manager
Version:        %{app_version}
Release:        1%{?dist}
Summary:        GTK4 graphical interface for ZeroTier networks
License:        GPL-3.0-or-later
URL:            https://github.com/RiemaruKarurosu/ZTManager
Source0:        https://github.com/RiemaruKarurosu/ZTManager/archive/refs/tags/v%{app_version}.tar.gz

BuildArch:      noarch
BuildRequires:  ninja-build
BuildRequires:  gettext
BuildRequires:  python3-devel
BuildRequires:  glib2-devel
BuildRequires:  desktop-file-utils

Requires:       python3
Requires:       python3-gobject
Requires:       python3-requests
Requires:       python3-pydbus
Requires:       python3-psutil
Requires:       gtk4
Requires:       libadwaita
Requires:       zerotier-one
Requires:       polkit

%description
ZT Manager is yet another graphical interface for managing ZeroTier
virtual networks on Linux. It allows you to join, leave, and configure
ZeroTier networks through a clean Adwaita-style interface.

%prep
%autosetup -n ZTManager-%{app_version}
%py3_shebang_fix .

%build
meson setup _build \
  --prefix=%{_prefix} \
  --bindir=%{_bindir} \
  --datadir=%{_datadir} \
  --sysconfdir=%{_sysconfdir} \
  --localstatedir=%{_localstatedir} \
  --buildtype=plain \
  -Dwerror=false
ninja -C _build %{?_smp_mflags}

%install
DESTDIR=%{buildroot} ninja -C _build install
%find_lang ztmanager

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/io.github.riemarukarurosu.ZTManager.desktop

%files -f ztmanager.lang
%{_bindir}/ztmanager
%{_datadir}/applications/io.github.riemarukarurosu.ZTManager.desktop
%{_datadir}/icons/hicolor/
%{_datadir}/glib-2.0/schemas/io.github.riemarukarurosu.ZTManager.gschema.xml
%{_datadir}/metainfo/io.github.riemarukarurosu.ZTManager.metainfo.xml
%{_datadir}/licenses/io.github.riemarukarurosu.ZTManager/
%{_datadir}/zt-manager/

%changelog
