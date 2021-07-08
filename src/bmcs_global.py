""" BMC Software TSO Analysis Helper 

    Provide global variables
"""
#!/usr/bin/env python3
#Filename: bmcs_global.py

import sys

bmcg = sys.modules[__name__]

# global variables
verbose = None
advanced = None
version = None
customerFile = None
customerDetails = None
analysisFolder = None
stagingFolder = None
mpPoolMultiplier = "1"

tso_settings = None
tso_auth_token = None
tso_admin = None
tso_pwd = None
tso_hostname = None
tso_port = None
tso_protocol = None
tso_grid = None
tso_action = None


help = "TrueSight Orchestration and Automation Value and Health Check Analysis Tool"
usage = "Usage: python tso-analysis.py --file 'customer.json' --help --verbose"

db_driver = "ODBC Driver 17 for SQL Server"
db_server = ""
db_port = "1443"
db_name = ""
db_user = ""
db_pwd = ""

_modVer = "1.0"

def init():
    
    global verbose
    global advanced
    global customerDetails
    global analysisFolder
    global version
    global mpPoolMultiplier

    version = ""
    verbose = False
    advanced = False
    customerDetails = {}
    analysisFolder = ""
    mpPoolMultiplier = "2"

if __name__ == "__main__":
    print (f"Version: {_modVer}")