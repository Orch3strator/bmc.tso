""" BMC Software Python Core Tools 

    Provide core functions for BMC Software related python scripts
"""
#!/usr/bin/env python3
#Filename: bmcs_base.py
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
import logging
import shutil
import io
import types
import datetime
from functools import wraps
from pathlib import Path
from shutil import copyfile

import psutil
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
 
def logStatus(key,val):
    print (str(key) + " =",  str(val))

def timer(start,end):
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return ("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
            
def getEpoch(timeVal,timeFormat):
    epoch = int(time.mktime(time.strptime(timeVal, timeFormat)))
    return epoch

def getCurrentTime():
    val = datetime.datetime.now()
    return val

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

def getFiles(path,pattern,extension):
    files = []
    with os.scandir(path) as listOfEntries:  
        for entry in listOfEntries:
            if entry.is_file():                
                if entry.name.startswith(pattern) and entry.name.endswith(extension):
                   file = os.path.join(path, entry.name)
                   file = os.path.normpath(file)
                   modified_date = getFileDate(file)
                   fileAge = datetime.datetime.today() - modified_date
                   if fileAge.days < 356:
                       files.append(file)                                               
    return files  

def renFile(source,dest):
    os.rename(source,dest)

def copyFile(source, target):
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

def getFileStatus(path):   
    return os.path.isfile(path)

def getCpuCount():
    return psutil.cpu_count()

def getCpuUtil():
    return psutil.cpu_percent(interval=None)    

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
    target = path
    lines = []
    if os.path.exists(target):
        try:
            with io.open(target,'r') as fp:
                    line = fp.readline()
                    cnt = 1          
                    while line:
                        lines.append(line)          
                        line = fp.readline()
                        cnt += 1
            fp.close
        except IOError as e:
            return str(e)
        except:
            return sys.exc_info() 

    return lines   

def writeFile(path,data):
    target = path
    if not os.path.exists(os.path.dirname(target)):
        try:
            os.makedirs(os.path.dirname(target))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    try:
        with open(path, 'w') as outfile:
            outfile.writelines(data)
        outfile.close() 
    except IOError as e:
        return str(e)
    except:
        return sys.exc_info()

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
            json.dump(data, outfile, indent=2, sort_keys=True)
    except IOError as e:
        return str(e)
    except:
        return sys.exc_info() 

         
# Import from git
def prettyjson(obj, indent=2, maxlinelength=80):
    
    """Renders JSON content with indentation and line splits/concatenations to fit maxlinelength.

    Only dicts, lists and basic types are supported"""

    items, _ = getsubitems(obj, itemkey="", islast=True, maxlinelength=maxlinelength)
    res = indentitems(items, indent, indentcurrent=0)

    return res

def getsubitems(obj, itemkey, islast, maxlinelength):

    items = []

    can_concat = True      # assume we can concatenate inner content unless a child node returns an expanded list
    isdict = isinstance(obj, dict)
    islist = isinstance(obj, list)
    istuple = isinstance(obj, tuple)

    # building json content as a list of strings or child lists

    if isdict or islist or istuple:
        if isdict: opening, closing, keys = ("{", "}", iter(obj.keys()))
        elif islist: opening, closing, keys = ("[", "]", range(0, len(obj)))
        elif istuple: opening, closing, keys = ("[", "]", range(0, len(obj)))    # tuples are converted into json arrays

        if itemkey != "": opening = itemkey + ": " + opening
        if not islast: closing += ","

        # Get list of inner tokens as list
        count = 0
        subitems = []
        itemkey = ""

        for k in keys:
            count += 1
            islast_ = count == len(obj)
            itemkey_ = ""
            if isdict: itemkey_ = basictype2str(k)
            inner, can_concat_ = getsubitems(obj[k], itemkey_, islast_, maxlinelength)    # inner = (items, indent)
            subitems.extend(inner)                      # inner can be a string or a list
            can_concat = can_concat and can_concat_     # if a child couldn't concat, then we are not able either

        # atttempt to concat subitems if all fit within maxlinelength

        if (can_concat):
            totallength = 0
            for item in subitems:
                totallength += len(item)
            totallength += len(subitems)-1     # spaces between items
            if (totallength <= maxlinelength): 
                str = ""
                for item in subitems:
                    str += item + " "      # add space between items, comma is already there
                str = str.strip()
                subitems = [ str ]         # wrap concatenated content in a new list
            else:
                can_concat = False
        # attempt to concat outer brackets + inner items
        if (can_concat):
            if (len(opening) + totallength + len(closing) <= maxlinelength):
                items.append(opening + subitems[0] + closing)
            else:
                can_concat = False
           
        if (not can_concat):
            items.append(opening)       # opening brackets
            items.append(subitems)      # Append children to parent list as a nested list
            items.append(closing)       # closing brackets

    else:
        # basic types
        strobj = itemkey
        if strobj != "": strobj += ": "
        strobj += basictype2str(obj)
        if not islast: strobj += ","
        items.append(strobj)
    

    return items, can_concat

def basictype2str(obj):
    if isinstance (obj, str):
        strobj = "\"" + str(obj) + "\""
    elif isinstance(obj, bool): 
        strobj = { True: "true", False: "false" }[obj]
    else:
        strobj = str(obj)
    return strobj

def indentitems(items, indent, indentcurrent):

    """Recursively traverses the list of json lines, adds indentation based on the current depth"""

    res = ""
    indentstr = " " * indentcurrent
    for item in items:
        if (isinstance(item, list)): 
            res += indentitems(item, indent, indentcurrent + indent)
        else:
            res += indentstr + item + "\n"

    return res


if __name__ == "__main__":
    logging.basicConfig(filename='bmcs.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logging.info('Analysis Started')
    logging.info('%s Version', _modVer)
    print (f"Version: {_modVer}")


