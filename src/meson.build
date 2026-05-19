pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'ztmanager'
gnome = import('gnome')

gnome.compile_resources('ztmanager',
  'ztmanager.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', '/usr/bin/python3')
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'ztmanager.in',
  output: 'ztmanager',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

ztmanager_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'zerotierlib.py',
  'preferences.py',
  'installer.py',
]

install_data(ztmanager_sources, install_dir: moduledir)
