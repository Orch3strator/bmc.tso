""" BMC Software Python Core Tools 

    Provide core functions for BMC Software related python scripts
"""
#!/usr/bin/env python3
#Filename: bmcs_core.py
import fnmatch
import getopt
import multiprocessing as mp
import os
import errno
import platform
import re
import sys
import time
import datetime
import json
import progressbar 
import pyodbc
import logging
import shutil
from functools import wraps
from pathlib import Path
from shutil import copyfile

import psutil
from colorama import Back, Fore, Style, init
from dateutil.parser import parse
from dateutil.tz import gettz


_modVer = "1.0"
_timeFormat = '%d %b %Y %H:%M:%S,%f'
log = logging.getLogger(__name__)

def sampleDoc():
    """
    Get path to export analysis reports
    
    Based of the underlying OS, the actual path name varies

    Note:
    
    Args: 
  
    Returns: 
        str: path to target analysis folder
    Raises:

    """
    pass

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.func_name, str(t1-t0))
               )
        return result
    return function_timer    

def getProcDuration(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd%dh%dm%ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%dh%dm%ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dm%ds' % (minutes, seconds)
    else:
        procTime = str(datetime.timedelta(seconds=seconds))
        return  procTime #'%ds' % (seconds,)

def timer(start,end):
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return ("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
            

def getEpoch(timeVal,timeFormat):
    epoch = int(time.mktime(time.strptime(timeVal, timeFormat)))
    return epoch

def getOsType():
    val = "" + platform.system() # + " " + platform.release() + " " + platform.version()
    return val

def backline():        
    print('\r', end='') 

def getLocalFolder():
    path=str(os.path.dirname(os.path.abspath(__file__))).split('\\')
    return path[len(path)-1]

def getCurrentFolder():
    path=str(os.path.dirname(os.path.abspath(__file__)))
    return path

def getParentFolder(folder):
    parentFolder = str(Path(folder).parent)
    return parentFolder

def getParentBaseFolder(folder):
    parentBaseFolder = str(os.path.basename(os.path.dirname(folder)))
    return parentBaseFolder

def getFileName(path):
    fileName = str(os.path.basename(path))
    return fileName

def getFileDate(path):
    try:
        fTime = os.path.getmtime(path)
    except OSError:
        fTime = 0
    fileTime = datetime.datetime.fromtimestamp(fTime)
    return fileTime
    

def getFolders(path):
    folderList = []
    with os.scandir(path) as listOfEntries:  
        for entry in listOfEntries:
            if not entry.is_file():
               folderList.append(entry.name)
    return folderList

def getFiles(path,pattern):
    files = []
    with os.scandir(path) as listOfEntries:  
        for entry in listOfEntries:
            if entry.is_file():                
                if entry.name.startswith(pattern):
                   # print (Fore.WHITE + '- Log File  : ', Fore.YELLOW + entry.name)
                   file = os.path.join(path, entry.name)
                   modified_date = getFileDate(file)
                   fileAge = datetime.datetime.today() - modified_date
                   if fileAge.days < 356:
                       files.append(file)                                               
    return files  

# def getCsvFileName(pattern):
#     """
#     Get file name for analysis report
    
#     Based on file pattern provided and default analysis folder

#     Note:
#         Increment file name, if file already exists to avoid duplicates
    
#     Args: 
#         pattern: file name pattern, example: "tso-analysis.csv"
  
#     Returns: 
#         str: new file name and path matching provided pattern, example: 'D:\\Data\\TSO\\Analysis\\tso-analysis-0001.csv'

#     """

#     file = os.path.join(getAnalysisPath(), pattern )
#     if not os.path.exists(file):
#         return file
#     filename, file_extension = os.path.splitext(file)
#     i = 1
#     fileIndex = str(i)
#     new_fname = "{}-{}{}".format(filename, fileIndex.zfill(4), file_extension)
#     while os.path.exists(new_fname):
#         i += 1
#         fileIndex = str(i)
#         new_fname = "{}-{}{}".format(filename, fileIndex.zfill(4), file_extension)
#     return new_fname    
 
def renFile(source,dest):
    os.rename(source,dest)

# def copyTsoLogFile(path):
#     target = tso.getTsoAnalysisFilePath(path)
#     source = path
#     try:
#         copyfile(source, target)
#     except IOError as e:
#         return str(e)
#     except:
#         return sys.exc_info()

def copyLogFile(source, target):
    if not os.path.exists(os.path.dirname(target)):
        try:
            os.makedirs(os.path.dirname(target))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    try:
        copyfile(source, target)
    except IOError as e:
        return str(e)
    except:
        return sys.exc_info()                  

def copyFolder(source, target):
    status = "OK"
    if os.path.exists(os.path.dirname(target)):
        try:
            shutil.rmtree(target)
        except IOError as ei:
            return str(ei)
        except:
            return sys.exc_info()             

    try:
        shutil.copytree(source, target)
    except OSError as eo:
        if eo.errno == errno.ENOTDIR:
            shutil.copy(source, target)
        return str(eo)
    except IOError as ei:
        return str(ei)
    except:
        return sys.exc_info() 
    return status

def getDateFromStr(timestamp):
    # 21 Feb 2019 08:15:19,033,
    match = timestamp.split(" ")
    date = str(match[0] + " " + match[1] + " " + match[2])
    return date
    
def getTimeFromStr(timestamp):
    # 21 Feb 2019 08:15:19,033,
    match = timestamp.split(" ")
    time = match[3].split(":")
    sec  = time[2].split(",")
    sTime = str(time[0] + ":" + time[1] + ":" + sec[0] )
    return sTime    

def getTimeInHourFromStr(timestamp):
    # 21 Feb 2019 08:15:19,033,
    match = timestamp.split(" ")
    time = match[3].split(":")
    sTime = str(time[0] + ":00:00" )
    return sTime  

def is_date(string):
    try: 
        parse(string,tzinfos={'IST': gettz('Asia/Calcutta'),'PDT': gettz('America/Los_Angeles'),'PST': gettz('America/Los_Angeles')})
        return True
    except ValueError:
        return False

def getFileStatus(path):   
    return os.path.isfile(path)

def logStatus(key,val):
    init() 
    print (Fore.WHITE + str(key) + " =",  Fore.YELLOW + str(val))

def getCpuCount():
    return psutil.cpu_count()

def getCpuUtil():
    return psutil.cpu_percent(interval=None)    

def conSql(driver,server,port,database,username,password):
    """
    Establish connection to RDBMS
    
    Connect to MS SQL server

    Note:
    
    Args: 
        driver: python OBDC driver, example: ODBC Driver 17 for SQL Server
        server: sql-server name
        port: database server port, example: 1443
        database: database name
        username: database user name
        password: databsae user password
    Returns: 
        cursor: cursor to database server
    Raises:

    """    
    try:
        cnxn = pyodbc.connect('DRIVER={'+driver+'};SERVER='+server+';PORT='+port+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
    except IOError as e:
            return str(e)
    except:
            return sys.exc_info()
    
    return cursor

def inserSql(cursor,tsql,values):
    status = "failed"
    #Insert Query
    # https://sqlchoice.azurewebsites.net/en-us/sql-server/developer-get-started/python/windows/step/2.html
    try:
        with cursor.execute(tsql,values):
            status = "success"
    except IOError as e:
            return str(e)
    except:
            return sys.exc_info()

    return status

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


def readFile(path):
    logFile = path
    lines = []
    with open(logFile) as fp:
            line = fp.readline()
            cnt = 1          
            while line:
                lines.append(line)          
                line = fp.readline()
                cnt += 1
    fp.close
    return lines   

def writeJsonFile(path,data):
    target = path
    if not os.path.exists(os.path.dirname(target)):
        try:
            os.makedirs(os.path.dirname(target))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    try:
        with open(path, 'w') as outfile:
            json.dump(data, outfile)
    except IOError as e:
        return str(e)
    except:
        return sys.exc_info() 

         

if __name__ == "__main__":
    logging.basicConfig(filename='tso.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logging.info('Analysis Started')
    logging.info('%s Version', _modVer)
    print (f"Version: {_modVer}")


