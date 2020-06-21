import curses
import time


class GUI:
    """A class to handle the shell GUI"""
    def __init__(self, upgrades):
        self.upgrades = upgrades

    def get_status(self):
        """ a test"""
        for upgrade in self.upgrades:
            print(upgrade.status)

    def c_main(self, screen):
        """The main GUI window"""
        screen = curses.initscr()
        screen.addstr(0, 0, "This string gets printed at position (0, 0)")
        screen.addstr(
            3, 1, "Try Russian text: Привет")  # Python 3 required for unicode
        screen.addstr(4, 4, "X")
        screen.addch(5, 5, "Y")
        screen.refresh()
        time.sleep(15)

    def start(self):
        """Starts the GUI"""
        curses.wrapper(self.c_main)
