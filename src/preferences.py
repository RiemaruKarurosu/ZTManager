import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw
from gi.repository import Gtk
from zerotiergtk.zerotierlib import *


class PreferencesSettings:

    def __init__(self, zerotier_window, application):
        self.window_zerotier = zerotier_window
        self.zerotier = zerotier_window.ztlib
        window = Adw.PreferencesWindow(application=application)
        page = Adw.PreferencesPage()

        # Auth Mode
        auth_group = Adw.PreferencesGroup()
        auth_group.set_title("Autenticación")
        
        self.host_mode_row = Adw.ActionRow.new()
        self.host_mode_row.set_title("Usar Modo Host")
        self.host_mode_row.set_subtitle("Obtener token automáticamente del sistema (requiere permisos admin)")
        self.host_mode_switch = Gtk.Switch()
        self.host_mode_switch.set_active(self.zerotier.host_mode)
        self.host_mode_switch.set_valign(Gtk.Align.CENTER)
        self.host_mode_switch.connect("notify::active", self.on_host_mode_toggled)
        self.host_mode_row.add_suffix(self.host_mode_switch)
        auth_group.add(self.host_mode_row)
        
        # Token Input
        self.token_row = Adw.PasswordEntryRow.new()
        self.token_row.set_title("Token X-ZT1-Auth")
        if self.zerotier.api_token:
            self.token_row.set_text(self.zerotier.api_token)
        self.token_row.connect("changed", self.on_token_input_changed)
        self.token_row.set_visible(not self.zerotier.host_mode)
        auth_group.add(self.token_row)
        
        page.add(auth_group)

        # Zerotier Service
        service_group = Adw.PreferencesGroup()
        service_group.set_title("Zerotier Service")
        print(zerotier_window.get_service_status())
        self.create_action_rows(service_group, "Zerotier start", "The app needs this to work", self.on_switch_state_start,
                                zerotier_window.on_check_lib(), True)
        self.create_action_rows(service_group, "Zerotier start on boot",
                                "Start zerotier service on boot -NOT WORKING- go to terminal and type: sudo systemctl enable zerotier-one",
                                self.on_switch_state_enable, zerotier_window.get_service_status(), False)
        page.add(service_group)

        window.add(page)
        window.present()

    def on_switch_state_start(self, switch, state):
        active = switch.get_active()
        service_code = 1 if active else 2

        if not self.window_zerotier.on_service_set(service_code):
            switch.disconnect_by_func(self.on_switch_state_start)
            switch.set_active(not active)
            switch.connect("state-set", self.on_switch_state_start)
            return True
        return False

    def on_switch_state_enable(self, switch, state):
        active = switch.get_active()
        service_code = 3 if active else 4

        self.window_zerotier.get_service_status()
        print(self.window_zerotier.on_service_set(service_code))
        self.window_zerotier.get_service_status()
        print('encendido 1' if active else 'apagado 1')
        return True

    def create_action_rows(self, group, title, subtitle, activation, status, active):
        start = Adw.ActionRow.new()
        start.set_title(title)
        start.set_subtitle(subtitle)

        switch = Gtk.Switch()

        switch.set_active(status)
        switch.set_sensitive(active)

        switch.set_halign(Gtk.Align.END)
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("notify::active", activation)

        start.add_suffix(switch)
        group.add(start)

    def on_host_mode_toggled(self, switch, gparam):
        active = switch.get_active()
        self.zerotier.host_mode = active
        self.token_row.set_visible(not active)
        if active:
            token = self.zerotier.get_token()
            if token:
                self.token_row.set_text(token)
            else:
                self.zerotier.save_token()
        else:
            self.zerotier.save_token()
            
        self.window_zerotier.on_check_lib()

    def verify_token(self, token):
        return self.zerotier.check_token(token)

    def on_token_input_changed(self, entry):
        token = entry.get_text()
        if self.verify_token(token):
            print(f"Token verificado: {token}")
            self.zerotier.api_token = token
            self.zerotier.headers = {'X-ZT1-Auth': f'{token}'}
            self.zerotier.save_token()
            self.window_zerotier.on_check_lib()
        else:
            print("Token no válido. Por favor, introduce un token válido.")

    def show_info_dialog(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self.window_zerotier,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Información adicional aquí."
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


