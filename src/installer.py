import subprocess
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from . import _


def _get_os_info() -> dict:
    info = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    info[k] = v.strip('"')
    except Exception:
        pass
    return info


def _build_install_script(os_id: str) -> str:
    if os_id == "nobara":
        return (
            "set -e\n"
            'echo "Importing ZeroTier GPG key..."\n'
            "rpm --import https://raw.githubusercontent.com/zerotier/ZeroTierOne/main/doc/contact%40zerotier.com.gpg\n"
            'echo "Adding ZeroTier RPM repository (Fedora)..."\n'
            "curl -fsSL -o /etc/yum.repos.d/zerotier.repo https://download.zerotier.com/redhat/zerotier.repo\n"
            'echo "Installing zerotier-one via dnf..."\n'
            "dnf install -y zerotier-one\n"
            'echo "Enabling and starting zerotier-one service..."\n'
            "systemctl enable zerotier-one\n"
            "systemctl start zerotier-one\n"
            'echo "Installation complete!"\n'
        )
    return "curl -s https://install.zerotier.com | bash"


class ZeroTierInstallerDialog(Adw.Window):
    def __init__(self, parent, on_install_complete=None):
        super().__init__(
            title=_("Install ZeroTier One"), transient_for=parent, modal=True
        )
        self.on_install_complete = on_install_complete
        self.set_default_size(660, 480)
        self._process = None

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(root)

        header = Adw.HeaderBar()
        root.append(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(18)
        content.set_margin_bottom(18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_vexpand(True)
        root.append(content)

        os_info = _get_os_info()
        os_id = os_info.get("ID", "").lower()
        os_name = os_info.get("NAME", _("Unknown OS"))

        if os_id == "nobara":
            os_text = _(
                "Detected: {} — Nobara patch will be applied (Fedora RPM path)"
            ).format(os_name)
        else:
            os_text = _("Detected: {}").format(os_name)

        os_label = Gtk.Label(label=os_text)
        os_label.set_xalign(0)
        os_label.add_css_class("dim-label")
        content.append(os_label)

        status_row = Gtk.Box(spacing=8)
        self.spinner = Gtk.Spinner()
        status_row.append(self.spinner)
        self.status_label = Gtk.Label(label=_("Click Install to begin."))
        self.status_label.set_xalign(0)
        self.status_label.set_hexpand(True)
        status_row.append(self.status_label)
        content.append(status_row)

        frame = Gtk.Frame()
        frame.set_vexpand(True)
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_min_content_height(240)

        self.output_view = Gtk.TextView()
        self.output_view.set_editable(False)
        self.output_view.set_monospace(True)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.output_view.set_margin_top(6)
        self.output_view.set_margin_bottom(6)
        self.output_view.set_margin_start(8)
        self.output_view.set_margin_end(8)
        self.output_buffer = self.output_view.get_buffer()
        self.end_mark = self.output_buffer.create_mark(
            "end", self.output_buffer.get_end_iter(), False
        )

        self.scrolled.set_child(self.output_view)
        frame.set_child(self.scrolled)
        content.append(frame)

        btn_box = Gtk.Box(spacing=8)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_margin_top(6)

        self.cancel_btn = Gtk.Button(label=_("Cancel"))
        self.cancel_btn.connect("clicked", self.on_cancel_clicked)
        btn_box.append(self.cancel_btn)

        self.install_btn = Gtk.Button(label=_("Install"))
        self.install_btn.add_css_class("suggested-action")
        self.install_btn.connect("clicked", self.on_install_clicked)
        btn_box.append(self.install_btn)

        content.append(btn_box)

    def on_install_clicked(self, button):
        self.install_btn.set_sensitive(False)
        self.spinner.start()
        self.output_buffer.set_text("")

        os_id = _get_os_info().get("ID", "").lower()
        script = _build_install_script(os_id)

        if os_id == "nobara":
            self._append_output(
                _(
                    "Nobara Linux detected.\n"
                    "The official install script does not support Nobara, so ZT Manager\n"
                    "will add the Fedora ZeroTier RPM repository and install via dnf.\n\n"
                )
            )
        else:
            self._append_output(_("Running official ZeroTier install script...\n\n"))

        self.status_label.set_label(_("Installing ZeroTier One — please wait..."))

        threading.Thread(target=self._run_install, args=(script,), daemon=True).start()

    def _run_install(self, script):
        try:
            self._process = subprocess.Popen(
                ["pkexec", "bash", "-c", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in iter(self._process.stdout.readline, ""):
                GLib.idle_add(self._append_output, line)
            self._process.stdout.close()
            self._process.wait()
            GLib.idle_add(self._on_done, self._process.returncode)
        except Exception as e:
            GLib.idle_add(self._append_output, f"\n{_('Error')}: {e}\n")
            GLib.idle_add(self._on_done, 1)

    def _append_output(self, text: str):
        end = self.output_buffer.get_end_iter()
        self.output_buffer.insert(end, text)
        self.output_buffer.move_mark(self.end_mark, self.output_buffer.get_end_iter())
        GLib.idle_add(self.output_view.scroll_mark_onscreen, self.end_mark)
        return False

    def _on_done(self, returncode: int):
        self.spinner.stop()
        self._process = None

        if returncode == 0:
            self.status_label.set_label(_("ZeroTier One installed successfully!"))
            self._append_output(_("\n✓ Done. You can now close this window.\n"))
            self.install_btn.set_label(_("Close"))
            self.install_btn.remove_css_class("suggested-action")
            self.install_btn.set_sensitive(True)
            self.install_btn.disconnect_by_func(self.on_install_clicked)
            self.install_btn.connect("clicked", lambda _: self.close())
            if self.on_install_complete:
                self.on_install_complete()
        else:
            self.status_label.set_label(
                _("Installation failed (exit code: {code})").format(code=returncode)
            )
            self.install_btn.set_label(_("Retry"))
            self.install_btn.set_sensitive(True)

        return False

    def on_cancel_clicked(self, button):
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass
        self.close()
