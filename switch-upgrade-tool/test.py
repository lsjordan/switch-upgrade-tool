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
        self.screen.border(0)
        self.topLineNum = 0
        self.highlightLineNum = 0
        self.markedLineNums = []
        self.device_count = len(upgrades)
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
        ### !!!
        ### This is where you would write a function to parse lines into rows
        ### and columns. For this demo, I'll just create a bunch of random ints
        ### !!!
        list1 = []
        for x in range(0, self.device_count):
            list1.append(f"{x} TESTING")
        self.outputLines = list1
        self.nOutputLines = self.device_count

    def displayScreen(self):
        # clear screen
        self.screen.erase()

        # now paint the rows
        top = self.topLineNum
        bottom = self.topLineNum + curses.LINES
        for (
                index,
                line,
        ) in enumerate(self.outputLines[top:bottom]):
            linenum = self.topLineNum + index
            line = '%s' % (line, )

            # highlight current line
            if index != self.highlightLineNum:
                self.screen.addstr(index, 0, line)
            else:
                self.screen.addstr(index, 0, line, curses.A_BOLD)
        self.screen.refresh()

    # move highlight up/down one line
    def updown(self, increment):
        nextLineNum = self.highlightLineNum + increment

        # paging
        if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
            self.topLineNum += self.UP
            return
        elif increment == self.DOWN and nextLineNum == curses.LINES and (
                self.topLineNum + curses.LINES) != self.nOutputLines:
            self.topLineNum += self.DOWN
            return

        # scroll highlight line
        if increment == self.UP and (self.topLineNum != 0
                                     or self.highlightLineNum != 0):
            self.highlightLineNum = nextLineNum
        elif increment == self.DOWN and (
                self.topLineNum + self.highlightLineNum + 1
        ) != self.nOutputLines and self.highlightLineNum != curses.LINES:
            self.highlightLineNum = nextLineNum

    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()


if __name__ == '__main__':
    ih = GUI()
