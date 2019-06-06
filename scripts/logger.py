# !/usr/bin/env python3

# LiamJordan. For support: lsjordan.uk@gmail.com
# A class to handle logging

from colorama import init
from termcolor import colored as c


class Logger:
    def __init__(self, prefix=None, debug_on=False):
        # Initialise colorama to allow colours to work on Windows systems
        init()
        self.debug_on = debug_on
        self.prefix = prefix
        self.error_color = "red"
        self.success_color = "green"
        self.info_color = "white"
        self.debug_color = "grey"

    def info(self, message, status=None, status_color="grey"):
        if status:
            self.log("INFO", message, self.info_color, status, status_color)
        else:
            self.log("INFO", message, self.info_color)

    def success(self, message, status=None, status_color="grey"):
        if status:
            self.log("SUCCESS", message, self.success_color, status,
                     status_color)
        else:
            self.log("SUCCESS", message, self.success_color)

    def error(self, message, status=None, status_color="grey"):
        if status:
            self.log("ERROR", message, self.error_color, status, status_color)
        else:
            self.log("ERROR", message, self.error_color)

    def debug(self, message, status=None, status_color="grey"):
        if self.debug_on:
            if status:
                self.log("DEBUG", message, self.debug_color, status,
                         status_color)
            else:
                self.log("DEBUG", message, self.debug_color)

    def log(self, type, message, color, status=None, status_color=None):
        if status:
            if self.prefix:
                print(
                    c(f"[{type}] - {self.prefix}: {message}", color) +
                    c(f" - {status}", status_color))
            else:
                print(
                    c(f"[{type}] - {message}", color) +
                    c(f" - {status}", status_color))
        else:
            if self.prefix:
                print(c(f"[{type}] - {self.prefix}: {message}", color))
            else:
                print(c(f"[{type}] - {message}", color))


def main():
    pass


if __name__ == "__main__":
    main()
