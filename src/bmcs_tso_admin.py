# https://communities.bmc.com/docs/DOC-113537
_modVer = "1.0"

import json
import os
import sys, getopt
import time
import logging
from urllib import parse as urlparse
from pathlib import Path

import bmcs_core_rest as bmcs
import bmcs_global as bmcg
import requests

log = logging.getLogger(__name__)

def getTsoBaseUrl():
    tso_hostname = bmcg.tso_hostname
    tso_port = bmcg.tso_port
    tso_protocol = bmcg.tso_protocol
    tso_base_url = "/baocdp/rest"
    return tso_protocol + "://" + tso_hostname + ":" + tso_port + tso_base_url
    
def getTsoLoginUrl():
    tso_url = "/login"
    return getTsoBaseUrl() + tso_url

def getTsoAdapterUrl():
    tso_url = "/adapter"
    return getTsoBaseUrl() + tso_url    

def getTsoAdapters(tso_auth_token):
    tso_adapters = []
    headers = {'Content-type': 'application/json;charset=UTF-8', "Authentication-Token":tso_auth_token,"configDataType":"json"}
    response = requests.get(getTsoAdapterUrl(), headers=headers)
    # for header in response.headers:
    #     print (f"TSO Header = {header}")
    tso_list = json.loads(response.content)
    tso_list = json.loads(response.text)
    tso_adapters = response.text
    return tso_adapters

def getTsoAdapterDetails(tso_adapters):
    adapters = {}
    adapters['adapters'] = []


    for item in tso_adapters:
        adapters["adapters"].append({
            "name": item["name"]
        })

    return adapters

        



def getTsoLogin():
    data = {"username":bmcg.tso_admin, "password":bmcg.tso_pwd} 
    headers = {'Content-type': 'application/json'}
    response = requests.post(getTsoLoginUrl(), json=data, headers=headers)        
    tso_auth_token = response.headers.get("Authentication-Token")
    return tso_auth_token

def initSettings(fileName):
    bmcg.tso_settings = bmcs.getFileContentJson(fileName)
    bmcg.tso_admin = bmcg.tso_settings['grids'][0]['user_name']
    bmcg.tso_pwd = bmcg.tso_settings['grids'][0]['user_password']
    bmcg.tso_hostname = bmcg.tso_settings['grids'][0]['hostname']
    bmcg.tso_port = bmcg.tso_settings['grids'][0]['port']
    bmcg.tso_protocol = bmcg.tso_settings['grids'][0]['protocol']
    bmcg.tso_grid = bmcg.tso_settings['grids'][0]['name']


if __name__ == "__main__":
    logging.basicConfig(filename='tso-admin.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logging.info('TSO REST Admin Started')
    logging.info('%s Version', _modVer)
    bmcg.init()
    

    # tso_auth_token = getTsoLogin()
    # tso_adapters = getTsoAdapters(tso_auth_token)

    # tso_adapters_count = len(tso_adapters)
    # print (f"TSO Adapter Count = {tso_adapters_count}")
    # for adapter in tso_adapters:
    #     print (f"TSO Adapter Name  = {adapter}")
    
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
            bmcg.verbose = True
        elif currentArgument in ("-h", "--help"):
            print (f"{bmcg.help}")
            print (f"{bmcg.usage}")
        elif currentArgument in ("-f", "--file"):
            fileName = str(Path(localFolder)/currentValue).lower()
            initSettings(fileName)
        elif currentArgument in ("-g", "--get"):
            bmcg.tso_action = "get"
        elif currentArgument in ("-s", "--set"):
            bmcg.tso_action = "set"

    logging.info(" - Current Folder: %s",format(localFolder))
    logging.info(" - Config File: %s",format(fileName))

    if bmcg.verbose:
        bmcs.logStatus(" - Current Folder %s",localFolder) 
        bmcs.logStatus(" - Config File",fileName) 
        bmcs.logStatus(" - TSO Grid",bmcg.tso_grid)   
        bmcs.logStatus(" - TSO Admin",bmcg.tso_admin)       
        bmcs.logStatus(" - CDP Host",bmcg.tso_hostname) 
        bmcs.logStatus(" - CDP Port",bmcg.tso_port) 
        bmcs.logStatus(" - CDP Protocol",bmcg.tso_protocol) 

    if bmcg.tso_action == "get":
        bmcg.tso_auth_token = getTsoLogin()
        # if bmcg.verbose:
        #     bmcs.logStatus(" - Authentication Token",bmcg.tso_auth_token)
        tso_adapters = getTsoAdapters(bmcg.tso_auth_token)
        if bmcs.jsonValidator(tso_adapters):
            bmcs.logStatus(" - TSO Adapters",tso_adapters)

        
        # tso_adapters_count = len(tso_adapters)

        # bmcs.logStatus(" - TSO Adapter Count",tso_adapters_count)
        # for adapter in tso_adapters:
        #     bmcs.logStatus(" - TSO Adapter Name",adapter)


    
  