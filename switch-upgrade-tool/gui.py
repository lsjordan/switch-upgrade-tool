import curses


class GUI:
    DOWN = 1
    UP = -1
    ESC_KEY = 27

    def __init__(self, upgrades):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.topLineNum = 0
        self.padding = 7
        self.highlightLineNum = 0
        self.height, self.width = self.screen.getmaxyx()
        self.height = self.height - (self.padding * 2)
        self.device_count = 55
        # self.device_count = len(upgrades)
        self.getOutputLines()
        self.run()

    def run(self):
        while True:
            self.displayScreen()
            # get user command
            c = self.screen.getch()
            if c == curses.KEY_UP:
                self.updown(self.UP)
            elif c == curses.KEY_DOWN:
                self.updown(self.DOWN)
            elif c == self.ESC_KEY:
                self.exit()

    def getOutputLines(self):
        """Store switches and statuses"""
        list1 = []
        for x in range(0, self.device_count):
            list1.append(f"{x} TESTING")
        self.outputLines = list1
        self.nOutputLines = self.device_count

    def displayScreen(self):
        # clear screen
        self.screen.erase()
        self.screen.border(0)

        # Header
        self.screen.addstr(1, 4, "Switch Upgrade tool running...")
        self.screen.addstr(2, 4, "Liam Jordan, 2020")

        #Hostname
        top = self.topLineNum
        bottom = self.topLineNum + self.height
        for (
                index,
                line,
        ) in enumerate(self.outputLines[top:bottom]):
            # highlight current line
            if index != self.highlightLineNum:
                self.screen.addstr(index + self.padding, int(self.width / 4),
                                   line)
            else:
                self.screen.addstr(index + self.padding, int(self.width / 4),
                                   line, curses.A_BOLD)

        # Status
        # todo

        self.screen.refresh()

    # move highlight up/down one line
    def updown(self, increment):
        nextLineNum = self.highlightLineNum + increment

        # paging
        if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
            self.topLineNum += self.UP
            return
        elif increment == self.DOWN and nextLineNum == self.height and (
                self.topLineNum + self.height) != self.nOutputLines:
            self.topLineNum += self.DOWN
            return

        # scroll highlight line
        if increment == self.UP and (self.topLineNum != 0
                                     or self.highlightLineNum != 0):
            self.highlightLineNum = nextLineNum
        elif increment == self.DOWN and (
                self.topLineNum + self.highlightLineNum + 1
        ) != self.nOutputLines and self.highlightLineNum != self.height:
            self.highlightLineNum = nextLineNum

    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()
