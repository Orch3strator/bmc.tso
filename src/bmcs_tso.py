""" BMC Software TSO Analysis Helpe 

    Analyse TSO infrastructure and workflow logs, helper functions
"""
#!/usr/bin/env python3
#Filename: 
import os
import sys
import time
import timeit
import re
import json
import progressbar 
import logging
import bmcs_core as bmcs
import bmcs_global as bmcg
from pathlib import Path
from multiprocessing import Pool, Process, cpu_count, current_process
from datetime import datetime


_modVer = "1.0"
_timeFormat = '%d %b %Y %H:%M:%S,%f'
log = logging.getLogger(__name__)

scriptPath = os.getcwd() 

def getReportTime(time):
    temp = re.split(':',time)
    time = str(temp[0] + ":00:00")
    return time

def getAnalysisPath():
    """
    Get path to export analysis reports
    
    Based of the underlying OS, the actual path name varies

    Returns: 
        str: path to target analysis folder
    """

    sOsType = bmcs.getOsType()
    folderAnalysis = ""
    if "Darwin" in sOsType:
        folderAnalysis = "/Users/vscheith/Online Storage/Dropbox/Development/Logs"
    else:
        folderAnalysis = "D:\\Data\\TSO\\Analysis"
    return folderAnalysis

def getStagingGridPath(grid):
    folder = str(bmcg.analysisFolder).lower()
    path = str(Path(bmcs.getParentFolder(folder))/"staging"/grid).lower()
    return path

def getCustomerJson(file):
    # file = Path(getAnalysisPath())/"customer-01.json"
    with open(file) as f:
        data = json.load(f)
    return data

def getCustomerDetails(file):
    customer = getCustomerJson(file)
    return customer

def getTsoPeers (path):
    folders = bmcs.getFolders(path)
    return folders 

def getNewFilePath(path,count):
    fileParent = bmcs.getParentFolder(path)
    fileParentBase = bmcs.getParentBaseFolder(fileParent)
    fileBase = bmcs.getParentBaseFolder(path)
    fileName = bmcs.getFileName(path)
    fileExt = Path(path).suffix.replace('.','')
    fileStagingParent = bmcs.getParentFolder(bmcg.analysisFolder)

    filePath = Path(fileStagingParent)/"staging"/fileParentBase
    bmcg.stagingFolder = filePath
    

    if fileExt.isnumeric():
        fileStem = Path(Path(fileName).stem).stem  
        fileName = str("tso-" + fileStem + "." + fileExt.zfill(4) + ".log")

    if "catalina" in fileName:
        fileExt = str(count)
        fileName = str("tso-catalina." + fileExt.zfill(4) + ".log")
    elif "bao-cdp-stdout" in fileName:
        fileExt = str(count)
        fileName = str("tso-stdout." + fileExt.zfill(4) + ".log")
    elif "bao-cdp-stderr" in fileName:
        fileExt = str(count)
        fileName = str("tso-stderr." + fileExt.zfill(4) + ".log")


    filePath = str(filePath).lower()
    fileBase = str(fileBase).lower()
    fileName = str(fileName).lower()

    filePath = Path(os.path.join(filePath, fileBase, fileName))
    return filePath

def getLogFiles(path,pattern):
    """
    Get TSO log files
    
    Get list of TSO log files matching patter

    Note:
    
    Args: 
        path: path to log files
        pattern: matching file pattern for log file
  
    Returns: 
        list: list of TSO log files
    Raises:

    """
    logFilesAll = []
    peers = getTsoPeers(path)

    for peer in peers:
        logFiles = []
        logFilePath = os.path.join(path, peer)
        logFilesTmp = bmcs.getFiles(logFilePath,pattern)
        for logFile in logFilesTmp:
            if ".zip" in logFile:
                pass
            elif "log." in logFile:
                logFiles.append(logFile)
                logFiles = sorted( logFiles, key=lambda a: int(a.split(".")[2]) )
            elif "catalina" in logFile:
                logFiles.append(logFile)
            elif "stderr" in logFile:
                logFiles.append(logFile)
            elif "stdout" in logFile:
                logFiles.append(logFile)
            elif "localhost" in logFile:
                logFiles.append(logFile)
            elif "host-manager" in logFile:
                logFiles.append(logFile)                                 
            else:
                logFileParts = logFile.split('.')
                logFileName = str(logFileParts[0]) + "." + str(logFileParts[1]) + ".0"
                logFileNew = os.path.join(logFilePath, logFileName )
                bmcs.renFile(logFile,logFileNew)
                logFiles.append(logFileNew)
                logFiles = sorted( logFiles, key=lambda a: int(a.split(".")[2]) )

        for logFile in logFiles:
            logFilesAll.append(logFile)
    return logFilesAll    

def getStagingLogFiles(path,pattern):
    """
    Get TSO log files in staging folder
    
    Get list of TSO log files matching patter

    Note:
    
    Args: 
        path: path to log files
        pattern: matching file pattern for log file
  
    Returns: 
        list: list of TSO log files
    Raises:

    """
    logFilesAll = []
    peers = getTsoPeers(path)
    for peer in peers:
        logFiles = []
        logFilePath = os.path.join(path, peer)
        logFilesTmp = bmcs.getFiles(logFilePath,pattern)
        for logFile in logFilesTmp:
            if ".log" in logFile:
                logFiles.append(logFile)
        
        for logFile in logFiles:
            logFilesAll.append(logFile)
    return logFilesAll        

def stageLogFiles01(description,logFiles):
    pbar = progressbar.ProgressBar()
    logFileCount = len(logFiles)

    if logFileCount > 0:
        widgets = [' - ',description,': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
        cnt = 0
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=logFileCount)
        pbar.start()
        try:
            for logFile in pbar(logFiles):
                fileName = getNewFilePath(logFile,cnt)
                bmcs.copyLogFile(logFile, fileName)
                pbar.update(cnt + 1)
                cnt += 1
            pbar.finish()
        except Exception as ex:
            print(ex)
            
def readProcLogFile8(path):
    logFile = path
    lines = []
    with open(logFile) as fp:
            line = fp.readline()
            cnt = 1
            lTimestamp = ""
            while line:
                logEntries = re.split(' \[|\] ',line)
                if logEntries[0] != "":
                    lTimestamp = logEntries[0]
                # if is_date(lTimestamp):
                if lTimestamp[0].isdigit():
                    if "[ProcessTermination=" in line:
                        entry = ""
                        for logEntry in logEntries:                            
                            if logEntry != "":
                                if logEntry.find("[") == 0:
                                    logEntry = logEntry[1:]
                                entry = entry + "[" + logEntry.strip() + "]#"
                        entry = entry + "\n"
                        # entry = "[" + logEntries[1] + "] " + " ".join(logEntries[2:-1]) + "]\n"
                        lines.append(entry)
                line = fp.readline()
                cnt += 1
    fp.close
    return lines

def readProcLogFile7(path):
    logFile = path
    lines = []
    with open(logFile) as fp:
            line = fp.readline()
            cnt = 1
            lTimestamp = ""
            while line:
                logEntries = re.split(' \[|\] ',line)
                if logEntries[0] != "":
                    lTimestamp = logEntries[0]
                # if is_date(lTimestamp):
                if lTimestamp[0].isdigit():
                    if "[ProcessTermination=" in line:
                        entry = ""
                        for logEntry in logEntries:                            
                            if logEntry != "":
                                if logEntry.find("[") == 0:
                                    logEntry = logEntry[1:]
                                entry = entry + "[" + logEntry.strip() + "]#"
                        entry = entry + "\n"
                        # entry = "[" + logEntries[1] + "] " + " ".join(logEntries[2:-1]) + "]\n"
                        lines.append(entry)
                line = fp.readline()
                cnt += 1
    fp.close
    return lines

def readGridLogFile(path):
    logFile = path
    folder = bmcs.getParentFolder(logFile)
    gridName = str(bmcs.getParentBaseFolder(folder)).upper()
    lines = []
    with open(logFile) as fp:
            line = fp.readline()
            cnt = 1          
            while line:
                if line != "" and line[0].isdigit():
                    logEntries = re.split(' \[|\] ',line)
                    lTimestamp = logEntries[0]
                    #if is_date(lTimestamp):
                    if lTimestamp[0].isdigit():
                        entry = ""
                        for logEntry in logEntries:
                            if logEntry != "":
                                if logEntry.find("[") == 0:
                                    logEntry = logEntry[1:]     
                                    # if len(logEntry) > 201:
                                    #     logEntry = str(logEntry[0:200])
                                entry = entry + "[" + logEntry.strip() + "]#"
                        entry = entry + "\n"
                        lines.append(entry)   
                # if line != "" and line.startswith("HEALTH_STAT"):
                #     logEntries = re.split(',',line)
                #     for logEntry in logEntries:
                #         entry = entry + "[" + logEntry.strip() + "]#"
                #     entry = entry + "#\n"
                #     lines.append(line)


                if line != "" and "HEALTH_STAT" in line:
                    logEntries = re.split(',',line)
                    if logEntries[2].startswith(" G"):
                        logEntry = "G:"+gridName
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntry +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[5].strip(' \n') + ']\n'
                        lines.append(tmp)
                    elif "VM" in logEntries[4] and "HOST_VENDOR" in logEntries[4]:
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntries[2].strip() +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[6].strip(' \n') + ']\n'
                        lines.append(tmp)
                    else:
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntries[2].strip() +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[5].strip(' \n') + ']\n'
                        lines.append(tmp)
                line = fp.readline()
                cnt += 1
    fp.close
    return lines

def readLogFile(path):
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

def readHealthLogFile(path):      
    logFile = path
    folder = bmcs.getParentFolder(logFile)
    gridName = str(bmcs.getParentBaseFolder(folder)).upper()    

    lines = []
    with open(logFile) as fp:
            line = fp.readline()    
            while line:
                if line != "" and "HEALTH_STAT" in line:
                    logEntries = re.split(',',line)
                    if logEntries[2].startswith(" G"):
                        logEntry = "G:"+gridName
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntry +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[5].strip(' \n') + ']\n'
                        lines.append(tmp)
                    elif "VM" in logEntries[4] and "HOST_VENDOR" in logEntries[4]:
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntries[2].strip() +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[6].strip(' \n') + ']\n'
                        lines.append(tmp)
                    else:
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntries[2].strip() +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[5].strip(' \n') + ']\n'
                        lines.append(tmp)
                line = fp.readline()
    fp.close
    return lines  

def readStdErrLogFile(path):    
    gridName = bmcg.customerDetails['grid']
    logFile = path
    lines = []
    with open(logFile) as fp:
            line = fp.readline()
            while line:

                line1 = line
                line2 = fp.readline()
                if line2.startswith("SEVERE"):
                    logLevel = "SEVERE"
                    logIssue = ""
                    module = ""
                    workflow = ""                    
                    path = ""
                    jobId = ""
                    logEntry1 = re.split(' ',line1)
                    logEntry2 = re.split(':',line2)
                    logEntry2 = str(logEntry2[1:]).strip()
                    logEntry2 = logEntry2.replace("[","").replace("]","").replace("\\n","").strip()

                    logEntryDate = logEntry1[0] + ' ' + logEntry1[1] + ' ' + logEntry1[2]
                    logEntryTime = logEntry1[3] + ' ' + logEntry1[4]
                    logTimeStamp = logEntryDate  + ' ' + logEntryTime
                    logItem1 = logEntry1[5]
                    logItem2 = logEntry1[6].replace("\n","")

                    if line2.startswith('SEVERE: Process is COMPENSATED'):
                        module = ""
                        workflow = ""
                        path = ""
                        logIssue = "COMPENSATION"
    
                    elif line2.startswith('SEVERE: Process ":'):
                        logTmp = re.split('"',line2)
                        modTmp = re.split(':',logTmp[1])
                        module = modTmp[1]
                        workflow = modTmp[-1]
                        path = logTmp[1]



                    javaClass = logItem1
                    javaOperation = logItem2
                    logMessage = logEntry2
                    tmp = '['+ logTimeStamp +']#['+ logLevel + ']#[' + logIssue + ']#[' + javaClass + ']#[' + javaOperation + ']#[' + gridName + ']#[' + module + ']#[' + workflow + ']#[' +  path + ']#[' +  jobId + ']#[' + logMessage + ']\n'
                    lines.append(tmp)

                if line2.startswith("WARNING"):
                    logLevel = "WARNING"
                    logIssue = ""
                    module = ""
                    workflow = ""                    
                    path = ""
                    jobId = ""
                    logEntry1 = re.split(' ',line1)
                    logEntry2 = re.split(':',line2)
                    logEntry2 = str(logEntry2[1:]).strip()
                    logEntry2 = logEntry2.replace("[","").replace("]","").replace("\\n","").strip()

                    logEntryDate = logEntry1[0] + ' ' + logEntry1[1] + ' ' + logEntry1[2]
                    logEntryTime = logEntry1[3] + ' ' + logEntry1[4]
                    logTimeStamp = logEntryDate  + ' ' + logEntryTime
                    logItem1 = logEntry1[5]
                    logItem2 = logEntry1[6].replace("\n","")

                    if line2.startswith('WARNING: Process is'):
                        module = ""
                        workflow = ""                    
                        path = ""
                        jobId = ""
    
                    elif line2.startswith('WARNING: Process ":'):
                        logTmp = re.split('"',line2)
                        modTmp = re.split(':',logTmp[1])
                        module = modTmp[1]
                        workflow = modTmp[-1]
                        path = logTmp[1]

                    javaClass = logItem1
                    javaOperation = logItem2
                    logMessage = logEntry2

                    tmp = '['+ logTimeStamp +']#['+ logLevel + ']#[' + logIssue + ']#[' + javaClass + ']#[' + javaOperation + ']#[' + gridName + ']#[' + module + ']#[' + workflow + ']#[' +  path + ']#[' +  jobId + ']#[' + logMessage + ']\n'
                    lines.append(tmp)

                # job for job ID
                if  line1 != "" and "job for job ID [" in line1:
                    logLevel = "ERROR"
                    logIssue = "EXECUTION"
                    module = ""
                    workflow = ""                    
                    path = ""
                    jobId = ""
                    javaClass = ""
                    javaOperation = ""
                    logMessage = ""                    

                    jobIdTmp1 = re.split("=",line1)
                    jobIdTmp2 = str(jobIdTmp1[1:])
                    jobIdTmp3 = jobIdTmp2.split("[")
                    jobIdTmp4 = jobIdTmp3[2].split("]")
                    jobId = str(jobIdTmp4[0])

                    javaClass = str(jobIdTmp1[0].split(":")[1]).strip()
                    logMessage = str(jobIdTmp1[1].split(",")[0]).strip()
                    tmp = '['+ logTimeStamp +']#['+ logLevel + ']#[' + logIssue + ']#[' + javaClass + ']#[' + javaOperation + ']#[' + gridName + ']#[' + module + ']#[' + workflow + ']#[' +  path + ']#[' +  jobId + ']#[' + logMessage + ']\n'

                line = fp.readline()
    fp.close
    return lines  

def readStdOutLogFile(path):    
    gridName = bmcg.customerDetails['grid']
    logFile = path
    lines = []
    with open(logFile) as fp:
            line = fp.readline()    
            while line:
                if line != "" and "HEALTH_STAT" in line:
                    logEntries = re.split(',',line)
                    if logEntries[2].startswith(" G"):
                        logEntry = "G:"+gridName
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntry +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[5].strip(' \n') + ']\n'
                        lines.append(tmp)
                    elif "VM" in logEntries[4]:
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntries[2].strip() +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[6].strip(' \n') + ']\n'
                        lines.append(tmp)
                    else:
                        tmp = '['+logEntries[0].strip() +']#[' + logEntries[1].strip() +']#['+ logEntries[2].strip() +']#['+ logEntries[3].strip() +']#['+ logEntries[4].strip() +']#['+ logEntries[5].strip(' \n') + ']\n'
                        lines.append(tmp)
                line = fp.readline()
    fp.close
    return lines

def readCatalinaLogFile8(path):    
    gridName = bmcg.customerDetails['grid']
    logFile = path
    lines = []
    with open(logFile) as fp:
            line = fp.readline()
            while line:
                module = ""
                workflow = ""                    
                path = ""
                jobId = ""         
                
                if line != "":       
                    logEntryTmp = re.split(' ',line)
                    if bmcg.version.startswith("8"):
                        if "SEVERE" in logEntryTmp:
                            logIssue = ""
                            logLevel = logEntryTmp[2]
                            logDate = logEntryTmp[0]
                            logTime = logEntryTmp[1]
                            logTimeStamp = logDate + " " + logTime
                            javaClass = logEntryTmp[4]
                            javaOperation = logEntryTmp[3].replace("[","").replace("]","").strip()                    
                            logMessage = str(" ".join(logEntryTmp[5:]).strip(' \n').replace("[", "").replace("]", ""))
                            pass

                            if "summary=" in logMessage:
                                logMessageTmp = logMessage.split("=")
                                logMessage = str(" ".join(logMessageTmp[1:]))

                            if "execute-process" in logMessage:
                                logMessageTmp = logMessage.split(",")
                                module = logMessageTmp[5].strip()
                                path = logMessageTmp[6].replace(".","").replace('"',"").strip()     
                                workflow = path.split(":")[-1]
                                if "authorization" in logMessage:
                                    logIssue = "AUTHORIZATION"

                            if "Proc" in logMessage and "not be found" in logMessage:
                                logMessageTmp = logMessage.split('"')
                                pathTmp = logMessageTmp[1].split(":")
                                path = logMessageTmp[1]
                                module = pathTmp[1]
                                workflow = pathTmp[-1]     
                                logIssue = "AVAILABILITY"             

                            if "COMPENSATED" in logMessage:
                                logIssue = "COMPENSATION"    
                            if "Process is CANCELLED." in logMessage:
                                logIssue = "AVAILABILITY"  
                                logLevel = "WARNING"                            
                            if "exception occurred" in logMessage:
                                logIssue = "EXCEPTION"      
                            if "Exception thrown during phase execution" in logMessage:
                                logIssue = "EXCEPTION"      
                            if "caught throwable" in logMessage:
                                logIssue = "EXCEPTION"   
                            if "java.lang.NullPointerException" in logMessage:
                                logIssue = "EXCEPTION"                                                                                     
                            if "Invalid input. No result generated." in logMessage:
                                logIssue = "INVALID"     
                            if "Error in Verifying Security" in logMessage:
                                logIssue = "AUTHORIZATION"    
                            if "probable memory leak" in logMessage:
                                logIssue = "MEMORY"   
                            if "likely to create a memory leak" in logMessage:
                                logIssue = "MEMORY"                              
                            if "jobId must not be empty" in logMessage:
                                logIssue = "PLATFORM"    
                            if javaClass == "com.sun.xml.ws.server.sei.TieHandler.createResponse" and logMessage == "null":
                                logIssue = "PLATFORM"                                                         

                                                
                            tmp = '['+ logTimeStamp +']#['+ logLevel + ']#[' + logIssue + ']#[' + javaClass + ']#[' + javaOperation + ']#[' + gridName + ']#[' + module + ']#[' + workflow + ']#[' +  path + ']#[' +  jobId + ']#[' + logMessage + ']\n'
                            lines.append(tmp)

                        if "WARNING" in logEntryTmp:
                            logIssue = ""
                            logLevel = logEntryTmp[2]
                            logDate = logEntryTmp[0]
                            logTime = logEntryTmp[1]
                            logTimeStamp = logDate + " " + logTime
                            javaClass = logEntryTmp[4]
                            javaOperation = logEntryTmp[3].replace("[","").replace("]","").strip()                    
                            logMessage = str(" ".join(logEntryTmp[5:]).strip(' \n').replace("[", "").replace("]", ""))

                            if "summary=" in logMessage:
                                logMessageTmp = logMessage.split("=")
                                logMessage = str(" ".join(logMessageTmp[1:]))

                            if "very likely to create a memory leak" in logMessage:
                                logIssue = "MEMORY"      
                            if "JDBC driver" in logMessage:
                                logIssue = "PLATFORM"    
                            if "application threads may still be running" in logMessage:
                                logIssue = "PLATFORM"                                                                            
                            if "setting maxIdle" in logMessage:
                                logIssue = "PLATFORM"                                                       

                            tmp = '['+ logTimeStamp +']#['+ logLevel + ']#[' + logIssue + ']#[' + javaClass + ']#[' + javaOperation + ']#[' + gridName + ']#[' + module + ']#[' + workflow + ']#[' +  path + ']#[' +  jobId + ']#[' + logMessage + ']\n'
                            lines.append(tmp)

                line = fp.readline()
    fp.close
    return lines

def readCatalinaLogFile7(path):    
    gridName = bmcg.customerDetails['grid']
    logFile = path
    lines = []
    with open(logFile) as fp:
            line = fp.readline()
            while line:
                module = ""
                workflow = ""                    
                path = ""
                jobId = ""         
                
                if line != "":       
                    logEntryTmp = re.split(' ',line)
                    if bmcg.version.startswith("8"):
                        if "SEVERE" in logEntryTmp:
                            logIssue = ""
                            logLevel = logEntryTmp[2]
                            logDate = logEntryTmp[0]
                            logTime = logEntryTmp[1]
                            logTimeStamp = logDate + " " + logTime
                            javaClass = logEntryTmp[4]
                            javaOperation = logEntryTmp[3].replace("[","").replace("]","").strip()                    
                            logMessage = str(" ".join(logEntryTmp[5:]).strip(' \n').replace("[", "").replace("]", ""))
                            pass

                            if "summary=" in logMessage:
                                logMessageTmp = logMessage.split("=")
                                logMessage = str(" ".join(logMessageTmp[1:]))

                            if "execute-process" in logMessage:
                                logMessageTmp = logMessage.split(",")
                                module = logMessageTmp[5].strip()
                                path = logMessageTmp[6].replace(".","").replace('"',"").strip()     
                                workflow = path.split(":")[-1]
                                if "authorization" in logMessage:
                                    logIssue = "AUTHORIZATION"

                            if "Proc" in logMessage and "not be found" in logMessage:
                                logMessageTmp = logMessage.split('"')
                                pathTmp = logMessageTmp[1].split(":")
                                path = logMessageTmp[1]
                                module = pathTmp[1]
                                workflow = pathTmp[-1]     
                                logIssue = "AVAILABILITY"             

                            if "COMPENSATED" in logMessage:
                                logIssue = "COMPENSATION"    
                            if "Process is CANCELLED." in logMessage:
                                logIssue = "AVAILABILITY"  
                                logLevel = "WARNING"                            
                            if "exception occurred" in logMessage:
                                logIssue = "EXCEPTION"      
                            if "Exception thrown during phase execution" in logMessage:
                                logIssue = "EXCEPTION"      
                            if "caught throwable" in logMessage:
                                logIssue = "EXCEPTION"   
                            if "java.lang.NullPointerException" in logMessage:
                                logIssue = "EXCEPTION"                                                                                     
                            if "Invalid input. No result generated." in logMessage:
                                logIssue = "INVALID"     
                            if "Error in Verifying Security" in logMessage:
                                logIssue = "AUTHORIZATION"    
                            if "probable memory leak" in logMessage:
                                logIssue = "MEMORY"   
                            if "likely to create a memory leak" in logMessage:
                                logIssue = "MEMORY"                              
                            if "jobId must not be empty" in logMessage:
                                logIssue = "PLATFORM"    
                            if javaClass == "com.sun.xml.ws.server.sei.TieHandler.createResponse" and logMessage == "null":
                                logIssue = "PLATFORM"                                                         

                                                
                            tmp = '['+ logTimeStamp +']#['+ logLevel + ']#[' + logIssue + ']#[' + javaClass + ']#[' + javaOperation + ']#[' + gridName + ']#[' + module + ']#[' + workflow + ']#[' +  path + ']#[' +  jobId + ']#[' + logMessage + ']\n'
                            lines.append(tmp)

                        if "WARNING" in logEntryTmp:
                            logIssue = ""
                            logLevel = logEntryTmp[2]
                            logDate = logEntryTmp[0]
                            logTime = logEntryTmp[1]
                            logTimeStamp = logDate + " " + logTime
                            javaClass = logEntryTmp[4]
                            javaOperation = logEntryTmp[3].replace("[","").replace("]","").strip()                    
                            logMessage = str(" ".join(logEntryTmp[5:]).strip(' \n').replace("[", "").replace("]", ""))

                            if "summary=" in logMessage:
                                logMessageTmp = logMessage.split("=")
                                logMessage = str(" ".join(logMessageTmp[1:]))

                            if "very likely to create a memory leak" in logMessage:
                                logIssue = "MEMORY"      
                            if "JDBC driver" in logMessage:
                                logIssue = "PLATFORM"    
                            if "application threads may still be running" in logMessage:
                                logIssue = "PLATFORM"                                                                            
                            if "setting maxIdle" in logMessage:
                                logIssue = "PLATFORM"                                                       

                            tmp = '['+ logTimeStamp +']#['+ logLevel + ']#[' + logIssue + ']#[' + javaClass + ']#[' + javaOperation + ']#[' + gridName + ']#[' + module + ']#[' + workflow + ']#[' +  path + ']#[' +  jobId + ']#[' + logMessage + ']\n'
                            lines.append(tmp)

                line = fp.readline()
    fp.close
    return lines

def writeLogFile(path,lines):
    
    Path(bmcs.getParentFolder(path)).mkdir(parents=True, exist_ok=True) 
    with open(path, 'w') as fp:
            fp.writelines(lines)
    fp.close

def updateProcLogFile(logFile):
    lines = ""
    lines = readProcLogFile8(logFile)
    writeLogFile(logFile,lines)

def updateGridLogFile(logFile):
    gridLines = []
    healthLines = []
    
    fileName = bmcs.getFileName(logFile)
    fileTmp = fileName.split(".")

    parentFolder = bmcs.getParentFolder(logFile)
    filePrefix = "health-grid"
    fileExtension = fileTmp[1]
    fileNameTmp = os.path.join(parentFolder, filePrefix + "." + fileExtension)
    fileName = getNewFilePath(fileNameTmp,fileExtension)
    
    lines = readGridLogFile(logFile)
    for line in lines:
        if line.startswith("[HEALTH_STAT"):
            healthLines.append(line)
        else:
            gridLines.append(line)

    writeLogFile(logFile,gridLines)
    writeLogFile(fileName,healthLines)

def updateHealthLogFile(logFile):
    fileName = bmcs.getFileName(logFile)
    if fileName.startswith("tso-health."):
        lines = readHealthLogFile(logFile)
        writeLogFile(logFile,lines)

def updateStdErrLogFile(logFile):
    lines = readStdErrLogFile(logFile)
    writeLogFile(logFile,lines)

def updateStdOutLogFile(logFile):
    lines = readStdOutLogFile(logFile)
    writeLogFile(logFile,lines)

def updateCatalinaLogFile(logFile):
    lines = ""
    lines = readCatalinaLogFile8(logFile)
    writeLogFile(logFile,lines)

def stageProcLogFile(description,logFiles):
    mpProcs = []
    pbar = progressbar.ProgressBar()
    logFileCount = len(logFiles)
    widgets = [' - ',description,': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
    cnt = 0
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=logFileCount)
    pbar.start()

    for logFile in pbar(logFiles):
        # mpProc = Process(target=updateProcLogFile, args=(logFile,))
        # mpProcs.append(mpProc)
        # mpProc.start()
        updateProcLogFile(logFile)
        pbar.update(cnt+1)
        cnt += 1
    
    for proc in mpProcs:
        proc.join()
        
    pbar.finish()

def stageGridLogFile(description,logFiles):
    mpProcs = []
    pbar = progressbar.ProgressBar()
    logFileCount = len(logFiles)
    widgets = [' - ',description,': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
    cnt = 0
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=logFileCount)
    pbar.start()

    for logFile in pbar(logFiles):
        # mpProc = Process(target=updateGridLogFile, args=(logFile,))
        # mpProcs.append(mpProc)
        # mpProc.start()
        updateGridLogFile(logFile)
        pbar.update(cnt+1)
        cnt += 1

    for proc in mpProcs:
            proc.join()

    pbar.finish()

    return ""  

def stageHealthLogFile(description,logFiles):
    mpProcs = []
    pbar = progressbar.ProgressBar()
    logFileCount = len(logFiles)
    widgets = [' - ',description,': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
    cnt = 0
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=logFileCount)
    pbar.start()

    for logFile in pbar(logFiles):
        # mpProc = Process(target=updateHealthLogFile, args=(logFile,))
        # mpProcs.append(mpProc)
        # mpProc.start()
        updateHealthLogFile(logFile)
        pbar.update(cnt+1)
        cnt += 1

    for proc in mpProcs:
            proc.join()

    pbar.finish()

    return ""  

def stageStdErrLogFile(description,logFiles):
    mpProcs = []
    pbar = progressbar.ProgressBar()
    logFileCount = len(logFiles)
    widgets = [' - ',description,': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
    cnt = 0
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=logFileCount)
    pbar.start()

    for logFile in pbar(logFiles):
        # mpProc = Process(target=updateStdErrLogFile, args=(logFile,))
        # mpProcs.append(mpProc)
        # mpProc.start()
        updateStdErrLogFile(logFile)
        pbar.update(cnt+1)
        cnt += 1

    for proc in mpProcs:
            proc.join()

    pbar.finish()

    return ""  

def stageStdOutLogFile(description,logFiles):
    mpProcs = []
    pbar = progressbar.ProgressBar()
    logFileCount = len(logFiles)
    widgets = [' - ',description,': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
    cnt = 0
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=logFileCount)
    pbar.start()

    for logFile in pbar(logFiles):
        # mpProc = Process(target=updateStdOutLogFile, args=(logFile,))
        # mpProcs.append(mpProc)
        # mpProc.start()
        updateStdOutLogFile(logFile)
        pbar.update(cnt+1)
        cnt += 1

    for proc in mpProcs:
            proc.join()

    pbar.finish()

    return ""  

def stageCatalinaLogFile(description,logFiles):
    mpProcs = []
    pbar = progressbar.ProgressBar()
    logFileCount = len(logFiles)
    widgets = [' - ',description,': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
    cnt = 0
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=logFileCount)
    pbar.start()

    for logFile in pbar(logFiles):
        # mpProc = Process(target=updateCatalinaLogFile, args=(logFile,))
        # mpProcs.append(mpProc)
        # mpProc.start()
        updateCatalinaLogFile(logFile)
        pbar.update(cnt+1)
        cnt += 1

    for proc in mpProcs:
            proc.join()

    pbar.finish()

    return ""  

def conSql():
    driver   = bmcg.db_driver
    server   = bmcg.db_server
    port     = bmcg.db_port
    database = bmcg.db_name
    username = bmcg.db_user
    password = bmcg.db_pwd
    cursor = bmcs.conSql(driver,server,port,database,username,password)

    return cursor

def rptGridLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,thread,status,adapter,jobId,summary,info,log):
    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,SFDC,CUSTOMER,GRID,PEER,THREAD_TYPE,STATUS,ADAPTER,PROCESS_ID,SUMMARY,INFO
    table = "LOG_GRID"
    tsql = "INSERT INTO " + table + " (REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,THREAD_TYPE,STATUS,ADAPTER,PROCESS_ID,SUMMARY,INFO,LOG_FILE_NAME) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    values = rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,thread,status,adapter,jobId,summary,info,log
    status = bmcs.inserSql(cursor,tsql,values)
    return status

def rptHealthLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,category,description,status,metricInstance,metricName,metricVal,log):
    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,CATEGORY,DESCRIPTION,STATUS,METRIC_INSTANCE,METRIC_NAME,METRIC_VALUE
    #(              ?,           ?,          ?,          ?,            ?,   ?,       ?,   ?,   ?,       ?,           ?,    ?,              ?,          ?,            ?)
    table = "LOG_HEALTH"
    tsql = "INSERT INTO " + table + " (REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,CATEGORY,DESCRIPTION,STATUS,METRIC_INSTANCE,METRIC_NAME,METRIC_VALUE,LOG_FILE_NAME) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    values = rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,category,description,status,metricInstance,metricName,metricVal,log
    #       (           ?,       ?,      ?,      ?,        ?,   ?,       ?,   ?,   ?,       ?,          ?,     ?,             ?,         ?,        ?)
    status = bmcs.inserSql(cursor,tsql,values)
    return status

def rptProcessLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,rootJobId,module,workflow,jobId,processTermState,processTimeStart,processTimeEnd,processTimeDuration,jobPath,log):
    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,ROOT_JOB,MODULE,WORKFLOW,PROCESS_ID,PROCESS_STATUS,PROCESS_START,PROCESS_END,PROCESS_DURATION,PROCESS_PATH
    #(             1?,          2?,         3?,         4?,           5?,  6?,      7?,  8?,  9?,     10?,   11?,     12?,       13?,           14?,          15?,         16?,            17?,         18?)
    #(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    table = "LOG_PROCESS"
    tsql = "INSERT INTO " + table + " (REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,ROOT_JOB,MODULE,WORKFLOW,PROCESS_ID,PROCESS_STATUS,PROCESS_START,PROCESS_END,PROCESS_DURATION,PROCESS_PATH,LOG_FILE_NAME) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    values = rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,rootJobId,module,workflow,jobId,processTermState,processTimeStart,processTimeEnd,processTimeDuration,jobPath,log
    status = bmcs.inserSql(cursor,tsql,values)
    return status

def rptProcessDetailLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,rootJobId,module,workflow,jobId,processTermState,processTimeStart,processTimeEnd,processTimeDuration,jobPath,log):
    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,ROOT_JOB,MODULE,WORKFLOW,PROCESS_ID,PROCESS_STATUS,PROCESS_START,PROCESS_END,PROCESS_DURATION,PROCESS_PATH
    #(             1?,          2?,         3?,         4?,           5?,  6?,      7?,  8?,  9?,     10?,   11?,     12?,       13?,           14?,          15?,         16?,            17?,         18?)
    #(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    table = "LOG_PROCESS_DETAIL"
    tsql = "INSERT INTO " + table + " (REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,ROOT_JOB,MODULE,WORKFLOW,PROCESS_ID,PROCESS_STATUS,PROCESS_START,PROCESS_END,PROCESS_DURATION,PROCESS_PATH,LOG_FILE_NAME) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    values = rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,rootJobId,module,workflow,jobId,processTermState,processTimeStart,processTimeEnd,processTimeDuration,jobPath,log
    status = bmcs.inserSql(cursor,tsql,values)
    return status

def rptPlatformLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,module,workflow,rootJobId,jobPath,logLevel,logType,javaClass,javaOperation,summary,log):
    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,MODULE,WORKFLOW,PROCESS_ID,PROCESS_PATH,LEVEL,TYPE,JAVA_CLASS,JAVA_OPERATION,SUMMARY
    #(             1?,          2?,         3?,         4?,           5?,  6?,      7?,  8?,  9?,   10?,     11?,       12?,         13?,  14?, 15?,       16?,           17?,    18?)
    #(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    #(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    table = "LOG_PLATFORM"
    tsql = "INSERT INTO " + table + " (REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,REPORT_WINDOW,SFDC,CUSTOMER,GRID,PEER,MODULE,WORKFLOW,PROCESS_ID,PROCESS_PATH,LEVEL,TYPE,JAVA_CLASS,JAVA_OPERATION,SUMMARY,LOG_FILE_NAME) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    values = rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,module,workflow,rootJobId,jobPath,logLevel,logType,javaClass,javaOperation,summary,log
    status = bmcs.inserSql(cursor,tsql,values)
    return status    

def analyseGridLogLine(cursor,line,customer,sfdc,grid,log):
    timeFormat = '%d %b %Y %H:%M:%S,%f'
    peer = "N/A"
    status = "N/A"
    adapter = "N/A"
    thread = "N/A"
    jobId = "N/A"
    summary = "N/A"
    logKey = ""
    logVal = ""

    logEntries = re.split('#',line)
    description =  logEntries[-2].replace("[", "").replace("]", "")

    try: 
        rptTimeStamp =  re.split(' ',logEntries[0].replace("[", "").replace("]", ""))

        if len(rptTimeStamp) == 4:
            if rptTimeStamp[2] == "2020": 
                timeVal = logEntries[0].replace("[", "").replace("]", "")
                rptDate = rptTimeStamp[0] + '-' +  rptTimeStamp[1] + '-' +  rptTimeStamp[2]
                rptTime = rptTimeStamp[3].replace(",", ".")
                rptWindow = getReportTime(rptTime)
                rptEpoch = bmcs.getEpoch(timeVal,timeFormat)
                rptTimeStamp = rptDate + " " + rptTime  
                tmpStatus = re.split(' ',logEntries[2].replace("[", "").replace("]", ""))

                if "Task" in tmpStatus[0]:
                    tempLine = re.split(' ',description)
                    status =  tempLine[0]
                    adapter = tempLine[1]
                    summary = " ".join(tempLine[2:]).strip()
                else:
                    status = tmpStatus[0]
                    summary = description

                if "Messagesummary" in summary:
                    summary = summary.replace("Messagesummary", "Message Summary")

                if "JmsPeerId urn:jxta" in summary:
                    info = "JMS/JMX"
                elif "ComponentUnavailableException" in summary:
                    info = "Component"
                elif "thrown exception" in summary:
                    info = "Exception "    
                elif "javax.jms.JMSException" in summary:
                    info = "JMS/JMX" 
                elif "FailoverTransport" in summary:
                    info = "Communication"  
                elif "JmsSender" in summary:
                    info = "JMS/JMX" 
                elif "JDBCExceptionReporter" in summary:
                    info = "JDBC"
                elif "HANode" in summary:
                    info = "HA Node"    
                elif "While in the slave state, the component" in summary:
                    info = "Component"                         
                elif "XSLTEvaluatable" in summary:
                    info = "XSLT"   
                elif "MessageFactory" in summary:
                    info = "Message Factory"   
                elif "ServerManager" in summary:
                    info = "Server Manager"                             
                elif "BaseFilter" in summary:
                    info = "Base Filter" 
                elif "java.sql.SQLIntegrityConstraintViolationException" in summary:
                    info = "JDBC"    
                elif "Communication exception. Error:‘Unauthorized’" in summary:
                    info = "Communication"              
                elif "Error occurred making request" in summary:
                    info = "Communication" 
                elif "Error occured performing query" in summary:
                    info = "Communication"              
                elif "Error closing invalid terminal connection" in summary:
                    info = "Communication" 
                elif "Error occurred processing request data" in summary:
                    info = "Error occurred processing request data"              
                elif "Java Rpc failed" in summary:
                    info = "Communication" 
                elif "Java Rpc failed" in summary:
                    info = "Communication"        
                elif "IO exception" in summary:
                    info = "Communication"   
                elif "IO error" in summary:
                    info = "Communication"                                   
                elif "AMP - Activity Processor - Parallel Adapter Invocation Worker" in summary:
                    info = "Adapter Invocation Worker"
                elif "AMP - Submit Rules Jobs Handler" in summary:
                    info = "AMP - Submit Rules Jobs Handler"                          
                elif "SchedulerJdbcPersistor" in summary:
                    info = "JDBC"          
                elif "SSL security Exception" in summary:
                    info = "Communication" 
                elif "Could not accept connection from tcp://" in summary:
                    info = "Communication" 
                elif "connect string: jdbc:sqlserver://" in summary:
                    info = "JDBC" 
                else:
                    info = "Not Assigned"        


                for logEntry in logEntries:
                    logEntry = logEntry.replace("[", "").replace("]", "")
                    if logEntry != "":
                        if "=" in logEntry:
                            logKV = re.split('=',logEntry)
                            logKey = logKV[0]
                            logVal = logKV[1]
                        else:
                            logKey = ""
                            logVal = ""

                        if "Thread" in logKey: 
                            thread = logVal               
                            tempVal =  re.split('-',thread)
                            if thread.startswith("ActiveMQ Transport"):
                                thread = "ActiveMQ Transport"
                            elif thread.startswith("ActiveMQ BrokerService"):
                                thread = "ActiveMQ Broker Service"                                  
                            elif thread.startswith("ActiveMQ Session"):
                                thread = "ActiveMQ Session"                                    
                            elif "Grid Framework" in thread:
                                thread = "AMP - Grid Framework" 
                            elif "Perform Action Executor" in thread:
                                thread = "AMP - Perform Action Executor"
                            elif "Submit Rules Jobs Handler" in thread:
                                thread = "AMP - Submit Rules Jobs Handler"  
                            elif thread.startswith("AMP"):                        
                                thread = "-".join(tempVal[0:3]).strip()                    
                            elif thread.startswith("http"):
                                thread = "HTTP - NIO" # + str(tempVal[4]).strip()
                            elif thread.startswith("Timer"):
                                thread = "TIMER" 
                            elif thread.startswith("Thread-"):
                                thread = "Thread"     
                            elif thread.startswith("THREAD -  Thread"): 
                                thread = "Thread"  
                            elif thread.startswith("THREAD - "):
                                thread = "Thread"                                     
                            elif thread.startswith("pool-"):
                                thread = "Pool Thread"       
                            elif thread.startswith("RemedyContextMonitorThread"):
                                thread = "Remedy Context Monitor Thread"       
                            elif ":" in thread:
                                tempVal =  re.split(':',logVal)
                                thread = tempVal[0].upper() + " - " + tempVal[-1]
                            else:
                                pass

                        if "PeerName" in logKey:
                            peer = logVal
                        if "AdapterName" in logKey:
                            adapter = logVal
                        if "JobID" in logKey:
                            jobId = logVal
                # REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,SFDC,CUSTOMER,GRID,PEER,THREAD_TYPE,STATUS,ADAPTER,JOBID,SUMMARY,INFO
                rptGridLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,thread,status,adapter,jobId,summary,info,log)
        else:
            pass

    except Exception as ex:
        print(f" - Exception Line={line}")
        print(f" - Exception={ex}")
        return str(ex)
   
def analyseHealthLogLine(cursor,line,customer,sfdc,grid,log):
    timeFormat = '%Y-%m-%d %H:%M:%S'
    #2019-02-21 01:21:39
    peer = ""
    category = ""
    description = ""
    status = ""
    metricInstance = ""

    logEntries = re.split('#',line)
    rptTimeStamp =  re.split(' ',logEntries[1].replace("[", "").replace("]", ""))
    timeVal = logEntries[1].replace("[", "").replace("]", "")
    rptDate = rptTimeStamp[0]
    rptTime = rptTimeStamp[1]
    rptWindow = getReportTime(rptTime)
    rptEpoch = bmcs.getEpoch(timeVal,timeFormat)
    rptTimeStamp = timeVal.replace(",", ".")
    
    logTemp1 = re.split(':',logEntries[2].replace("[", "").replace("]", ""))
    logTemp2 = logEntries[3].replace("[", "").replace("]", "")
    logTemp3 = logEntries[4].replace("[", "").replace("]", "")
    catTemp = logTemp1[0]

    metricName = logTemp2
    metricVal = logTemp3

    if catTemp == "A":
        category = "Adapter"
        peer = logTemp1[1]
        metricInstance = logTemp1[2]
        if metricName.startswith("COUNT"):
            status = ""
        else:
            status = metricVal
            metricName = ""
            metricVal = ""                
    elif catTemp == "C":
        category = "Component"
        peer = logTemp1[1]
        metricInstance = logTemp1[2]        
        status = metricVal
        metricName = ""
        metricVal = ""          
    elif catTemp == "P":
        category = "Peer"
        peer = logTemp1[1]
        metricInstance = logTemp1[1]                                                                       
        if metricName.startswith("COUNT"):
            pass
        elif metricName.startswith("NUMBER"):
            pass
        elif metricName.startswith("MEMORY"):
            pass
        elif metricName.startswith("CPU_UTILIZATION"):
            pass
        elif metricName.startswith("FREE_MEMORY"):
            pass    
        elif metricName.startswith("HOST_FREE_RAM"):
            pass 
        elif metricName.startswith("UPTIME"):
            pass                                               
        else:
            description = metricName + "=" + metricVal
            metricName = ""
            metricVal = "" 
    elif catTemp == "G":
        category = "Grid"
        metricInstance = logTemp1[1]
        if metricName.startswith("COUNT"):
            pass
        elif metricName.startswith("NUMBER"):
            pass
        elif metricName.startswith("UPTIME"):
            pass            
        else:
            description = metricName + "=" + metricVal
            metricName = ""
            metricVal = "" 
    else:
        pass                


    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,SFDC,CUSTOMER,GRID,PEER,CATEGORY,DESCRIPTION,STATUS,METRIC_INSTANCE,METRIC_NAME,METRIC_VALUE
    rptHealthLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,category,description,status,metricInstance,metricName,metricVal,log)

def analyseProcessLogLine(cursor,line,peer,customer,sfdc,grid,log): 
    timeFormat = '%d %b %Y %H:%M:%S,%f'
    #21 Feb 2019 08:15:19,145
    processTermState = ""
    processTimeStart = ""
    processTimeEnd = ""
    processTimeDuration = ""
    module = ""
    workflow = ""
    jobChildWorkflows = []

    logEntries = re.split('#',line)
    # Time and Date
    rptTimeStamp =  re.split(' ',logEntries[0].replace("[", "").replace("]", ""))
    timeVal = logEntries[0].replace("[", "").replace("]", "")
    rptDate = rptTimeStamp[0] + " " + rptTimeStamp[1] + " " + rptTimeStamp[2]
    rptTime = rptTimeStamp[3].replace(",", ".")
    rptWindow = getReportTime(rptTime)
    rptEpoch = bmcs.getEpoch(timeVal,timeFormat)
    rptTimeStamp = timeVal.replace(",", ".")

    for logEntry in logEntries:
        logEntryTmp = logEntry.replace("[", "").replace("]", "")
        if "=" in logEntryTmp:
            logEntryKeyVal = re.split('=',logEntryTmp)
            logEntryKey = logEntryKeyVal[0]
            logEntryVal = logEntryKeyVal[1]
            
            if logEntryKey.startswith("Current Time"):
                # Thu Jun 27 01:06:17 CDT 2019
                pass

            if logEntryKey.startswith("Process Name"):
                # :AEG-SA-Utilities:Construct Status
                logTemp = re.split(':',logEntryVal)
                module = logTemp[1]
                workflow = logTemp[-1]


            if logEntryKey.startswith("Root Job Id"):
                # db76d26516e94b02:5de9bee6:16b8fafe70b:-7ffb1-1561615577835
                rootJobId = logEntryVal
                jobId = rootJobId


            if logEntryKey.startswith("Job Id"):
                # db76d26516e94b02:5de9bee6:16b8fafe70b:-7ffb1-1561615577835/:AEG_Monitors_And_Schedules:CLC Monitor:start:call-process1
                jobPath = logEntryVal
                if "/" in jobPath:                    
                    jobId = re.split('/',jobPath)[0]
                    jobDetailsTemp = re.split('/',jobPath)
                    jobDetails = jobDetailsTemp[1:]
                    for jobDetail in jobDetails:
                        jobTmp = jobDetail
                        jobChildWorkflows.append(jobTmp)
               
                    rootJob = "false"
                else:
                    rootJob = "true"

                jobChildWorkflows = str("/".join(jobChildWorkflows))

            if logEntryKey.startswith("Parent Job Id"):
                # db76d26516e94b02:5de9bee6:16b8fafe70b:-7ffb1-1561615577835
                pass 

            if logEntryKey.startswith("ProcessTermination"):
                # The process terminated in the completed state. The process started at 27 Jun 2019 01:06:17,847, terminated at 27 Jun 2019 01:06:17,861, and the execution took 14 milliseconds.
                processTemp = re.split('state.',logEntryVal)[0]
                processTermState = re.split('in the ',processTemp)[1]
                # Process Start
                processTemp = re.split('started at.',logEntryVal)[1]
                processTimeStart = re.split(', terminated at',processTemp)[0].replace(",", ".")
                
                # Process End
                processTemp = re.split('terminated at.',logEntryVal)[1]
                processTimeEnd = re.split(', and the',processTemp)[0].replace(",", ".")

                # Process Duration
                processTemp = re.split('execution took ',logEntryVal)[1]
                processTimeDuration = re.split(' ',processTemp)[0]
                if "," in processTimeDuration:
                    processTimeDuration = processTimeDuration.replace(",", "")                 


    if rootJob == "true":
        if bmcg.advanced:
            try:
                print("")
                bmcs.logStatus(" - Parameter grid",grid) 
                bmcs.logStatus(" - Parameter peer",peer) 
                bmcs.logStatus(" - Parameter rootJob",rootJob) 
                bmcs.logStatus(" - Parameter rootJobId",rootJobId) 
                bmcs.logStatus(" - Parameter jobId",jobId) 
                bmcs.logStatus(" - Parameter module",module) 
                bmcs.logStatus(" - Parameter workflow",workflow) 
                bmcs.logStatus(" - Parameter jobPath",jobPath) 
                bmcs.logStatus(" - Parameter processTermState",processTermState) 
                bmcs.logStatus(" - Parameter processTimeStart",processTimeStart) 
                bmcs.logStatus(" - Parameter processTimeEnd",processTimeEnd) 
                bmcs.logStatus(" - Parameter processTimeDuration",processTimeDuration)  
            except Exception as ex:
                 print(f"{ex}")
                 
        rptProcessLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,rootJobId,module,workflow,jobId,processTermState,processTimeStart,processTimeEnd,processTimeDuration,jobPath,log)
    else:
        if bmcg.advanced:
            try:
                print("")
                bmcs.logStatus(" - Parameter grid",grid) 
                bmcs.logStatus(" - Parameter peer",peer) 
                bmcs.logStatus(" - Parameter rootJob",rootJob) 
                bmcs.logStatus(" - Parameter rootJobId",rootJobId) 
                bmcs.logStatus(" - Parameter jobId",jobId) 
                bmcs.logStatus(" - Parameter module",module) 
                bmcs.logStatus(" - Parameter workflow",workflow) 
                bmcs.logStatus(" - Parameter jobChildWorkflows",jobChildWorkflows) 
                bmcs.logStatus(" - Parameter processTermState",processTermState) 
                bmcs.logStatus(" - Parameter processTimeStart",processTimeStart) 
                bmcs.logStatus(" - Parameter processTimeEnd",processTimeEnd) 
                bmcs.logStatus(" - Parameter processTimeDuration",processTimeDuration)  
            except Exception as ex:
                 print(f"{ex}")                          

        jobPath = jobChildWorkflows
        rptProcessDetailLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,rootJobId,module,workflow,jobId,processTermState,processTimeStart,processTimeEnd,processTimeDuration,jobPath,log)

    pass

def analyseStdErrLogLine(cursor,line,peer,customer,sfdc,grid,log):
    timeFormat = '%d %b %Y %H:%M:%S,%f'
    timeFormat = '%b %d, %Y %I:%M:%S %p'
    # 21 Feb 2019 08:15:19,145
    # Nov 15, 2017 4:16:20 PM
    #logTimeStamp logLevel logIssue javaClass javaOperation gridName module workflow path jobId logMessage
    logEntry = line.replace("[", "").replace("]", "")
    logEntries = re.split('#',logEntry)

    logTimeStamp = logEntries[0]
    logLevel = logEntries[1]
    logType = logEntries[2] 
    javaClass = logEntries[3] 
    javaOperation = logEntries[4] 
    gridName = logEntries[5] 
    module = logEntries[6] 
    workflow = logEntries[7] 
    jobPath = logEntries[8] 
    rootJobId = logEntries[9] 
    summary = logEntries[10].strip(' \n')

    rptTimeStamp =  re.split(' ',logTimeStamp)
    timeVal = logEntries[0].replace("[", "").replace("]", "")
    rptDate = rptTimeStamp[0] + " " + rptTimeStamp[1].replace(",", "") + " " + rptTimeStamp[2]
    rptTime = " ".join(rptTimeStamp[3:])
    rptWindow = getReportTime(rptTime) + " " + rptTimeStamp[4]
    rptEpoch = bmcs.getEpoch(logTimeStamp,timeFormat)
    rptTimeStamp = timeVal.replace(",", "")

    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,SFDC,CUSTOMER,GRID,PEER,MODULE,WORKFLOW,PROCESS_ID,PROCESS_PATH,LEVEL,TYPE,JAVA_CLASS,JAVA_OPERATION,SUMMARY,FILE
    rptPlatformLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,module,workflow,rootJobId,jobPath,logLevel,logType,javaClass,javaOperation,summary,log)

def analyseCatalinaLogLine(cursor,line,peer,customer,sfdc,grid,log):
    timeFormat = '%d %b %Y %H:%M:%S,%f'
    timeFormat = '%d-%b-%Y %H:%M:%S.%f'
    # 21 Feb 2019 08:15:19,145
    # 01-Dec-2017 14:56:15.166
    #logTimeStamp logLevel logIssue javaClass javaOperation gridName module workflow path jobId logMessage
    logEntry = line.replace("[", "").replace("]", "")
    logEntries = re.split('#',logEntry)

    logTimeStamp = logEntries[0]
    logLevel = logEntries[1]
    logType = logEntries[2] 
    javaClass = logEntries[3] 
    javaOperation = logEntries[4] 
    gridName = logEntries[5] 
    module = logEntries[6] 
    workflow = logEntries[7] 
    jobPath = logEntries[8] 
    rootJobId = logEntries[9] 
    summary = logEntries[10].strip(' \n')

    rptTimeStamp =  re.split(' ',logTimeStamp)
    timeVal = logEntries[0].replace("[", "").replace("]", "")
    rptDate = rptTimeStamp[0]
    rptTime = rptTimeStamp[1]
    rptWindow = getReportTime(rptTime) 
    rptEpoch = bmcs.getEpoch(logTimeStamp,timeFormat)
    rptTimeStamp = timeVal.replace(",", "")

    #REPORT_TIMESTAMP,REPORT_EPOCH,REPORT_DATE,REPORT_TIME,SFDC,CUSTOMER,GRID,PEER,MODULE,WORKFLOW,PROCESS_ID,PROCESS_PATH,LEVEL,TYPE,JAVA_CLASS,JAVA_OPERATION,SUMMARY,FILE
    rptPlatformLog(cursor,rptTimeStamp,rptEpoch,rptDate,rptTime,rptWindow,sfdc,customer,grid,peer,module,workflow,rootJobId,jobPath,logLevel,logType,javaClass,javaOperation,summary,log)

def analyseGridLog(logListItem):
    # logListItem = logFile + "#" + customer + "#" + sfdc + "#" + grid
    logListTmp = re.split('#',logListItem)
    log = logListTmp[0]
    customer = logListTmp[1]
    sfdc = logListTmp[2]
    grid = logListTmp[3]

    try:
        if os.path.exists(log) and os.path.getsize(log) > 0:
            print("+", end="", flush=True)
            cursor = conSql()
            lines = readLogFile(log) 
            for line in lines:
                analyseGridLogLine(cursor,line,customer,sfdc,grid,log)
            cursor.close()
            print(".", end="", flush=True)

    except IOError as e:
            return str(e)
    except:
            return sys.exc_info()    

def analyseHealthLog(logListItem):
    # logListItem = logFile + "#" + customer + "#" + sfdc + "#" + grid
    logListTmp = re.split('#',logListItem)
    log = logListTmp[0]
    customer = logListTmp[1]
    sfdc = logListTmp[2]
    grid = logListTmp[3]    
    try:
        if os.path.exists(log) and os.path.getsize(log) > 0:
            print("+", end="", flush=True)
            cursor = conSql()
            lines = readLogFile(log) 
            for line in lines:
                analyseHealthLogLine(cursor,line,customer,sfdc,grid,log)
            cursor.close()
            print(".", end="", flush=True)
    except IOError as e:
            return str(e)
    except:
            return sys.exc_info()

def analyseProcessLog(logListItem):
    # logListItem = logFile + "#" + customer + "#" + sfdc + "#" + grid
    logListTmp = re.split('#',logListItem)
    log = logListTmp[0]
    customer = logListTmp[1]
    sfdc = logListTmp[2]
    grid = logListTmp[3]    
    try:
        if os.path.exists(log) and os.path.getsize(log) > 0:
            peer = bmcs.getParentBaseFolder(log)
            print("+", end="", flush=True)
            cursor = conSql()
            lines = readLogFile(log) 
            for line in lines:
                analyseProcessLogLine(cursor,line,peer,customer,sfdc,grid,log)
            cursor.close()
            print(".", end="", flush=True)
    except IOError as e:
            return str(e)
    except:
            return sys.exc_info()

def analyseStdErrLog(logListItem):
    # logListItem = logFile + "#" + customer + "#" + sfdc + "#" + grid
    logListTmp = re.split('#',logListItem)
    log = logListTmp[0]
    customer = logListTmp[1]
    sfdc = logListTmp[2]
    grid = logListTmp[3]    
    try:
        if os.path.exists(log) and os.path.getsize(log) > 0:
            peer = bmcs.getParentBaseFolder(log)
            print("+", end="", flush=True)
            cursor = conSql()
            lines = readLogFile(log) 
            for line in lines:
                analyseStdErrLogLine(cursor,line,peer,customer,sfdc,grid,log)
            cursor.close()
            print(".", end="", flush=True)
    except IOError as e:
            return str(e)
    except:
            return sys.exc_info()

def analyseCatalinaLog(logListItem):
    # logListItem = logFile + "#" + customer + "#" + sfdc + "#" + grid
    logListTmp = re.split('#',logListItem)
    log = logListTmp[0]
    customer = logListTmp[1]
    sfdc = logListTmp[2]
    grid = logListTmp[3]       
    try:
        if os.path.exists(log) and os.path.getsize(log) > 0:
            peer = bmcs.getParentBaseFolder(log)
            print("+", end="", flush=True)
            cursor = conSql()
            lines = readLogFile(log) 
            for line in lines:
                analyseCatalinaLogLine(cursor,line,peer,customer,sfdc,grid,log)
            cursor.close()
            print(".", end="", flush=True)
    except IOError as e:
            return str(e)
    except:
            return sys.exc_info()

def analyseGridLogWithpBar(logList):
    cursor = conSql()
    for logListItem in logList:
        # logItem = logFile + "#" + customer + "#" + sfdc + "#" + grid
        logListTmp = re.split('#',logListItem)
        log = logListTmp[0]
        customer = logListTmp[1]
        sfdc = logListTmp[2]
        grid = logListTmp[3]    
    
        lines = readLogFile(log) 
        bmcs.logStatus(" + Log File",log)
        pbar = progressbar.ProgressBar()
        logLinesCount = len(lines)
        widgets = [' - Analyze ',"Lines",': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
        cnt = 0
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=logLinesCount)
        pbar.start()    
        for line in pbar(lines):
            analyseGridLogLine(cursor,line,customer,sfdc,grid,log)
            pbar.update(cnt+1)
            cnt += 1   
        pbar.finish()            
    cursor.close()    

def analyseHealthLogWithpBar(logList):
    cursor = conSql()
    for logListItem in logList:    
        # logList = logFile + "#" + customer + "#" + sfdc + "#" + grid
        logListTmp = re.split('#',logListItem)
        log = logListTmp[0]
        customer = logListTmp[1]
        sfdc = logListTmp[2]
        grid = logListTmp[3]      
        lines = readLogFile(log) 
        bmcs.logStatus(" + Log File",log)
        pbar = progressbar.ProgressBar()
        logLinesCount = len(lines)
        widgets = [' - Analyze ',"Lines",': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
        cnt = 0
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=logLinesCount)
        pbar.start()    
        for line in pbar(lines):
            analyseHealthLogLine(cursor,line,customer,sfdc,grid,log)
            pbar.update(cnt+1)
            cnt += 1   
        pbar.finish()            
    cursor.close()  

def analyseProcessLogWithpBar(logList):
    cursor = conSql()
    for logListItem in logList:     
        # logList = logFile + "#" + customer + "#" + sfdc + "#" + grid
        logListTmp = re.split('#',logListItem)
        log = logListTmp[0]
        customer = logListTmp[1]
        sfdc = logListTmp[2]
        grid = logListTmp[3]     
        bmcs.logStatus(" + Log File",log)
        peer = bmcs.getParentBaseFolder(log)
        lines = readLogFile(log)            
        pbar = progressbar.ProgressBar()
        logLinesCount = len(lines)
        widgets = [' - Analyze ',"Lines",': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
        cnt = 0
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=logLinesCount)
        pbar.start()    
        for line in pbar(lines):
            analyseProcessLogLine(cursor,line,peer,customer,sfdc,grid,log)
            pbar.update(cnt+1)
            cnt += 1   
        pbar.finish()            
    cursor.close()  

def analyzeStdErrLogsWithpBar(logList):
    cursor = conSql()
    for logListItem in logList:      
        # logList = logFile + "#" + customer + "#" + sfdc + "#" + grid
        logListTmp = re.split('#',logListItem)
        log = logListTmp[0]
        customer = logListTmp[1]
        sfdc = logListTmp[2]
        grid = logListTmp[3]         
        peer = bmcs.getParentBaseFolder(log)
        lines = readLogFile(log) 
        bmcs.logStatus(" + Log File",log)
        pbar = progressbar.ProgressBar()
        logLinesCount = len(lines)
        widgets = [' - Analyze ',"Lines",': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
        cnt = 0
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=logLinesCount)
        pbar.start()    
        for line in pbar(lines):
            analyseStdErrLogLine(cursor,line,peer,customer,sfdc,grid,log)
            pbar.update(cnt+1)
            cnt += 1   
        pbar.finish()            
    cursor.close()     

def analyzeCatalinaLogsWithpBar(logList):
    cursor = conSql()
    for logListItem in logList:    
        # logList = logFile + "#" + customer + "#" + sfdc + "#" + grid
        logListTmp = re.split('#',logListItem)
        log = logListTmp[0]
        customer = logListTmp[1]
        sfdc = logListTmp[2]
        grid = logListTmp[3]            
        peer = bmcs.getParentBaseFolder(log)
        lines = readLogFile(log) 
        bmcs.logStatus(" + Log File",log)
        pbar = progressbar.ProgressBar()
        logLinesCount = len(lines)
        widgets = [' - Analyze ',"Lines",': ', progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
        cnt = 0
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=logLinesCount)
        pbar.start()    
        for line in pbar(lines):
            analyseCatalinaLogLine(cursor,line,peer,customer,sfdc,grid,log)
            pbar.update(cnt+1)
            cnt += 1   
        pbar.finish()            
    cursor.close()

def analyseGridLogs():
    logList = []
    pattern = "tso-grid"
    grid = bmcg.customerDetails['grid']
    folder = bmcg.stagingFolder
    logFiles = getStagingLogFiles(folder,pattern)
    logCount = len(logFiles)
    mpSupport = bmcg.customerDetails['mp']
    customer = bmcg.customerDetails['customer']
    sfdc = bmcg.customerDetails['id']
    grid = bmcg.customerDetails['grid']

    for logFile in logFiles:
        logEntry = logFile + "#" + customer + "#" + sfdc + "#" + grid + "#" 
        logList.append(logEntry)
    
    if mpSupport == "true":
        mpCpu = cpu_count() 
        mpPoolMultiplier = int(bmcg.mpPoolMultiplier)
        mpPoolCount = int(mpCpu * mpPoolMultiplier)
        mpPool = Pool(processes=mpPoolCount)        
        procStart = time.time()
        if bmcg.verbose:
            bmcs.logStatus(" - TSO Grid",grid)
            bmcs.logStatus(" - TSO Log Type","Grid")
            bmcs.logStatus(" - Analyzing Log Files",logCount)
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Multi Processes Multiplier", bmcg.mpPoolMultiplier)
            bmcs.logStatus(" - Multi Processor Count",mpCpu)
            bmcs.logStatus(" - Multi Processes Pool",mpPoolCount)

        mpPool.map(analyseGridLog,logList)
        mpPool.close()
        mpPool.join()

        procEnd = time.time()
        procDuration = bmcs.timer(procStart,procEnd)      

        if bmcg.verbose:
            print("")
            bmcs.logStatus(" - Analyzing Log Files Start",procStart)
            bmcs.logStatus(" - Analyzing Log Files End  ",procEnd) 
            bmcs.logStatus(" - Analyzing Log Files Duration",procDuration) 
    else:
        logFileCount = len(logFiles)
        if bmcg.verbose:
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Total Log Files",logFileCount)

        analyseGridLogWithpBar(logList)
   
def analyseHealthLogs():
    logList = []
    pattern = "tso-health"
    customer = bmcg.customerDetails['customer']
    sfdc = bmcg.customerDetails['id']    
    grid = bmcg.customerDetails['grid']
    folder = getStagingGridPath(grid)
    logFiles = getStagingLogFiles(folder,pattern)
    logCount = len(logFiles)
    mpSupport = bmcg.customerDetails['mp']

    for logFile in logFiles:
        logEntry = logFile + "#" + customer + "#" + sfdc + "#" + grid + "#" 
        logList.append(logEntry)    
    
    if mpSupport == "true":
        mpCpu = cpu_count() 
        mpPoolMultiplier = int(bmcg.mpPoolMultiplier)
        mpPoolCount = int(mpCpu * mpPoolMultiplier)
        mpPool = Pool(processes=mpPoolCount) 
        procStart = time.time()
        if bmcg.verbose:
            bmcs.logStatus(" - TSO Grid",grid)
            bmcs.logStatus(" - TSO Log Type","Health")
            bmcs.logStatus(" - Analyzing Log Files",logCount)
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Multi Processes Multiplier", bmcg.mpPoolMultiplier)
            bmcs.logStatus(" - Multi Processor Count",mpCpu)
            bmcs.logStatus(" - Multi Processes Pool",mpPoolCount)
        mpPool.map(analyseHealthLog,logList)
        mpPool.close()
        mpPool.join()            
        procEnd = time.time()
        procDuration = bmcs.timer(procStart,procEnd)    
        print("")   
        if bmcg.verbose:
            bmcs.logStatus(" - Analyzing Log Files Start",procStart)
            bmcs.logStatus(" - Analyzing Log Files End  ",procEnd) 
            bmcs.logStatus(" - Analyzing Log Files Duration",procDuration) 
    else:
        logFileCount = len(logFiles)
        if bmcg.verbose:
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Total Log Files",logFileCount)
        
        analyseHealthLogWithpBar(logList)

def analyzeProcessLogs():
    logList = []
    pattern = "tso-processes"
    customer = bmcg.customerDetails['customer']
    sfdc = bmcg.customerDetails['id']    
    grid = bmcg.customerDetails['grid']

    folder = getStagingGridPath(grid)
    logFiles = getStagingLogFiles(folder,pattern)
    logCount = len(logFiles)
    mpSupport = bmcg.customerDetails['mp']


    for logFile in logFiles:
        logEntry = logFile + "#" + customer + "#" + sfdc + "#" + grid + "#" 
        logList.append(logEntry) 

    if mpSupport == "true":
        mpCpu = cpu_count() 
        mpPoolMultiplier = int(bmcg.mpPoolMultiplier)
        mpPoolCount = int(mpCpu * mpPoolMultiplier)
        mpPool = Pool(processes=mpPoolCount)
        procStart = time.time()
        if bmcg.verbose:
            bmcs.logStatus(" - TSO Grid",grid)
            bmcs.logStatus(" - TSO Log Type","Process")
            bmcs.logStatus(" - Analyzing Log Files",logCount)
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Multi Processes Multiplier", bmcg.mpPoolMultiplier)
            bmcs.logStatus(" - Multi Processor Count",mpCpu)
            bmcs.logStatus(" - Multi Processes Pool",mpPoolCount)
        mpPool.map(analyseProcessLog,logList)
        mpPool.close()
        mpPool.join() 
        procEnd = time.time()
        procDuration = bmcs.timer(procStart,procEnd)      
        print("") 
        if bmcg.verbose:
            bmcs.logStatus(" - Analyzing Log Files Start",procStart)
            bmcs.logStatus(" - Analyzing Log Files End  ",procEnd) 
            bmcs.logStatus(" - Analyzing Log Files Duration",procDuration) 
    else:
        logFileCount = len(logFiles)
        if bmcg.verbose:
            bmcs.logStatus(" - TSO Grid",grid)
            bmcs.logStatus(" - TSO Log Type","Process")
            bmcs.logStatus(" - Analyzing Log Files",logCount)            
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Total Log Files",logFileCount)
        
        analyseProcessLogWithpBar(logList)       

def analyzeStdErrLogs():
    logList = []
    pattern = "tso-stderr"
    customer = bmcg.customerDetails['customer']
    sfdc = bmcg.customerDetails['id']    
    grid = bmcg.customerDetails['grid']
    folder = getStagingGridPath(grid)
    logFiles = getStagingLogFiles(folder,pattern)
    logCount = len(logFiles)
    mpSupport = bmcg.customerDetails['mp']

    for logFile in logFiles:
        logEntry = logFile + "#" + customer + "#" + sfdc + "#" + grid + "#" 
        logList.append(logEntry)     

    if mpSupport == "true":
        mpCpu = cpu_count() 
        mpPoolMultiplier = int(bmcg.mpPoolMultiplier)
        mpPoolCount = int(mpCpu * mpPoolMultiplier)
        mpPool = Pool(processes=mpPoolCount)         
        procStart = time.time()
        if bmcg.verbose:
            bmcs.logStatus(" - TSO Grid",grid)
            bmcs.logStatus(" - TSO Log Type","STD Error")
            bmcs.logStatus(" - Analyzing Log Files",logCount)
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Multi Processes Multiplier", bmcg.mpPoolMultiplier)
            bmcs.logStatus(" - Multi Processor Count",mpCpu)
            bmcs.logStatus(" - Multi Processes Pool",mpPoolCount)
        mpPool.map(analyseStdErrLog,logList)
        mpPool.close()
        mpPool.join()         
        procEnd = time.time()
        procDuration = bmcs.timer(procStart,procEnd)
        print("")
        if bmcg.verbose:
            bmcs.logStatus(" - Analyzing Log Files Start",procStart)
            bmcs.logStatus(" - Analyzing Log Files End  ",procEnd) 
            bmcs.logStatus(" - Analyzing Log Files Duration",procDuration) 
    else:
        logFileCount = len(logFiles)
        if bmcg.verbose:
            bmcs.logStatus("Multi Processor Support",mpSupport)
            bmcs.logStatus("Total Log Files",logFileCount)
        
        analyzeStdErrLogsWithpBar(logList) 

def analyzeCatalinaLogs():
    logList = []
    pattern = "tso-catalina"
    customer = bmcg.customerDetails['customer']
    sfdc = bmcg.customerDetails['id']    
    grid = bmcg.customerDetails['grid']
    folder = getStagingGridPath(grid)
    logFiles = getStagingLogFiles(folder,pattern)
    logCount = len(logFiles)
    mpSupport = bmcg.customerDetails['mp']

    for logFile in logFiles:
        logEntry = logFile + "#" + customer + "#" + sfdc + "#" + grid + "#" 
        logList.append(logEntry)      
    
    if mpSupport == "true":
        mpCpu = cpu_count() 
        mpPoolMultiplier = int(bmcg.mpPoolMultiplier)
        mpPoolCount = int(mpCpu * mpPoolMultiplier)
        mpPool = Pool(processes=mpPoolCount) 
        procStart = time.time()
        if bmcg.verbose:
            bmcs.logStatus(" - TSO Grid",grid)
            bmcs.logStatus(" - TSO Log Type","Catalina")
            bmcs.logStatus(" - Analyzing Log Files",logCount)
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Multi Processes Multiplier", bmcg.mpPoolMultiplier)
            bmcs.logStatus(" - Multi Processor Count",mpCpu)
            bmcs.logStatus(" - Multi Processes Pool",mpPoolCount)
        mpPool.map(analyseCatalinaLog,logList)
        mpPool.close()
        mpPool.join()      
        procEnd = time.time()
        procDuration = bmcs.timer(procStart,procEnd) 
        print("")
        if bmcg.verbose:   
            bmcs.logStatus(" - Analyzing Log Files Start",procStart)
            bmcs.logStatus(" - Analyzing Log Files End  ",procEnd) 
            bmcs.logStatus(" - Analyzing Log Files Duration",procDuration)  
    else:
        logFileCount = len(logFiles)
        if bmcg.verbose:
            bmcs.logStatus(" - Multi Processor Support",mpSupport)
            bmcs.logStatus(" - Total Log Files",logFileCount)
        
        analyzeCatalinaLogsWithpBar(logList) 

def getAnalysisGrid():
    pass        


def archiveLogs():
    pass

# bmcg.customerDetails = getCustomerDetails(_customerFile)


if __name__ == "__main__":
    print (f"Version: {_modVer}")
