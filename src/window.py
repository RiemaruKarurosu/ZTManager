# window.py
#
# Copyright 2024 Riemaru
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

from gi.repository import Adw
from gi.repository import Gtk
from zerotiergtk.zerotierlib import *

class NewNetwork(Gtk.Dialog):
    def __init__(self, parent, on_add_network_callback=None):
        super().__init__(title="Añadir Red", transient_for=parent)
        self.set_default_size(300, 150)
        self.on_add_network_callback = on_add_network_callback

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        self.set_titlebar(header_bar)

        self.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        self.add_button("Aceptar", Gtk.ResponseType.OK)

        content_area = self.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        content_area.append(box)

        self.network_id_entry = Gtk.Entry(placeholder_text="ID de Red")
        box.append(self.network_id_entry)

        self.connect("response", self.on_response)

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            network_id = self.network_id_entry.get_text()

            if self.on_add_network_callback:
                self.on_add_network_callback(network_id)

        self.close()


@Gtk.Template(resource_path='/org/zerotier/ZerotierGTK/window.ui')
class ZerotiergtkWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ZerotiergtkWindow'

    my_infobar = Gtk.Template.Child()
    action_row = Gtk.Template.Child()
    addnetwork = Gtk.Template.Child()
    refresh = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action_rows = []
        self.ztlib = ZeroTierNetwork()
        self._connect_signals()


    def _connect_signals(self):
        self.refresh.connect("clicked", self.on_refresh_clicked)
        self.addnetwork.connect("clicked", self.on_add_clicked)


    def _update_networks_list(self):
        self.remove_all_children()
        networks = self.ztlib.get_networks()

        if not networks:
            self._show_error_message("No se encontraron redes disponibles.")
            return

        for network in networks:
            self._create_network_action_row(network)


    def _create_network_action_row(self, network):
        action_row = self.action_row

        status_icon = self._get_network_status_icon(network["status"])

        row = Adw.ActionRow.new()
        row.set_title(network["name"])
        row.set_subtitle(f"NetID: {network['nwid']} Ip: {network['assignedAddresses']} Status: {network['status']}")
        row.set_icon_name(status_icon)

        switch = Gtk.Switch()
        button = Gtk.Button()
        button.set_icon_name("preferences-system")
        button.set_valign(Gtk.Align.CENTER)

        switch.set_halign(Gtk.Align.END)
        switch.set_valign(Gtk.Align.CENTER)

        row.add_suffix(switch)
        row.add_suffix(button)

        action_id = network["id"]
        self.action_rows.append(row)
        action_row.add(row)
        action_row.set_name(action_id)


    def on_check_lib(self):
        if self.ztlib.zt_status():
            self.my_infobar.set_visible(False)
            self.on_row_action()
            return True
        else:
            self.my_infobar.set_visible(True)
            return False


    def on_service_set(self, status):
        status = self.ztlib.service(status)
        self.on_check_lib()
        return status


    def on_refresh_clicked(self, widget):
        self.on_row_action()


    def on_add_clicked(self, widget):
        add_network_window = NewNetwork(self, self.add_network_callback)
        add_network_window.show()


    def add_network_callback(self, network_id):
        if network_id:
            self.ztlib.join_networks(network_id)
        else:
            self._show_error_message("ID de Red inválido.")


    def get_service_status(self):
        return self.ztlib.zt_enable_status()


    def remove_all_children(self):
        print(self.action_row.get_title())
        print(self.action_row.get_description())
        print(self.action_row.get_title())
        for i in self.action_rows:
            print(i)
            self.action_row.remove(i)


    def on_row_action(self):
        self.remove_all_children()
        networks = self.ztlib.get_networks()

        for network in networks:
            action_row = self.action_row

            if network["status"] == 'OK':
                status = 'emblem-default'
            elif network["status"] == 'ACCESS_DENIED':
                status = 'emblem-important'
            else:
                status = 'dialog-error'

            start = Adw.ActionRow.new()
            start.set_title(network["name"])
            start.set_subtitle(f"NetID: { network['nwid'] } Ip: {network['assignedAddresses']} Status: { network['status'] } ")
            start.set_icon_name(status)

            switch = Gtk.Switch()
            button = Gtk.Button()
            button.set_icon_name("preferences-system")
            button.set_valign(Gtk.Align.CENTER)

            switch.set_halign(Gtk.Align.END)
            switch.set_valign(Gtk.Align.CENTER)
            #switch.connect("notify::active")

            start.add_suffix(switch)
            start.add_suffix(button)

            action_id = network["id"]
            self.action_rows.append(start)
            action_row.add(start)
            action_row.set_name(action_id)


