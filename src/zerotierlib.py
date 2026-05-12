#
# ZeroTier Class
# API version: 0.1.0
#
from pydbus import SystemBus
from pathlib import Path
import requests
import urllib3
import subprocess
import os
import json
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ZeroTierNetwork:
    COMMANDS = ('start', 'stop', 'enable', 'disable')
    BASE_URL = 'http://localhost:9993/'
    PATH = Path.home() / '.config' / 'ztlib'
    FILE = 'zt.conf'
    SERVICE = 'zerotier-one.service'

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.host_mode = False
        self.serviceStatus = None
        self.headers = {'X-ZT1-Auth': f'{api_token}'} if api_token else None
        self.read_token()

    def zt_start(self) -> str:
        try:
            if self.check_token(self.api_token):
                return 'OK'
            if self.read_token() in (401, 404) and self.check_token(self.get_token()):
                return 'OK'
            return 'MISSING ROOT PERMISSION'
        except Exception as e:
            return f'MISSING ROOT PERMISSIONS EXCEPTION: {e}'

    def zt_status(self) -> bool:
        try:
            cmd = f"flatpak-spawn --host systemctl is-active {self.SERVICE}"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout.strip() == "active"
        except Exception:
            return False

    def is_installed(self) -> bool:
        try:
            cmd = "flatpak-spawn --host which zerotier-one"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    def zt_enable_status(self) -> bool:
        try:
            cmd = f"flatpak-spawn --host systemctl is-enabled {self.SERVICE}"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.stdout.strip() == "enabled"
        except Exception:
            return False

    def service(self, setstatus: int) -> bool:
        """Sets the status of the service to 'start', 'stop', 'enable', or 'disable'."""
        if setstatus:
            try:
                self.serviceStatus = self.COMMANDS[setstatus - 1]
                self._zt_activate()
                return True
            except Exception as e:
                print(f"Error al cambiar el estado del servicio: {e}")
                return False

    def _zt_activate(self):
        bus = SystemBus()
        systemd = bus.get(".systemd1")
        actions = {
            self.COMMANDS[0]: lambda: systemd.StartUnit(self.SERVICE, "replace"),
            self.COMMANDS[1]: lambda: systemd.StopUnit(self.SERVICE, "replace"),
            self.COMMANDS[2]: lambda: (systemd.EnableUnitFiles([self.SERVICE], False, True), systemd.Reload()),
            self.COMMANDS[3]: lambda: (systemd.DisableUnitFiles([self.SERVICE], False), systemd.Reload())
        }
        action = actions.get(self.serviceStatus)
        if action:
            action()
        self.serviceStatus = None

    def save_token(self):
        config = {
            'X-ZT1-Auth': self.api_token,
            'host_mode': self.host_mode
        }
        configpath = self.PATH / self.FILE
        configpath.parent.mkdir(parents=True, exist_ok=True)
        with open(configpath, 'w') as configfile:
            json.dump(config, configfile, indent=4)
        os.chmod(configpath, 0o600)
        print(f"Token guardado en: {configpath}")

    def read_token(self) -> int:
        configpath = self.PATH / self.FILE
        if not configpath.exists():
            return 404
        with open(configpath, 'r') as configfile:
            config = json.load(configfile)
        
        self.host_mode = config.get('host_mode', False)
        api_token = config.get('X-ZT1-Auth')
        
        if api_token and self.check_token(api_token):
            self.api_token = api_token
            self.headers = {'X-ZT1-Auth': f'{api_token}'}
            return 200
            
        if self.host_mode:
            if self.get_token():
                return 200
                
        return 401

    def check_token(self, api_token: str) -> bool:
        try:
            url = self.BASE_URL + 'status'
            response = requests.get(url, headers={'X-ZT1-Auth': api_token}, verify=False)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error al verificar el token: {e}")
            return False

    def get_token(self) -> Optional[str]:
        try:
            cmd = "flatpak-spawn --host pkexec cat /var/lib/zerotier-one/authtoken.secret"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            clave_api = result.stdout.strip()
            if self.check_token(clave_api):
                self.api_token = clave_api
                self.headers = {'X-ZT1-Auth': f'{self.api_token}'}
                self.save_token()
                return clave_api
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener el token: {e}")
            return None

    def send_request(self, method: str, endpoint: str, data: Optional[dict] = None):
        try:
            url = self.BASE_URL + endpoint
            response = getattr(requests, method)(url, headers=self.headers, json=data, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return None

    def get_networks(self, network: Optional[str] = None):
        endpoint = f'network/{network}' if network else 'network'
        result = self.send_request('get', endpoint)
        return result if result is not None else []

    def join_networks(self, network: str):
        return self.send_request('post', f'network/{network}')

    def update_network(self, network: str, config: dict):
        return self.send_request('post', f'network/{network}', config)

    def leave_networks(self, network: str):
        return self.send_request('delete', f'network/{network}')

    def get_peers(self, network: Optional[str] = None):
        endpoint = f'peer/{network}' if network else 'peer'
        result = self.send_request('get', endpoint)
        return result if result is not None else []

    #Not tested.
    def create_network(self, config: dict):
        return self.send_request('post', 'network', config)
    
    def get_network_details(self, network_id: str):
        return self.send_request('get', f'network/{network_id}')

    def delete_network(self, network_id: str):
        return self.send_request('delete', f'network/{network_id}')
    
    def get_peer_details(self, peer_id: str):
        return self.send_request('get', f'peer/{peer_id}')
