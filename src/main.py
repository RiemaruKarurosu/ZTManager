# main.py
#
# Copyright 2026 Riemaru Karurosu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gettext
import locale
import os
import sys

DOMAIN = 'ztmanager'
LOCALEDIR = os.path.join(os.path.dirname(__file__), '..', 'share', 'locale')
if not os.path.exists(LOCALEDIR):
    LOCALEDIR = '/usr/share/locale'

gettext.bindtextdomain(DOMAIN, LOCALEDIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

import gi
from ztmanager.zerotierlib import *
from ztmanager.preferences import *

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import ZerotiergtkWindow


class ZerotierGtkApplication(Adw.Application):

    ztlib = ZeroTierNetwork()

    def __init__(self, version):
        self.version = version
        super().__init__(application_id='io.github.riemarukarurosu.ZTManager',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)
        self.zerotier_window = None

    def do_activate(self):
        self.zerotier_window = self.props.active_window
        if not self.zerotier_window:
            self.zerotier_window = ZerotiergtkWindow(application=self)
            self.zerotier_window.on_check_lib()
        self.zerotier_window.present()


    def on_about_action(self, widget, unused):
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name=_('ZT Manager'),
                                application_icon='io.github.riemarukarurosu.ZTManager',
                                developer_name='Riemaru Karurosu',
                                version=f'{self.version}',
                                developers=['Riemaru Karurosu'],
                                copyright=_('© 2026 Riemaru Karurosu'),
                                license_type=Gtk.License.GPL_3_0,
                                website='https://github.com/RiemaruKarurosu/ZT-Manager',
                                issue_url='https://github.com/RiemaruKarurosu/ZT-Manager/issues')
        about.present()

    def on_preferences_action(self, widget, unused):
        preferences = PreferencesSettings(self.zerotier_window, self)

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    app = ZerotierGtkApplication(version)
    return app.run(sys.argv)

