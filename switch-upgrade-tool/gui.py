import curses
import time


class GUI:
    """A class to handle the shell GUI"""
    def __init__(self, upgrades):
        self.upgrades = upgrades
        # self.device_count = len(upgrades)
        self.device_count = 10

    def get_status(self):
        """ a test"""
        for upgrade in self.upgrades:
            print(upgrade.status)

    def c_main(self, screen):
        """The main GUI window"""
        screen = curses.initscr()
        height, width = screen.getmaxyx()
        header = curses.newwin(3, width, 0, 0)
        header.addstr(1, 1, "Switch Upgrade tool running...")
        header.addstr(2, 1, "Liam Jordan, 2020")
        header.refresh()
        device = curses.newwin(self.device_count, int(width / 2), 4, 0)
        device.addstr(1, int(width / 4), "testing")
        for x in range(0, self.device_count):
            device.addstr(x, int(width / 4), "testing")
        device.refresh()
        time.sleep(15)

    def start(self):
        """Starts the GUI"""
        curses.wrapper(self.c_main)
