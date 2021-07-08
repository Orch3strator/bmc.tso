#!/usr/bin/env python3
import os, sys, getopt, fnmatch, re
import multiprocessing as mp
from colorama import Fore, Back, Style, init
from dateutil.parser import parse
from pathlib import Path
from time import time
from multiprocessing import Pool
from multiprocessing import Process, Manager, freeze_support


def backline():        
    print('\r', end='') 
 
def getLocalFolder():
    path=str(os.path.dirname(os.path.abspath(__file__))).split('\\')
    return path[len(path)-1]

def getPeerFolders(path):
    peerList = []
    with os.scandir(path) as listOfEntries:  
        for entry in listOfEntries:
            if not entry.is_file():
               # print (Fore.WHITE + '- Log Folder: ', Fore.YELLOW + entry.name)
               peerList.append(entry.name)
    return peerList

def getPeerLogs(path):
    peerLogFiles = []
    with os.scandir(path) as listOfEntries:  
        for entry in listOfEntries:
            if entry.is_file():
               # print (Fore.WHITE + '- Log File  : ', Fore.YELLOW + entry.name)
                if entry.name.startswith("grid.log"):
                   logFile = os.path.join(path, entry.name)
                   peerLogFiles.append(logFile)
                elif entry.name.startswith("processes.log"):
                    logFile = os.path.join(path, entry.name)
                    peerLogFiles.append(logFile)                      
                elif entry.name.startswith("health.log"):
                    logFile = os.path.join(path, entry.name)
                    peerLogFiles.append(logFile)                                           
    return peerLogFiles
            
def execAnalysisProcessLog(logFile,afolder, logType, peer):
    lines        = []    
    logFileName  = os.path.basename(logFile)
    targetBase   = afolder 
    targetFolder = str(Path(os.path.join(targetBase, peer )))
    targetFile   = logFileName
       
    targetFileName = str(Path(os.path.join(targetBase, targetFolder, targetFile)))
    if not os.path.exists(targetFolder):
        os.makedirs(targetFolder)
         
    if logType in logFile:
        print(" ")
        print (Fore.WHITE + '- Process Log File     : ', Fore.YELLOW + logFile)
        print (Fore.WHITE + '- Create Analysis File : ', Fore.YELLOW + targetFileName)
        print(" - Processing ", end='')
        with open(logFile) as fp:
            line = fp.readline()
            cnt = 1          
            while line:
                logEntries = re.split(' \[|\] ',line)
                lTimestamp = logEntries[0]
                if is_date(lTimestamp):
                    # print("Line {}: {}".format(cnt, lTimestamp))
                    print(".", end='')
                    # backline()
                    lines.append(line)

                line = fp.readline()
                cnt += 1
        fp.close
        with open(targetFileName, 'w') as fo:
            fo.writelines(lines)
        fo.close


# 1. LOGGER  TIMESTAMP
# 2. [PROCESS TIMSTAMP]
# 3. [Process Name= CURRENT PROCESS NAME WHERE LOG IS GENERATED]
# 4. [Root Job ID=CURRENT ROOT JOB ID]
# 5. [JOB ID=HIERARCHICAL PATH FROM ROOT CALL PROCESS TO CURRENT CALL ACTIVITTY] 
# 6. [ProcessTermination=LAST PROCESS START WITH START AND END TIME STAMPS]


def execAnalysis(lfolder, afolder):
    rootPath = lfolder
    logFiles = []
    peerList = getPeerFolders(lfolder)
    for peer in peerList:
        print (Fore.WHITE + '- TSO Peer: ', Fore.YELLOW + peer)
        logFilePath = os.path.join(rootPath, peer)
        
        for logFile in getPeerLogs(logFilePath):
            execAnalysisProcessLog(logFile,afolder,"processes",peer)
            logFiles.append(logFile)

    #for logFile in logFiles:
    #    print (Fore.WHITE + '- TSO Peer Log File: ', Fore.YELLOW + logFile)

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False


def main(argv):
    cpu_max = mp.cpu_count()
    init()
    lfolder = ''
    afolder = ''
    

    try:
      opts, args = getopt.getopt(argv,"hl:a:",["lfolder=","afolder="])
    except getopt.GetoptError:
      print ('tso-process.py -l <Log Files Folder> -o <Analysis Report Folder>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
        print ('tso-process.py -l <Log Files Folder> -o <Analysis Report Folder>')
        sys.exit()
      elif opt in ("-l", "--lfolder"):
        lfolder = arg
      elif opt in ("-a", "--afolder"):
        afolder = arg
      else:
        print ('tso-process.py -l <Log Files Folder> -o <Analysis Report Folder>')
        sys.exit(2)

    if len(afolder) < 1:
        afolder = "D:\\Data\\TSO\\Analysis"
    if len(lfolder) < 1:
        lfolder = "D:\\Data\\TSO\\Logs\\Grid"     
    scriptPath = os.getcwd()       

    print (Fore.GREEN  + 'TSO Log File Anaysis ')
    print (Fore.WHITE + '- Processors: ', Fore.YELLOW + str(cpu_max))
    print (Fore.WHITE + '- Script    : ', Fore.YELLOW + scriptPath)
    print (Fore.WHITE + '- Log File  : ', Fore.YELLOW + lfolder)
    print (Fore.WHITE + '- Analysis  : ', Fore.YELLOW + afolder)

   
    
    # execAnalysis(lfolder ,afolder)
    # pool.close()
    # pool.join()


if __name__ == "__main__":
     # Multi Processor Support
    results = []
    freeze_support()
    pool = mp.Pool(mp.cpu_count())
    
    # main(sys.argv[1:])
