"""
!/usr/bin/env python3

LiamJordan. For support: lsjordan.uk@gmail.com
A script to upgrade Cisco switch IOS
"""

import argparse
import getpass
import ipaddress
import os

import netmiko
import yaml
from packaging import version

from logger import Logger
from netdevices import Switch as s


class SwitchNotSupported(Exception):
    """Raised when the switch is not supported"""
    pass


class global_arrays(object):
    """Store required global arrays for access by functions"""
    host_list = []
    copy_list = []
    upgrade_list = []
    reload_list = []


def parse_arguments():
    """Manage arguments and help file"""
    parser = argparse.ArgumentParser(
        description="switch upgrade tool",
        epilog="(c) 2019 Liam Jordan",
        fromfile_prefix_chars="@",
        add_help=False,
    )
    host = parser.add_mutually_exclusive_group(required=True)
    host.add_argument("--host", help="switch IP address")
    host.add_argument("--list",
                      help="File containing list of switch IP addresses")
    parser.add_argument("--user", help="Username to connect", required=True)
    parser.add_argument("--copy",
                        help="Copy upgrade files to devices",
                        action="store_true")
    parser.add_argument("--upgrade",
                        help="Execute remote upgrade",
                        action="store_true")
    parser.add_argument("--reload",
                        help="Reload switches post upgrade",
                        action="store_true")
    parser.add_argument("--debug", help="Debug logging", action="store_true")
    parser.add_argument("--help",
                        help="Show this help msg and exit",
                        action="help")
    return parser.parse_args()


def validate_hosts(args):
    """Reads in the host or list variable and returns a list of hosts"""
    log = Logger(["VALIDATE HOSTS"], debug_on=args.debug)
    hosts = []
    if args.host:
        hosts.append(args.host)
    elif args.list:
        try:
            with open(f"../iplists/{args.list}") as f:
                mylist = f.read().splitlines()
                for item in mylist:
                    hosts.append(item)
        except FileNotFoundError as e:
            log.error(e)
            quit()
    for host in hosts:
        try:
            ipaddress.ip_address(host)
            log.debug(f"{host} - Valid IP")
            global_arrays.host_list.append(host)
        except ValueError:
            log.error(f"{host} - INVALID IP")
    return True


def supported_switch(s):
    """Identify if the switch is supported by this upgrade process"""
    if s.ios_xe():
        raise SwitchNotSupported("IOS-XE")
    elif s.reload_pending():
        raise SwitchNotSupported("RELOAD PENDING")
    elif s.stacked():
        raise SwitchNotSupported("STACKED")
    return True


def yaml_loader(filepath, log):
    """Load a yaml file"""
    try:
        with open(filepath, "r") as myfile:
            return yaml.load(myfile)
    except FileNotFoundError as e:
        log.error(e)
        quit()


def print_result(host, status, info, msg, msg_color):
    """print the information from check_upgrade to the user"""
    s_log = Logger(host)
    if status == "error":
        s_log.error(info, msg, msg_color)
    elif status == "info":
        s_log.info(info, msg, msg_color)
    elif status == "success":
        s_log.success(info, msg, msg_color)
    else:
        s_log.error("Something went wrong")


def check_upgrade(s, images, image_path="../images/"):
    """Gathers information from switch and checks it against an images file.
    Will categorise the switch as either ready for file transfer or ready for
    upgrade. Returns both values, one will be empty"""
    status = "error"
    info = "NO INFO"
    msg = "NO MESSAGE"
    msg_color = "red"
    try:
        supported_switch(s)
        s.upgradefile = images[s.family()][s.featureset()]["image"]
        s.image_path = image_path
        s.next_version = images[s.family()][s.featureset()]["version"]
        info = f"[{s.family()}][{s.featureset()}][{s.version()}]"
        if not version.parse(s.version()) < version.parse(s.next_version):
            status = "info"
            msg = "No upgrade available"
            msg_color = "white"
        elif s.file_on_flash(s.upgradefile):
            status = "success"
            msg = f"upgrade to {s.next_version} - file already on flash"
            msg_color = "green"
            global_arrays.upgrade_list.append(s)
        elif not os.path.isfile(f"{image_path}{s.upgradefile}"):
            status = "success"
            msg = f"upgrade to {s.next_version} - upgrade file not available"
            msg_color = "red"
        elif not int(os.stat(f"{image_path}{s.upgradefile}").st_size) < int(
                s.free_space()):
            status = "success"
            msg = f"upgrade to {s.next_version} - not enough space on flash"
            msg_color = "red"
        else:
            status = "success"
            msg = f"upgrade to {s.next_version} - file ready for transfer"
            msg_color = "yellow"
            global_arrays.copy_list.append(s)
    except SwitchNotSupported as e:
        status = "error"
        info = "Not supported"
        msg = e
        msg_color = "red"
    except netmiko.ssh_exception.NetMikoTimeoutException:
        status = "error"
        info = "Unable to connect"
        msg = "Switch timed out"
        msg_color = "red"
    except KeyError as ke:
        status = "error"
        info = f"[{ke}]"
        msg = "Family not defined, check ../configs/swimages.yml"
        msg_color = "red"
    print_result(
        host=s.host,
        status=status,
        info=info,
        msg=msg,
        msg_color=msg_color,
    )
    return True


def copy_file(log):
    """Transfers the s.upgradefile from local directory to switch flash, for a
    list of switches. Returns a list of successful switches."""
    for switch in global_arrays.copy_list:
        log.info(f"{switch.host} - Preparing to copy file...")
        switch.save_config()
        switch.backup_config()
        switch.send_config("ip scp server enable")
        if switch.send_file(f"{switch.image_path}{switch.upgradefile}",
                            f"flash:/{switch.upgradefile}"):
            log.success(f"{switch.host} - Copy success")
            global_arrays.upgrade_list.append(switch)
        else:
            log.error(f"{switch.host} - Copy failed")
    return True


def upgrade_switches(log):
    """Sends an upgrade configuration to a switch, for a list of switches.
    Returns a list of successful switches"""
    for switch in global_arrays.upgrade_list:
        log.info(f"{switch.host} - Preparing to upgrade...")
        switch.save_config()
        switch.backup_config()
        if switch.send_config(f"boot system flash:/{switch.upgradefile}"):
            log.success(f"{switch.host} - Upgrade success")
            global_arrays.reload_list.append(switch)
        else:
            log.error(f"{switch.host} - Upgrade failed")
    return True


def reload_switches(log):
    """Sends a reload command to a switch, for a list of switches"""
    for switch in global_arrays.reload_list:
        log.info(f"{switch.host} - Preparing to reload...")
        switch.save_config()
        switch.backup_config()
        if switch.reload():
            log.success(f"{switch.host} - Reload success, reloading in 5 mins")
        else:
            log.error(f"{switch.host} - Reload failed")
    return True


def main(args):
    """Identify if a switch has an upgrade available. Can be used to copy IOS
    file, perform config upgrade or reload a switch"""
    log = Logger("[MAIN]", debug_on=args.debug)
    log.debug("Executing [main]")
    validate_hosts(args)
    images = yaml_loader("../configs/swimages.yml", log)
    password = getpass.getpass("Password: ")
    for host in global_arrays.host_list:
        sw = s(host, args.user, password, debug_on=args.debug)
        check_upgrade(sw, images)
    if args.copy:
        copy_file(log)
    if args.upgrade:
        upgrade_switches(log)
    if args.reload:
        reload_switches(log)


if __name__ == "__main__":
    main(parse_arguments())
