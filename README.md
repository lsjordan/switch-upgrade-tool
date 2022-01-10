# switch-upgrade-tool
Network switch OS upgrade tool. Primarily used for Cisco IOS

## Overview
In the default mode this tool will connect to a switch IP (or list of IP's) and gather all required information about the current OS version. It compares this to a simple config file, and displays if an OS upgrade is required. It also has copy, upgrade and reload modes, which can be used to fully automate the upgrade.

## Usage
Execute /scripts/swupgrade.py  

swupgrade.py (--host HOST | --list LIST) [--user USER] [--copy][--upgrade] [--reload] [--debug] [--help]  


switch upgrade utility

optional arguments:  
  --host HOST  switch IP address  
  --list LIST  File containing list of switch IP addresses  
  --user USER  Username to connect  
  --copy       Copy upgrade files to devices  
  --upgrade    Execute remote upgrade  
  --reload     Reload switches post upgrade  
  --debug      Debug logging  
  --help       Show this help msg and exit  

-- 2019 Liam Jordan | Italik LTD

## /backups/
Used during the copy, upgrade and reload phases. The switch config is saved to file automatically, the backups directory is the default save location.

## /configs/
Used to store config files. The swimages.yml file is required, and contains information about possible upgrades. This should be updated with the OS version you want to use.

## /images/
Used to store OS images. If you want to copy the image using the script, this is the default location. The file name should be the same as the image field in the swimages.yml file.

## /iplists/
The default directory the script uses to look for an iplist file. Should be in the same format as example.ip.
