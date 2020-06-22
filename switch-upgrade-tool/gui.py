import curses
import time
from curses import textpad


class GUI(object):
    DOWN = 1
    UP = -1
    ESC_KEY = 27

    def __init__(self, upgrades):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.nodelay(True)
        self.screen.timeout(150)
        self.screen.keypad(1)
        self.topLineNum = 0
        self.highlightLineNum = 0
        self.output_hosts = []
        self.output_status = []
        self.window_height = 0
        self.list_height = 0
        self.width = 0
        self.padding = 0
        self.upgrades = upgrades
        self.device_count = len(upgrades)
        self.set_dimensions()
        self.get_host_names()

    def run(self):
        while True:
            self.displayScreen()
            # # get user command
            c = self.screen.getch()
            if c == curses.KEY_UP:
                self.updown(self.UP)
            elif c == curses.KEY_DOWN:
                self.updown(self.DOWN)
            elif c == self.ESC_KEY:
                self.exit()

    def set_dimensions(self):
        """reads the dimensions of the terminal and sets layout"""
        self.window_height, self.width = self.screen.getmaxyx()
        self.padding = int(0.2 * self.window_height)
        self.list_height = self.window_height - (self.padding * 2)
        return 0

    def get_status(self):
        """Read the upgrade statuses"""
        self.output_status = []
        for upgrade in self.upgrades:
            self.output_status.append(upgrade.status)

    def get_host_names(self):
        """Store switches and statuses"""
        for upgrade in self.upgrades:
            self.output_hosts.append(upgrade.host)

    def displayScreen(self):
        # clear screen
        self.screen.erase()

        # Header
        self.screen.addstr(1, 4, "Switch Upgrade tool running...")
        self.screen.addstr(2, 4, "Liam Jordan, 2020")

        top = self.topLineNum
        bottom = self.topLineNum + self.list_height

        # Box
        boxsize = int(0.15 * self.window_height)
        box = [[boxsize, boxsize],
               [self.window_height - boxsize, self.width - boxsize]]
        textpad.rectangle(self.screen, box[0][0], box[0][1], box[1][0],
                          box[1][1])

        #Hostname
        for (
                index,
                line,
        ) in enumerate(self.output_hosts[top:bottom]):
            # highlight current line
            if index != self.highlightLineNum:
                self.screen.addstr(index + self.padding, int(self.width / 4),
                                   line)
            else:
                self.screen.addstr(index + self.padding, int(self.width / 4),
                                   line, curses.A_STANDOUT)
        self.get_status()
        # Status
        for (
                index,
                line,
        ) in enumerate(self.output_status[top:bottom]):
            # highlight current line
            if index != self.highlightLineNum:
                self.screen.addstr(index + self.padding,
                                   int(((self.width / 4) * 3) - len(line)),
                                   line)
            else:
                self.screen.addstr(index + self.padding,
                                   int(((self.width / 4) * 3) - len(line)),
                                   line, curses.A_STANDOUT)
        self.screen.refresh()

    # move highlight up/down one line
    def updown(self, increment):
        nextLineNum = self.highlightLineNum + increment

        # paging
        if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
            self.topLineNum += self.UP
            return
        elif increment == self.DOWN and nextLineNum == self.list_height and (
                self.topLineNum + self.list_height) != self.device_count:
            self.topLineNum += self.DOWN
            return

        # scroll highlight line
        if increment == self.UP and (self.topLineNum != 0
                                     or self.highlightLineNum != 0):
            self.highlightLineNum = nextLineNum
        elif increment == self.DOWN and (
                self.topLineNum + self.highlightLineNum + 1
        ) != self.device_count and self.highlightLineNum != self.list_height:
            self.highlightLineNum = nextLineNum

    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()
