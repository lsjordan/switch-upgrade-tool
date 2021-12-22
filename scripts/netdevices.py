"""
!/usr/bin/env python3

LiamJordan. For support: lsjordan.uk@gmail.com
A file containing network device classes
"""

import datetime as dt
import time

import paramiko
from netmiko import ConnectHandler
from scp import SCPClient

from logger import Logger


class InvalidConfigCommand(Exception):
    """Raised when the switch is not supported"""
    pass


def _progress(status, total, count):
    """A function to display a progress bar out to the terminal. Used in the
    copy file function"""
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = "#" * filled_len + "." * (bar_len - filled_len)
    # Drop bytes encoding
    try:
        status = status.decode("utf-8")
    except AttributeError:
        pass
    print("[%s] %s%s - %s" % (bar, percents, "%", status),
          end="\r",
          flush=True)
    return


class Switch:
    def __init__(self,
                 host,
                 username,
                 password,
                 type="cisco_ios",
                 debug_on=False):
        self.host = host
        self.log = Logger(self.host, debug_on)
        self.username = username
        self.password = password
        self.type = type
        self.connect = None
        self.allfacts = {}
        self.flashinfo = []
        self.log.debug("[__init__] complete")

    def ssh(self):
        """Establishes an SSH connection"""
        self.log.debug("Executing [ssh]")
        if not self.connect:
            self.connect = ConnectHandler(
                ip=self.host,
                username=self.username,
                password=self.password,
                device_type=self.type,
            )
        if not self.connect.is_alive():
            self.connect = None
            self.connect = self.ssh()
        self.log.debug("[ssh] complete")
        return self.connect

    def facts(self):
        """Gathers basic facts by running show version on the switch"""
        self.log.debug("Executing [base_facts]")
        self.allfacts.update(self.ssh().send_command("show ver",
                                                     use_textfsm=True)[0])
        self.log.debug("[base_facts] complete")
        return self.allfacts

    def running_image(self):
        """returns the current running_image in a standard format"""
        self.log.debug("Executing [running_image]")
        if not self.allfacts.get("running_image"):
            self.facts()
        if "/" not in self.allfacts["running_image"]:
            self.allfacts[
                "running_image"] = f"/{self.allfacts['running_image']}"
        self.log.debug("[running_image] complete")
        return self.allfacts["running_image"]

    def next_boot_file(self):
        """returns the bootfile configuration from running config in a standard
        format. This may not be the current boot image, but will be the
        bootfile used when the switch is reloaded. Used to identify if an
        upgrade is in progress."""
        self.log.debug("Executing [next_boot_file]")
        if not self.allfacts.get("nbf"):
            self.allfacts["nbf"] = (
                self.ssh().send_command("show boot | i BOOT path-list").split(
                    " : ")[-1].strip("flash:"))
        if "/" not in self.allfacts["nbf"]:
            self.allfacts["nbf"] = f"/{self.allfacts['nbf']}"
        self.log.debug("[next_boot_file] complete")
        return self.allfacts["nbf"]

    def reload_pending(self):
        """Checks if a reload is pending on the switch by comparing the current
        bootfile with the next_boot_file"""
        self.log.debug("Executing [reload_pending]")
        if self.running_image() == self.next_boot_file():
            self.log.debug("[reload_pending] complete")
            return False
        else:
            self.log.debug("[reload_pending] complete")
            return True

    def stacked(self):
        """Identifies if a switch is stacked by checking the number of serial
        numbers provided"""
        self.log.debug("Executing [stacked]")
        if not self.allfacts.get("stacked"):
            if not self.allfacts.get("serial"):
                self.facts()
            if len(self.allfacts["serial"]) != 1:
                self.allfacts.update({"stacked": True})
            else:
                self.allfacts.update({"stacked": False})
        self.log.debug("[stacked] complete")
        return self.allfacts["stacked"]

    def ios_xe(self):
        """Checks if the current IOS bootfile is an IOS-XE version"""
        self.log.debug("Executing [ios_xe]")
        if not self.allfacts.get("ios_xe"):
            if "packages.conf" in self.running_image():
                self.allfacts.update({"ios_xe": True})
            else:
                self.allfacts.update({"ios_xe": False})
        self.log.debug("[ios_xe] complete")
        return self.allfacts["ios_xe"]

    def version(self):
        """Returns the switch IOS version"""
        self.log.debug("Executing [version]")
        if not self.allfacts.get("version"):
            self.facts()
        self.log.debug("[version] complete")
        return self.allfacts["version"]

    def featureset(self):
        """Returns the switch featureset"""
        self.log.debug("Executing [featureset]")
        if not self.allfacts.get("featureset"):
            if not self.allfacts.get("running_image"):
                self.facts()
            if "lanlite" in self.allfacts["running_image"]:
                featureset = "lanlite"
            elif "lanbase" in self.allfacts["running_image"]:
                featureset = "lanbase"
            elif "universal" in self.allfacts["running_image"]:
                featureset = "universal"
            self.allfacts.update({"featureset": featureset})
        self.log.debug("[featureset] complete")
        return self.allfacts["featureset"]

    def family(self):
        """Returns the switch family"""
        self.log.debug("Executing [family]")
        if not self.allfacts.get("family"):
            if not self.allfacts.get("hardware"):
                self.facts()
            family = self.allfacts["hardware"][0].split("-")[1]
            if "+" in family:
                family = family.partition("+")[0].rstrip() + "+"
            self.allfacts.update({"family": family})
        self.log.debug("[family] complete")
        return self.allfacts["family"]

    def flash(self):
        """Gets the current flash information"""
        self.log.debug("Executing [flash]")
        self.flashinfo = self.ssh().send_command("dir", use_textfsm=True)
        for item in self.flashinfo[:]:
            if "d" in item['permissions']:
                self.flashinfo.extend(self.ssh().send_command(
                    f"dir {item['name']}", use_textfsm=True))
        self.log.debug("[flash] complete")
        return self.flashinfo

    def file_on_flash(self, file):
        """Checks if the given file exists on Flash"""
        self.log.debug("Executing [file_on_flash]")
        if len(self.flashinfo) == 0:
            self.flash()
        for item in self.flashinfo:
            if "d" not in item["permissions"]:
                if file in item["name"]:
                    self.log.debug("[file_on_flash] complete")
                    return True
        self.log.debug("[file_on_flash] complete")
        return False

    def free_space(self):
        """Returns the available space on flash in bytes"""
        self.log.debug("Executing [free_space]")
        if len(self.flashinfo) == 0:
            self.flash()
        self.log.debug("[free_space] complete")
        return self.flashinfo[0]["total_free"]

    def save_config(self):
        """Saves the current running config"""
        self.log.debug("Executing [save_config]")
        self.ssh().send_command("wr mem")
        self.log.debug("[save_config] complete")
        return True

    def backup_config(self, path="../backups/"):
        """Takes a copy of the current running config and saves it to the
        backup directory"""
        self.log.debug("Executing [backup_config]")
        self.ssh().send_command("show run")
        timestamp = dt.datetime.fromtimestamp(
            time.time()).strftime("%d%m%Y-%H%M%S")
        print(
            self.ssh().send_command("show run"),
            file=open(f"{path}{self.host}-{timestamp}.ios", "a"),
        )
        self.log.debug("[backup_config] complete")
        return True

    def send_file(self, file, destination):
        """Transfers a given file to switch flash memory"""
        self.log.debug("Executing [send_file]")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=self.host,
            username=self.username,
            password=self.password,
            allow_agent=False,
            look_for_keys=False,
        )
        scp = SCPClient(ssh.get_transport(), progress=_progress)
        scp.put(file, destination)
        scp.close()
        self.log.debug("[send_file] complete")
        return True

    def send_config(self, command):
        """Sends the given configuration command string to the switch"""
        self.log.debug("Executing [send_config]")
        if "% Invalid input" in self.ssh().send_config_set(command):
            raise InvalidConfigCommand(command)
        self.log.debug("[send_config] complete")
        return True

    def reload(self):
        """Reload the switch"""
        self.log.debug("Executing [reload]")
        connect = self.ssh()
        output = connect.send_command_timing("reload in 5")
        if "?" in output:
            output += connect.send_command_timing("y")
        self.log.debug("[reload] complete")
        return True
