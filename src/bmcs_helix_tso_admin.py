""" BMC Software Python Core Tools for TSO

    Provide core functions for BMC Software related python scripts
"""
#!/usr/bin/env python3
#Filename: bmcs_helix_tso_admin.py

import bmcs_helix_tso_core as bmcs
import logging
import json
import os, sys, getopt

from urllib import parse as urlparse
from pathlib import Path



logger_admin = logging.getLogger(__name__)
help = "TrueSight Orchestration and Automation Admin Tool"
usage = "Usage: python bmcs_helix_tso_admin.py --file 'tso.json' --help --verbose"

def main():
    localFolder = bmcs.getCurrentFolder()
    fileName = None
    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]
    unixOptions = "hf:vgs"
    gnuOptions = ["help", "file=", "verbose","get","set"]

    try:
        arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        sys.exit(2)

    for currentArgument, currentValue in arguments:
        if currentArgument in ("-v", "--verbose"):
            bmcs.verbose = True
        elif currentArgument in ("-h", "--help"):
            print (f"{help}")
            print (f"{usage}")
        elif currentArgument in ("-f", "--file"):
            fileName = str(Path(localFolder)/currentValue).lower()
        elif currentArgument in ("-g", "--get"):
            bmcs.tso_action = "get"
        elif currentArgument in ("-s", "--set"):
            bmcs.tso_action = "set"

    if bmcs.fileExists(fileName):
        bmcs.initSettings(fileName)
    
    

    logger_admin.info("Current Folder: %s",format(localFolder))
    logger_admin.info("Config File: %s",format(fileName))        

    try:
        if bmcs.verbose:
            logger_admin.info("Verbose Mode: %s",bmcs.verbose) 

    except:
        logger_admin.info("Status Config File: %s","Missing") 
        sys.exit(2)    


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG,filename='tso-admin.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logger_admin.info('TSO REST Admin Started')
    bmcs.init()
    logger_admin.info('TSO Admin Tool Version: %s', bmcs.version)

    main()
