import curses

class GUI:
    """A class to handle the shell GUI"""
    def __init__(self, upgrades):
        self.upgrades = upgrades

    def get_status(self):
        """ a test"""
        for upgrade in self.upgrades:
            print(upgrade.status)
