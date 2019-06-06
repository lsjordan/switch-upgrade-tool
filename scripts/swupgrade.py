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


def parse_arguments():
    """Manage arguments and help file"""
    parser = argparse.ArgumentParser(
        description="switch upgrade utility",
        epilog="(c) 2019 Liam Jordan",
        fromfile_prefix_chars="@",
        add_help=False,
    )
    host = parser.add_mutually_exclusive_group(required=True)
    host.add_argument("--host", help="switch IP address", action="append")
    host.add_argument("--list",
                      help="File containing list of switch IP addresses")
    parser.add_argument("--user", help="Username to connect", default="italik")
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
    valid = []
    if args.host:
        for host in args.host:
            hosts.append(host)
    elif args.list:
        with open(f"../iplists/{args.list}") as f:
            mylist = f.read().splitlines()
            for item in mylist:
                hosts.append(item)
    for host in hosts:
        try:
            ipaddress.ip_address(host)
            log.debug(f"{host} - Valid IP")
            valid.append(host)
        except ValueError:
            log.error(f"{host} - INVALID IP")
    return valid


def supported_switch(s):
    """Identify if the switch is supported by this upgrade process"""
    if s.ios_xe():
        raise SwitchNotSupported("IOS-XE")
    elif s.reload_pending():
        raise SwitchNotSupported("RELOAD PENDING")
    elif s.stacked():
        raise SwitchNotSupported("STACKED")
    return True


def yaml_loader(filepath):
    """Load a yaml file"""
    with open(filepath, "r") as myfile:
        return yaml.load(myfile)


def print_result(host, type, info, msg, msg_color, debug_on=False):
    """print the information from check_upgrade to the user"""
    s_log = Logger(host, debug_on=debug_on)
    if type == "error":
        s_log.error(info, msg, msg_color)
    elif type == "info":
        s_log.info(info, msg, msg_color)
    elif type == "success":
        s_log.success(info, msg, msg_color)
    else:
        s.log.error("Something went wrong")


def check_upgrade(s, images, image_path="../images/", debug_on=False):
    """Gathers information from switch and checks it against an images file.
    Will categorise the switch as either ready for file transfer or ready for
    upgrade. Returns both values, one will be empty"""
    type = "error"
    info = "NO INFO"
    msg = "NO MESSAGE"
    msg_color = "red"
    copy_s = None
    upgrade_s = None
    try:
        supported_switch(s)
        s.upgradefile = images[s.family()][s.featureset()]["image"]
        s.image_path = image_path
        s.next_version = images[s.family()][s.featureset()]["version"]
        info = f"[{s.family()}][{s.featureset()}][{s.version()}]"
        if not version.parse(s.version()) < version.parse(s.next_version):
            type = "info"
            msg = "No upgrade available"
            msg_color = "white"
        elif s.file_on_flash(s.upgradefile):
            type = "success"
            msg = f"upgrade to {s.next_version} - file already on flash"
            msg_color = "green"
            upgrade_s = s
        elif not os.path.isfile(f"{image_path}{s.upgradefile}"):
            type = "error"
            msg = f"upgrade to {s.next_version} - upgrade file not available"
            msg_color = "red"
        elif not int(os.stat(f"{image_path}{s.upgradefile}").st_size) < int(
                s.free_space()):
            type = "error"
            msg = f"upgrade to {s.next_version} - not enough space on flash"
            msg_color = "red"
        else:
            type = "success"
            msg = f"upgrade to {s.next_version} - file ready for transfer"
            msg_color = "yellow"
            copy_s = s
    except SwitchNotSupported as e:
        type = "error"
        info = "Not supported"
        msg = e
        msg_color = "red"
    except netmiko.ssh_exception.NetMikoTimeoutException:
        type = "error"
        info = "Unable to connect"
        msg = "Switch timed out"
        msg_color = "red"
    except KeyError as ke:
        type = "error"
        info = f"[{ke}]"
        msg = "Family not defined, check ../configs/swimages.yml"
        msg_color = "red"
    print_result(host=s.host,
                 type=type,
                 info=info,
                 msg=msg,
                 msg_color=msg_color,
                 debug_on=debug_on)
    return copy_s, upgrade_s


def copy_file(switch_list):
    """Transfers the s.upgradefile from local directory to switch flash, for a
    list of switches. Returns a list of successful switches."""
    success = []
    for switch in switch_list:
        switch.save_config()
        switch.backup_config()
        switch.send_config("ip scp server enable")
        if switch.send_file(f"{switch.image_path}{switch.upgradefile}",
                            f"flash:/{switch.upgradefile}"):
            success.append(switch)
    return success


def upgrade_switches(switch_list):
    """Sends an upgrade configuration to a switch, for a list of switches.
    Returns a list of successful switches"""
    success = []
    for switch in switch_list:
        switch.save_config()
        switch.backup_config()
        if switch.send_config(f"boot system flash:/{switch.upgradefile}"):
            success.append(switch)
    return success


def reload_switches(switch_list):
    """Sends a reload command to a switch, for a list of switches"""
    for switch in switch_list:
        switch.save_config()
        switch.backup_config()
        switch.reload()
    return True


def main(args):
    """Identify if a switch has an upgrade available. Can be used to copy IOS
    file, perform config upgrade or reload a switch"""
    log = Logger("[MAIN]", debug_on=args.debug)
    log.debug("Executing [main]")
    host_list = validate_hosts(args)
    copy_list = []
    upgrade_list = []
    reload_list = []
    images = yaml_loader("../configs/swimages.yml")
    password = getpass.getpass("Password: ")
    for host in host_list:
        sw = s(host, args.user, password)
        (copy_s, upgrade_s) = check_upgrade(sw, images, debug_on=args.debug)
        if copy_s is not None:
            copy_list.append(copy_s)
        if upgrade_s is not None:
            upgrade_list.append(upgrade_s)
    for host in copy_list:
        print(host.host)
    if args.copy:
        upgrade_list.append(copy_file(copy_list))
    if args.upgrade:
        reload_list.append(upgrade_switches(upgrade_list))
    if args.reload:
        reload_switches(reload_list)


if __name__ == "__main__":
    main(parse_arguments())
