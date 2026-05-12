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
from gi.repository import GLib
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
    my_label_infobar = Gtk.Template.Child()
    install_zerotier_button = Gtk.Template.Child()
    action_row = Gtk.Template.Child()
    addnetwork = Gtk.Template.Child()
    refresh = Gtk.Template.Child()
    show_peers = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action_rows = []
        self.ztlib = ZeroTierNetwork()
        self._connect_signals()
        
        GLib.timeout_add_seconds(3, self._auto_refresh_tick)
        
    def _auto_refresh_tick(self):
        if not self.my_infobar.get_visible():
            self.on_row_action()
        return True


    def _connect_signals(self):
        self.refresh.connect("clicked", self.on_refresh_clicked)
        self.addnetwork.connect("clicked", self.on_add_clicked)
        self.show_peers.connect("clicked", self.on_show_peers_clicked)
        self.install_zerotier_button.connect("clicked", self.on_install_zerotier_clicked)


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
        has_service = self.ztlib.zt_status()
        has_token = self.ztlib.api_token and self.ztlib.check_token(self.ztlib.api_token)
        
        if has_service and has_token:
            self.my_infobar.set_visible(False)
            self.on_row_action()
            return True
        else:
            self.my_infobar.set_visible(True)
            if self.ztlib.host_mode and not self.ztlib.is_installed():
                self.my_label_infobar.set_label("ZeroTier-One is not installed on your system. Please install it to use this app in Host Mode.")
                self.install_zerotier_button.set_visible(True)
            elif not self.ztlib.host_mode and not self.ztlib.api_token:
                self.my_label_infobar.set_label("No token provided. Please go to Preferences and enter a valid X-ZT1-Auth Token.")
                self.install_zerotier_button.set_visible(False)
            else:
                self.my_label_infobar.set_label("Warning: You need to start the zerotier service. Go to Preferences, otherwise this app will not work.")
                self.install_zerotier_button.set_visible(False)
            return False

    def on_show_peers_clicked(self, widget):
        peers_dialog = PeersDialog(self, self.ztlib)
        peers_dialog.present()

    def on_install_zerotier_clicked(self, button):
        import subprocess
        cmd = "flatpak-spawn --host pkexec sh -c 'curl -s https://install.zerotier.com | bash'"
        try:
            subprocess.run(cmd, shell=True)
            self.on_check_lib()
        except Exception as e:
            print(f"Error installing zerotier: {e}")


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
            self.on_row_action()
        else:
            self._show_error_message("ID de Red inválido.")


    def get_service_status(self):
        return self.ztlib.zt_enable_status()


    def remove_all_children(self):
        for i in self.action_rows:
            try:
                self.action_row.remove(i)
            except Exception:
                pass
        self.action_rows.clear()


    def on_row_action(self):
        networks = self.ztlib.get_networks()
        if not isinstance(networks, list):
            return

        current_ids = {n["id"]: n for n in networks}
        rows_to_remove = [row for row in self.action_rows if row.get_name() not in current_ids]
        for row in rows_to_remove:
            try:
                self.action_row.remove(row)
            except Exception:
                pass
            self.action_rows.remove(row)

        for network in networks:
            action_id = network["id"]
            existing_row = next((r for r in self.action_rows if r.get_name() == action_id), None)

            if network["status"] == 'OK':
                status = 'emblem-default'
            elif network["status"] in ('REQUESTING_CONFIGURATION', 'WAITING_FOR_NETWORK_DATA', 'JOINING'):
                status = 'view-refresh'
            elif network["status"] == 'ACCESS_DENIED':
                status = 'emblem-important'
            else:
                status = 'dialog-error'

            name = network.get("name")
            if not name:
                name = network.get("nwid", network.get("id", "Unknown"))

            subtitle = f"NetID: { network['nwid'] } Ip: {network['assignedAddresses']} Status: { network['status'] } "

            if existing_row:
                try:
                    if existing_row.get_title() != name:
                        existing_row.set_title(name)
                    if existing_row.get_subtitle() != subtitle:
                        existing_row.set_subtitle(subtitle)
                    if existing_row.props.icon_name != status:
                        existing_row.set_icon_name(status)
                    if hasattr(existing_row, '_switch'):
                        new_state = network.get('allowManaged', True)
                        if existing_row._switch.get_active() != new_state:
                            existing_row._switch.set_active(new_state)
                except Exception as e:
                    print(f"Error updating row: {e}")
            else:
                start = Adw.ActionRow.new()
                start.set_name(action_id)
                start.set_title(name)
                start.set_subtitle(subtitle)
                start.set_icon_name(status)

                switch = Gtk.Switch()
                button = Gtk.Button()
                button.set_icon_name("preferences-system")
                button.set_valign(Gtk.Align.CENTER)

                switch.set_halign(Gtk.Align.END)
                switch.set_valign(Gtk.Align.CENTER)
                switch.set_active(network.get('allowManaged', True))
                switch.connect("state-set", self.on_network_switch_toggled, network["id"])
                start._switch = switch

                start.add_suffix(switch)
                button.connect("clicked", self.on_network_settings_clicked, network)
                start.add_suffix(button)

                self.action_rows.append(start)
                self.action_row.add(start)

    def on_network_switch_toggled(self, switch, state, network_id):
        config = {"allowManaged": state}
        self.ztlib.update_network(network_id, config)
        return False

    def on_network_settings_clicked(self, button, network):
        dialog = NetworkDetailsDialog(self, self.ztlib, network, self.on_row_action)
        dialog.show()

class PeersDialog(Gtk.Dialog):
    def __init__(self, parent, ztlib):
        super().__init__(title="Peers", transient_for=parent)
        self.set_default_size(500, 400)
        
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        self.set_titlebar(header_bar)

        content_area = self.get_content_area()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        scrolled.set_child(box)
        content_area.append(scrolled)
        
        peers = ztlib.get_peers()
        if peers:
            for peer in peers:
                row = Adw.ActionRow.new()
                row.set_title(f"Peer: {peer.get('address', 'Unknown')}")
                paths = peer.get('paths', [])
                ip = paths[0].get('address') if paths else 'No IP'
                latency = peer.get('latency', -1)
                row.set_subtitle(f"Role: {peer.get('role', 'Unknown')} | IP: {ip} | Latency: {latency}ms")
                box.append(row)
        else:
            lbl = Gtk.Label(label="No peers found.")
            box.append(lbl)

class NetworkDetailsDialog(Gtk.Dialog):
    def __init__(self, parent, ztlib, network, refresh_callback):
        super().__init__(title=f"Details: {network.get('name', 'Unknown')}", transient_for=parent)
        self.set_default_size(350, 400)
        self.ztlib = ztlib
        self.network_id = network.get("id")
        self.refresh_callback = refresh_callback
        
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        self.set_titlebar(header_bar)

        content_area = self.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(15)
        box.set_margin_bottom(15)
        box.set_margin_start(15)
        box.set_margin_end(15)
        content_area.append(box)
        
        group = Adw.PreferencesGroup()
        group.set_title("Network Information")
        
        self.add_info_row(group, "ID", self.network_id)
        self.add_info_row(group, "Name", network.get("name", "Unknown"))
        self.add_info_row(group, "MAC Address", network.get("mac", "Unknown"))
        self.add_info_row(group, "MTU", str(network.get("mtu", "Unknown")))
        self.add_info_row(group, "Status", network.get("status", "Unknown"))
        
        ips = ", ".join(network.get("assignedAddresses", []))
        self.add_info_row(group, "IPs", ips if ips else "None")
        
        box.append(group)
        
        remove_btn = Gtk.Button(label="Remove Network")
        remove_btn.add_css_class("destructive-action")
        remove_btn.connect("clicked", self.on_remove_clicked)
        box.append(remove_btn)

    def add_info_row(self, group, title, subtitle):
        row = Adw.ActionRow.new()
        row.set_title(title)
        row.set_subtitle(subtitle)
        
        copy_btn = Gtk.Button()
        copy_btn.set_icon_name("edit-copy-symbolic")
        copy_btn.set_valign(Gtk.Align.CENTER)
        copy_btn.add_css_class("flat")
        copy_btn.connect("clicked", self.on_copy_clicked, subtitle)
        row.add_suffix(copy_btn)
        
        group.add(row)
        
    def on_copy_clicked(self, button, text):
        clipboard = self.get_display().get_clipboard()
        clipboard.set(text)
        
    def on_remove_clicked(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text="¿Estás seguro de que deseas eliminar esta red?"
        )
        dialog.set_property("secondary-text", "Esta acción hará que ZeroTier olvide la red por completo.")
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        confirm_btn = dialog.add_button("Eliminar", Gtk.ResponseType.OK)
        confirm_btn.add_css_class("destructive-action")
        
        def on_response(d, response):
            if response == Gtk.ResponseType.OK:
                self.ztlib.leave_networks(self.network_id)
                if self.refresh_callback:
                    self.refresh_callback()
                self.close()
            d.destroy()
            
        dialog.connect("response", on_response)
        dialog.present()


