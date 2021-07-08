""" BMC Software Python Core Tools for TSO

    Provide core functions for BMC Software related python scripts
"""
#!/usr/bin/env python3
#Filename: bmcs_helix_tso_core.py

import logging
import time, datetime
import os, platform
import json
import requests
from pathlib import Path

_modVer = "1.0"
_timeFormat = '%d %b %Y %H:%M:%S,%f'
logging.basicConfig(level=logging.DEBUG, filename='tso-tools.log', filemode='a', format='%(asctime)s,%(levelname)s,%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)  

# global variables
verbose = None
advanced = None
version = None
tso_config_file = None
tso_settings = None
tso_admin = None
tso_pwd = None
tso_hostname = None
tso_port = None
tso_protocol = None
tso_grid = None
tso_action = None


def init():
    
    global verbose
    global advanced
    global version
    global tso_config_file
    global tso_settings
    global tso_admin
    global tso_pwd
    global tso_hostname
    global tso_port
    global tso_protocol
    global tso_grid
    global tso_action

    version = _modVer
    verbose = False
    advanced = False
    tso_config_file = ""
    tso_admin = "aoadmin"
    tso_pwd = "admin123"
    tso_hostname = "localhost"
    tso_port = 8080
    tso_protocol = "http"
    tso_grid = "GRID1"
    tso_action = "get"


def initSettings(fileName):
    global tso_config_file
    global tso_settings
    global tso_admin
    global tso_pwd
    global tso_hostname
    global tso_port
    global tso_protocol
    global tso_grid

    tso_config_file = str(fileName).lower()
    tso_settings = getFileContentJson(fileName)
    tso_admin = tso_settings['grids'][0]['user_name']
    tso_pwd = tso_settings['grids'][0]['user_password']
    tso_hostname = tso_settings['grids'][0]['hostname']
    tso_port = tso_settings['grids'][0]['port']
    tso_protocol = tso_settings['grids'][0]['protocol']
    tso_grid = tso_settings['grids'][0]['name']

    if verbose:
        logger.info("TSO Admin User: %s",tso_admin) 
        logger.info("TSO Admin Password: %s","$$$$$$$$") 
        logger.info("TSO Host: %s",tso_hostname) 
        logger.info("TSO Port: %s",tso_port) 
        logger.info("TSO Protocol: %s",tso_protocol) 
        logger.info("TSO Grid: %s",tso_grid) 



def getEpoch(timeVal,timeFormat):
    epoch = int(time.mktime(time.strptime(timeVal, timeFormat)))
    return epoch

def getOsType():
    val = "" + platform.system() # + " " + platform.release() + " " + platform.version()
    return val

def getCurrentFolder():
    path=str(os.path.dirname(os.path.abspath(__file__)))
    return path

def getFileJson(file):
    with open(file) as f:
        data = json.load(f)
    return data

def getFileContentJson(file):
    content = getFileJson(file)
    return content  

def fileExists(path):
    file = Path(path)
    if file.is_file():
        return True
    else:
        return False


if __name__ == "__main__":
    init()
  

    logger.info('TSO Tools Started')
    logger.info('%s Version', version)
    print (f"Version: {version}")    