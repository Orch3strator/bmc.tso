""" BMC Software TSO Analysis 

    Analyse TSO infrastructure and workflow logs
"""
#!/usr/bin/env python3
#Filename: tso-analysis.py

import os
import sys, getopt
import time

from pathlib import Path
from multiprocessing import Pool, Process, cpu_count, current_process
from multiprocessing.dummy import Pool as ThreadPool

import bmcs_core as bmcs
import bmcs_tso as tso
import bmcs_global as bmcg


scriptPath = os.getcwd() 
_cpuCount = bmcs.getCpuCount()
_cpuUtil = bmcs.getCpuUtil()
_rootFolder = tso.getAnalysisPath()
_modVer = "1.0"
bmcg.analysisFolder = ""

def getCustomerDetails():
    bmcg.customerDetails = tso.getCustomerDetails(bmcg.customerFile)
    getGridVersion()
    getAnalysisPath()
    getMpPoolMultiplier()
    bmcg.stagingFolder = Path(bmcs.getParentFolder(bmcg.analysisFolder))/"staging"/getGridName()

def getMpPoolMultiplier():
    val = bmcg.customerDetails['mpPoolMultiplier']
    bmcg.mpPoolMultiplier = val
    return val

def getAnalysisPath():
    val = str(bmcg.customerDetails['folder']).lower()
    bmcg.analysisFolder = val
    return val

def getGridName():
    val = str(bmcg.customerDetails['grid']).lower()
    return val

def getGridVersion():
    val = bmcg.customerDetails['version']
    bmcg.version = val
    return val    

def getCustomerName():
    val = bmcg.customerDetails['customer']
    return val

def getCustomerID():
    val = bmcg.customerDetails['id']
    return val

def getGridPath(grid):
    path = str(Path(bmcg.analysisFolder)/grid).lower()
    return path

def getArchivePath(grid):

    path = bmcg.analysisFolder
    fileParent = bmcs.getParentFolder(path)
    # fileParentBase = bmcs.getParentBaseFolder(fileParent)
    # fileBase = bmcs.getParentBaseFolder(path)
    # fileName = bmcs.getFileName(path)
    # fileExt = Path(path).suffix.replace('.','')
    fileStagingParent = bmcs.getParentFolder(bmcg.analysisFolder)

    filePath = Path(fileStagingParent)/"archive"/grid    
    return filePath    

def getLogFiles(type):
    folder = str(getGridPath(getGridName())).lower()
    logFiles = tso.getLogFiles(folder,type)
    return logFiles

def getStagingLogFiles(type):
    folder = str(bmcg.stagingFolder).lower()
    logFiles = tso.getStagingLogFiles(folder,type)
    return logFiles    

def archiveLogs():
    gridName = getGridName()
    archivePath = str(getArchivePath(gridName)).lower()
    stagingPath = str(bmcg.stagingFolder).lower()
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" + Stage Archive","Start")
        bmcs.logStatus(" - Staging Folder",stagingPath)
        bmcs.logStatus(" - Archive Folder",archivePath)
    status = bmcs.copyFolder(stagingPath,archivePath)
    if bmcg.verbose:
        bmcs.logStatus(" - Archive Status",status)
        bmcs.logStatus(" + Stage Archive","End")  
    return status



def stagingLogFiles01():
    customerName = getCustomerName()
    gridName = getGridName()
    customerId = getCustomerID()
    processors = cpu_count()
    folder = str(bmcg.analysisFolder).lower()

    if bmcg.verbose:
        bmcs.logStatus(" - CPU Cores",processors)
        bmcs.logStatus(" - Customer",customerName)
        bmcs.logStatus(" - ID",customerId)
        bmcs.logStatus(" - Grid",gridName)
        bmcs.logStatus(" - Folder",folder)
        print("")
        bmcs.logStatus(" + Stage 01","Start")

    logFilesStdErr = getLogFiles("bao-cdp-stderr")
    logFilesStdOut = getLogFiles("bao-cdp-stdout")
    logFilesCatalina = getLogFiles("catalina")
    logFilesLocalHost = getLogFiles("localhost")

    logFilesProcess = getLogFiles("processes.log")
    logFilesGrid = getLogFiles("grid.log")
    logFilesHealth = getLogFiles("health.log")

    tso.stageLogFiles01("Std Error",logFilesStdErr)
    tso.stageLogFiles01("Std Out",logFilesStdOut)
    tso.stageLogFiles01("Catalina",logFilesCatalina)
    tso.stageLogFiles01("Grid",logFilesGrid)
    tso.stageLogFiles01("Process",logFilesProcess)
    tso.stageLogFiles01("Health",logFilesHealth)
    tso.stageLogFiles01("Local Host",logFilesLocalHost)
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 01","End")

def stagingLogFiles02():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" - Staging Folder",bmcg.stagingFolder)
        print("")
        bmcs.logStatus(" + Stage 02","Start")
    
    status = ""

    logFilesStdErr = getStagingLogFiles("tso-stderr")
    logFilesStdOut = getStagingLogFiles("tso-stdout")
    logFilesCatalina = getStagingLogFiles("tso-catalina")

    logFilesProcess = getStagingLogFiles("tso-processes")
    logFilesGrid = getStagingLogFiles("tso-grid")
    logFilesHealth = getStagingLogFiles("tso-health")

    tso.stageStdErrLogFile("Std Error",logFilesStdErr)
    tso.stageStdOutLogFile("Std Out",logFilesStdOut)
    tso.stageCatalinaLogFile("Catalina",logFilesCatalina)

    tso.stageGridLogFile("Grid",logFilesGrid)
    tso.stageProcLogFile("Process",logFilesProcess)
    tso.stageHealthLogFile("Health",logFilesHealth)
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 02","End")

    return status

def stagingLogFiles03():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" - Staging Folder",bmcg.stagingFolder)
        print("")
        bmcs.logStatus(" + Stage 03","Start")

    logFiles = getStagingLogFiles("tso-grid")
    logCount = len(logFiles)
    if bmcg.verbose:
        bmcs.logStatus(" - TSO Log Type","Grid")
        bmcs.logStatus(" - Analyzing Log Files",logCount)


    status = ""   
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 03","End")

    return status     

def stagingLogFiles7_2():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" - Staging Folder",bmcg.stagingFolder)
        print("")
        bmcs.logStatus(" + Stage 02","Start")
    
    status = ""

    logFilesStdErr = getStagingLogFiles("tso-stderr")
    logFilesStdOut = getStagingLogFiles("tso-stdout")
    logFilesCatalina = getStagingLogFiles("tso-catalina")

    logFilesProcess = getStagingLogFiles("tso-processes")
    logFilesGrid = getStagingLogFiles("tso-grid")
    logFilesHealth = getStagingLogFiles("tso-health")

    # tso.stageStdErrLogFile("Std Error",logFilesStdErr)
    # tso.stageStdOutLogFile("Std Out",logFilesStdOut)
    # tso.stageCatalinaLogFile("Catalina",logFilesCatalina)

    tso.stageGridLogFile("Grid",logFilesGrid)
    # tso.stageProcLogFile("Process",logFilesProcess)
    # tso.stageHealthLogFile("Health",logFilesHealth)
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 02","End")

    return status

def analyzeLogFilesGrid():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" + Stage 03 - Analysis Grid","Start")   
    tso.analyseGridLogs()
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 03 - Analysis Grid","End")     

def analyzeLogFilesHealth():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" + Stage 03 - Analysis Health","Start")      
    tso.analyseHealthLogs()
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 03 - Analysis Health","End")      

def analyzeLogFilesProcess():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" + Stage 03 - Analysis Process","Start")       
    tso.analyzeProcessLogs()
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 03 - Analysis Process","End")    

def analyzeLogFilesStdErr():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" + Stage 03 - Analysis Platform STD ERROR","Start")      
    tso.analyzeStdErrLogs()   
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 03 - Analysis Platform STD ERROR","End")       

def analyzeLogFilesCatalina():
    if bmcg.verbose:
        print("")
        bmcs.logStatus(" + Stage 03 - Analysis Platform Catalina","Start")     
    tso.analyzeCatalinaLogs()    
    if bmcg.verbose:
        bmcs.logStatus(" + Stage 03 - Analysis Platform Catalina","End")        


if __name__ == "__main__":
    bmcg.init()
    
    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]
    unixOptions = "hf:v"
    gnuOptions = ["help", "file=", "verbose"]

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
            bmcg.customerFile = Path(_rootFolder)/currentValue
            bmcg.customerFile = str(bmcg.customerFile).lower()
            getCustomerDetails()
            print (f"File: {currentValue}")


    print(f"==== TSO Log Analysis Collection ====")
    
    try:
        if bmcg.verbose:
            bmcs.logStatus(" - Root Folder",_rootFolder) 
            bmcs.logStatus(" - Verbose Mode",bmcg.verbose) 
            bmcs.logStatus(" - Customer Config File",bmcg.customerFile) 
            bmcs.logStatus(" - Customer Name",getCustomerName()) 
            bmcs.logStatus(" - Customer ID",getCustomerID()) 
            bmcs.logStatus(" - Log Analysis Path",getAnalysisPath()) 
    except:
        bmcs.logStatus(" - Status Config File","Missing") 
        print(f"=====================================")
        sys.exit(2)
    
    procStart = time.time()
    if str(bmcg.version).startswith("7.6"):
        stagingLogFiles01()
        stagingLogFiles7_2()
    
    if str(bmcg.version).startswith("8"):
        stagingLogFiles01()
        archiveLogs()
        stagingLogFiles02()
        analyzeLogFilesGrid()
        analyzeLogFilesHealth()
        analyzeLogFilesProcess()
        analyzeLogFilesStdErr()
        analyzeLogFilesCatalina()
        pass

    procEnd = time.time()
    procDuration = bmcs.timer(procStart,procEnd)
    bmcs.logStatus(" - Log Analysis Duration",procDuration) 
    print(f"=====================================")

