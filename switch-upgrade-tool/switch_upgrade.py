# get and validate input
#     hosts
#     username
#     password
#     device type
#     upgrade level (check, copy, upgrade, reload)

# build a list of upgrade objects
# start upgrade workers
"""
!/usr/bin/env python3

Liam Jordan. For support: lsjordan.uk@gmail.com
An application to upgrade Network Switches
"""
import argparse
import getpass
import ipaddress

from gui import GUI
from switch import Switch
from upgrade import Upgrade


def parse_arguments():
    """Manage arguments and help file"""
    parser = argparse.ArgumentParser(
        description="switch upgrade tool",
        epilog="(c) 2020 Liam Jordan",
        fromfile_prefix_chars="@",
        add_help=False,
    )
    host = parser.add_mutually_exclusive_group(required=True)
    host.add_argument("--host", help="switch IP address")
    host.add_argument("--list",
                      help="File containing list of switch IP addresses")
    parser.add_argument("--user", help="Username to connect", required=True)
    parser.add_argument(
        "--prep",
        help="Save config, transfer files. BEWARE: JunOS devices will reboot",
        action="store_true")
    parser.add_argument("--upgrade",
                        help="Execute upgrade commands",
                        action="store_true")
    parser.add_argument("--reload",
                        help="Reload switches post upgrade",
                        action="store_true")
    parser.add_argument("--help",
                        help="Show this help msg and exit",
                        action="help")
    return parser.parse_args()


def initialise_hosts(args):
    """returns a list of hosts when given the program arguments"""
    if args.host:
        return [args.host]
    elif args.list:
        with open(f"../iplists/{args.list}") as f:
            return f.read().splitlines()
    else:
        raise Exception("How did you get here?")


def validate_hosts(hosts):
    """checks all hosts in a list are valid IP addresses"""
    for host in hosts:
        ipaddress.ip_address(host)


def main(args):
    """Execute main program"""
    hosts = initialise_hosts(args)
    validate_hosts(hosts)

    # get switch password
    password = getpass.getpass("Password: ")

    # init switch list
    switches = [Switch(host, args.user, password) for host in hosts]

    # init upgrade list
    upgrades = [Upgrade(switch) for switch in switches]

    # start GUI
    GUI(upgrades)

    # start upgrade workers
    # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #     [executor.submit(upgrade.start) for upgrade in upgrades]


if __name__ == "__main__":
    main(parse_arguments())
