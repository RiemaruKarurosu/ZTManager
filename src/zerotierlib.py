#
# ZeroTier Class
# API version: 0.1.0
#
from pydbus import SystemBus
from pathlib import Path

import requests
import subprocess
import os


class ZeroTierNetwork:
    COMMANDS = ('start', 'stop', 'enable', 'disable')
    URL = 'http://localhost:9993/'
    PATH = Path.home() / '.config' / 'ztlib'
    FILE = 'zt.conf'
    SERVICE = 'zerotier-one.service'

    def __init__(self, api_token=None):
        self.api_token = api_token
        self.serviceStatus = None
        self.listNetworks = []
        if self.api_token:
            self.headers = {'X-ZT1-Auth': f'{api_token}'}
            print(self.api_token)
        else:
            self.headers = None
        print(self.zt_start())

    # Maybe Work(?
    def zt_start(self) -> str:
        try:
            if not self.check_token(self.api_token):
                if self.read_token() == 401 or self.read_token() == 404:
                    if self.check_token(self.get_token()):
                        return 'OK'
                    else:
                        return 'MISSING ROOT PERMISSION'
                return 'OK'
            return 'OK'
        except Exception:
            return 'MISSING ROOT PERMISSIONS EXCEPTION'



    # ZeroTier Status:

    # Check if ZeroTier-One is active
    # New Pydbus implementation
    def zt_status(self) -> bool:
        try:
            bus = SystemBus()
            systemd = bus.get(".systemd1")
            for unit in systemd.ListUnits():
                if unit[0] == self.SERVICE:
                    if unit[3] == "active" and unit[4] == 'running':
                        return True
                    else:
                        return False
            return False
        except Exception:
            return False



    def zt_enable_status(self) -> bool:
        try:
            bus = SystemBus()
            systemd = bus.get(".systemd1")
            state = systemd.GetUnitFileState(self.SERVICE)
            print(state)
            if state == 'enabled':
                return True
            elif state == 'disabled':
                return False
        except Exception:
            return False



    # Status ZeroTier-One service
    def service(self, setstatus):
        if setstatus:
            try:
                self.serviceStatus = self.COMMANDS[setstatus - 1]
                self._zt_activate()
                return True
            except Exception as e:
                print(e)
                return False

    def _zt_activate(self):
        bus = SystemBus()
        systemd = bus.get(".systemd1")
        if self.serviceStatus == self.COMMANDS[0]:
            response = systemd.StartUnit(self.SERVICE, "replace")
            print(response)
        elif self.serviceStatus == self.COMMANDS[1]:
            systemd.StopUnit(self.SERVICE, "replace")
        elif self.serviceStatus == self.COMMANDS[2]:
            systemd.EnableUnitFiles(['zerotier-one.service'], False, True)
            systemd.Reload()
        elif self.serviceStatus == self.COMMANDS[3]:
            systemd.DisableUnitFiles(['zerotier-one.service'], False)
            systemd.Reload()
        else:
            print("Error, no existe")

        self.serviceStatus = None

    # Save apiToken to ~/.config
    def read_token(self) -> int:
        configpath = self.PATH / self.FILE
        if configpath.exists():
            with open(configpath, 'r') as configfile:
                apitoken = configfile.readlines()
            for token in apitoken:
                if token.startswith('X-ZT1-Auth'):
                    key, value = token.split('=')
                    api_token = value.strip()
                    if self.check_token(api_token):
                        self.api_token = api_token
                        self.headers = {'X-ZT1-Auth': f'{api_token}'}
                    else:
                        return 401
            return 200
        else:
            return 404

    def check_token(self, api_token):
        url = self.URL + 'status'
        header = {'X-ZT1-Auth': f'{api_token}'}
        try:
            response = requests.get(url, headers=header)
        except Exception:
            return False
        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            return False
        else:
            return False

    def save_token(self):
        if not self.PATH.exists():
            self.PATH.mkdir(parents=True)
        configpath = self.PATH / self.FILE
        if not configpath.exists():
            configpath.touch()

        with open(configpath, 'w') as configfile:
            configfile.write(f'X-ZT1-Auth = {self.api_token} \n')

        os.chmod(configpath, 0o600)
        print(configpath)

    # Get the Token to use ZeroTierOne Service
    def get_token(self):
        try:
            cmd = "flatpak-spawn --host pkexec cat /var/lib/zerotier-one/authtoken.secret"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            clave_api = result.stdout.strip()
            print(f'Saving API: {clave_api}')
            if self.check_token(clave_api):
                self.api_token = clave_api
                self.headers = {'X-ZT1-Auth': f'{self.api_token}'}
                self.save_token()
                return clave_api
        except subprocess.CalledProcessError:
            return 'Error[01]: MissingRootAdmin'

        # ListNetworks

    def get_networks(self, network=None):
        if network:
            url = self.URL + 'network/' + network
        else:
            url = self.URL + 'network'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def join_networks(self, network):
        url = self.URL + 'network/' + network
        print(url)
        response = requests.post(url, headers=self.headers)
        return response.json()

    def update_network(self, network, config):
        # Version 2.0 plan.
        pass

    def leave_networks(self, network):
        url = self.URL + 'network' + network
        response = requests.delete(url, headers=self.headers)
        print(response)
        return response
        # Peers

    def get_peers(self, network=None):
        if network:
            url = self.URL + 'peer/' + network
        else:
            url = self.URL + 'peer'
        response = requests.get(url, headers=self.headers)
        print(response.json())
        return response.json()

