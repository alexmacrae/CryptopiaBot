from wifi import Cell, Scheme
import os
import subprocess
import shlex
import string
import time


class Wifi():
    def __init__(self):

        self.ssids = None
        self.networksd = '/etc/wpa_config/networks.d/'
        self.get_ssids()

    def get_ssids(self):

        # get all cells from the air and make a list

        self.ssids = [cell.ssid for cell in Cell.all('wlan0')]

        return self.ssids

    def save(self, ssid, psk):
        # using wpa_config save the ssid to /etc/wpa_supplicant/wpa_supplicant.conf
        # -f forces overwrite of entry if it exists

        if psk:
            wpa_config_str = ['wpa_config', 'add', '-f', ssid, psk]
        else:
            wpa_config_str = ['wpa_config', 'add', '-fo', ssid, psk]  # -o = open, for open network

        subprocess.call(['wpa_config', 'migrate'])  # migrate any networks that may have been manually inputted into wpa_supplicant.conf to wpa_config
        subprocess.call(wpa_config_str)  # add to wpa_config (but not to wpa_supplicant.conf yet)
        subprocess.call(['wpa_config', 'make'])  # write to wpa_supplicant.conf

    def delete(self, ssid):
        subprocess.call(['wpa_config', 'del', ssid])

    def exists(self, ssid):
        # Tests if ssid exists in wpa_supplicant.
        # Stored as a file temporarily in /etc/wpa_config/networks.d/ and wpa_config inserts into wpa_supplicant.conf upon `make`
        if os.path.isfile(self.networksd + ssid + '.conf'):
            return True
        else:
            return False

            # subprocess.call('wpa_config show \"' + ssid + '\"')

    def enable(self, ssid):
        subprocess.call(['ifup', 'wlan0'])
        subprocess.call(['dhcpcd', 'wlan0'])

class NetworkInfo:
    def get_ip_address(self, interface):
        # Not a simple subprocess.call due to the need for a PIPE in the command
        # https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
        command_line_1 = "ip addr show " + interface
        args1 = shlex.split(command_line_1)
        command_line_2 = "grep -Po 'inet \K[\d.]+'"
        args2 = shlex.split(command_line_2)

        command_line_1 = subprocess.Popen(args1, stdout=subprocess.PIPE)
        command_line_2 = subprocess.Popen(args2, stdin=command_line_1.stdout, stdout=subprocess.PIPE)
        command_line_1.stdout.close()

        ip_address = command_line_2.communicate()[0]
        ip_address = ip_address.rstrip()

        if ip_address == '':
            ip_address = 'NOT CONNECTED'

        return str(ip_address)


if __name__ == '__main__':

    print '----START TESTING WIFI----'

    w = Wifi()
    print w.ssids


