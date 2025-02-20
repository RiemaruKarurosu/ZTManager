#
# ZeroTier Class
# API version: 0.1.0
#
from pydbus import SystemBus
from pathlib import Path

import requests
import subprocess
import os
import json


class ZeroTierNetwork:
    COMMANDS = ('start', 'stop', 'enable', 'disable')
    URL = 'http://localhost:9993/'
    PATH = Path.home() / '.config' / 'ztlib'
    FILE = 'zt.conf'
    SERVICE = 'zerotier-one.service'
    URL = 'https://localhost:9993/'

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.serviceStatus = None
        self.listNetworks = []
        if self.api_token:
            self.headers = {'X-ZT1-Auth': f'{api_token}'}
        else:
            self.headers = None
        print(self.zt_start())

    def zt_start(self) -> str:
        try:
            if self.check_token(self.api_token):
                return 'OK'
            
            if self.read_token() in (401, 404):
                if self.check_token(self.get_token()):
                    return 'OK'
                return 'MISSING ROOT PERMISSION'
            
            return 'OK'
        except Exception as e:
            return f'MISSING ROOT PERMISSIONS EXCEPTION: {e}'

    def zt_status(self) -> bool:
        unit = self.get_systemd_unit(self.SERVICE)
        if unit and unit[3] == "active" and unit[4] == 'running':
            return True
        return False


    def zt_enable_status(self) -> bool:
        unit = self.get_systemd_unit(self.SERVICE)
        if unit:
            return unit[3] == 'enabled'
        return False
        
    def service(self, setstatus):
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
        config = {'X-ZT1-Auth': self.api_token}
        configpath = self.PATH / self.FILE
        if not self.PATH.exists():
            self.PATH.mkdir(parents=True)
        if not configpath.exists():
            configpath.touch()

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
        api_token = config.get('X-ZT1-Auth')
        if api_token and self.check_token(api_token):
            self.api_token = api_token
            self.headers = {'X-ZT1-Auth': f'{api_token}'}
            return 200
        return 401
        

    def check_token(self, api_token: str) -> bool:
        try:
            url = self.URL + 'status'
            response = requests.get(url, headers={'X-ZT1-Auth': api_token})
            return response.status_code == 200
        except requests.exceptions.RequestException:
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
        except subprocess.CalledProcessError:
            return 'Error[01]: MissingRootAdmin'
            
    def send_request(self, method: str, endpoint: str, data: Optional[dict] = None):
        try:
            url = self.BASE_URL + endpoint
            response = getattr(requests, method)(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return None
    
    def get_networks(self, network: Optional[str] = None):
        endpoint = f'network/{network}' if network else 'network'
        return self.send_request('get', endpoint)
        
    def join_networks(self, network: str):
        return self.send_request('post', f'network/{network}')
        
    def update_network(self, network: str, config: dict):
        # Plan para la versión 2.0
        pass

    def leave_networks(self, network: str):
        return self.send_request('delete', f'network/{network}')

    def get_peers(self, network: Optional[str] = None):
        endpoint = f'peer/{network}' if network else 'peer'
        return self.send_request('get', endpoint)
