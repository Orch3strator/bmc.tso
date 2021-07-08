""" BMC Software Python Core Tools 

    Provide core functions for BMC Software related python scripts
"""
#!/usr/bin/env python3
#Filename: bmcs_core_rest.py

import os
import platform
import re
import sys
import time
import json
import logging

from pathlib import Path

_modVer = "1.0"
_timeFormat = '%d %b %Y %H:%M:%S,%f'
log = logging.getLogger(__name__)


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

def jsonValidator(data):
    try:
        json.loads(data)
        return True
    except ValueError as error:
        print("invalid json: %s" % error)
        return False

if __name__ == "__main__":
    logging.basicConfig(filename='tso.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logging.info('TSO REST Admin Started')
    logging.info('%s Version', _modVer)
    print (f"Version: {_modVer}")