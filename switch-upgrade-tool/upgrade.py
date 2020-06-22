# upgrade phases

# phase one - check
# gather info
# check if switch is supported
# check if an upgrade is available

# phase two - prep
# check switch is ready for upgrade
#     run backups
#     save configs
#     juniper, reload, clean file system

# phase 3 - transfer upgrade file
# check file exists
# check remote file exists
# check space available
# transfer file

# phase 4 - upgrade phase
# execute upgrade commands

# phase 5 - reboot
# ping device
# reload device
# wait for no response
# wait for response
# wait for SSH

# phase 6 - validate
# validate new version
# end
import time


class Upgrade(object):
    """A class to handle switch upgrade progress"""
    def __init__(self, switch):
        self.switch = switch
        self.host = switch.host
        self.status = "NOT STARTED"

    def start(self):
        """TESTING"""
        for x in range(5):
            self.status = f"the number {x}"
            time.sleep(5)
