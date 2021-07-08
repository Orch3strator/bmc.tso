#!/usr/bin/env python3
import os, sys, time, re, json
from multiprocessing import cpu_count
from datetime import datetime
import bmcs_core as bmcs
import csv
from collections import Counter
from itertools import chain
import progressbar 

modVer = "1.0"
pbar = progressbar.ProgressBar()
folderTsoLogs = bmcs.getAnalysisPath()
scriptPath = os.getcwd() 
peers = bmcs.getTsoPeers(folderTsoLogs)

tsoGridLogFile = []
tsoGridLogFile = bmcs.getTsoAnalysisGridLogFiles(folderTsoLogs)

if __name__ == "__main__":
    print(f"==== TSO Grid Log File Anaysis ====")
    processes = []
    processors = cpu_count()
    csvFileNameError = bmcs.getCsvFileName("tso-analysis-error.csv")
    csvFileNameWarn = bmcs.getCsvFileName("tso-analysis-warn.csv")
    startTime = time.time()

    bmcs.logStatus("- CPU Cores",processors)
    bmcs.logStatus("- CSF File Warning",csvFileNameWarn)
    bmcs.logStatus("- CSV File Error",csvFileNameError)
    bmcs.logStatus("- Start",startTime)
 
    dictWarn = {}
    dictError = {}
    listError = []
    listWarn = []
    bmcs.logStatus("- Log Files",len(tsoGridLogFile))
    linesGridAll = []
    for logFile in pbar(tsoGridLogFile):
        # bmcs.logStatus("- Read File",logFile)
        cnt = 0
        peer = bmcs.getParentBaseFolder(logFile)
        
        jobList = ""
        # if "0000.log" in logFile:
        linesLogFile = bmcs.readTsoLog(logFile)
    
        for line in linesLogFile:
            linesGridAll.append(line)
        
    # Process all log entries
    linesCountLogFile = len(linesLogFile)
    linesCountAllLogFile  = len(linesGridAll)
    bmcs.logStatus("- Log Entries",linesCountAllLogFile)

    widgets = [progressbar.Percentage(),' ', progressbar.Bar(),' ', progressbar.ETA(),' ', progressbar.AdaptiveETA()]
    cnt = 0
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=linesCountAllLogFile)
    pbar.start()
    for line in pbar(linesGridAll):
        timeStamp = ""
        sTime = ""
        sDate = ""
        sTimeInHour = ""
        errorLevel = ""
        errorType = ""
        jobID = ""
        adapterName = ""
        logMessage = ""
        logList = ""

        logEntries = re.split('#',line)
        logMessage = logEntries[-2]

        if logMessage.find("[") == 0:
            logMessage = logEntries[-2].split("[")[1].split("]")[0]
        else:
            logMessage = logEntries[-2]

        for logEntry in logEntries:
            logKey = ""
            logVal = ""
            logRaw = logEntry
            if logEntry:
                lineCounter = cnt
                if logEntry.find("[") == 0:
                    logEntry = logEntry[1:-1]
                if "ERROR" in logEntries[2] or "WARN" in logEntries[2]: 
                #if "ERROR" in logEntries[2]:    
                    if "=" in logEntry:
                        logKV = re.split('=',logEntry)
                        logKey = logKV[0]
                        logVal = logKV[1]
                    if bmcs.is_date(logEntry):
                        if logEntry[0].isdigit() and len(logEntry) == 24 and "2019" in logEntry:
                            timeStamp = logEntry     
                            sTime = bmcs.getTimeFromStr(timeStamp)
                            sDate = bmcs.getDateFromStr(timeStamp)
                            sTimeInHour = bmcs.getTimeInHourFromStr(timeStamp)    
                    if "ERROR" in logEntry:
                        errorLevel = logEntry.split(" ")[0]
                        errorType = logEntry.split(" ")[-1]
                    if "WARN" in logEntry:
                        errorLevel = logEntry.split(" ")[0]
                        errorType = logEntry.split(" ")[2]  
                    if "JobID" in logKey:
                        jobID = logVal    
                    if "AdapterName" in logKey:
                        adapterName = logVal
        pbar.update(cnt+1)
        cnt += 1
                # ['Peer','Error_Level','Error_Type','Adapter','Job_ID','Start','Date','Time','TimeStamp','Message']
        if "WARN" in errorLevel:
            logList =  {'Peer': peer, 'Error_Level': errorLevel,  'Error_Type': errorType, 'Adapter':adapterName , 'Job_ID':jobID, 'Start':sTimeInHour, 'Date':sDate, 'Time':sTime, 'TimeStamp':timeStamp,'Message':logMessage} 
            # datapoints = [peer,errorLevel,errorType,adapterName,jobID,sTimeInHour,sDate,sTime,timeStamp,logMessage]
            dictWarn.update(logList)
            listWarn.append(logList)

        if "ERROR" in errorLevel:
            logList =  {'Peer': peer, 'Error_Level': errorLevel,  'Error_Type': errorType, 'Adapter':adapterName , 'Job_ID':jobID, 'Start':sTimeInHour, 'Date':sDate, 'Time':sTime, 'TimeStamp':timeStamp,'Message':logMessage}
            # datapoints = [peer,errorLevel,errorType,adapterName,jobID,sTimeInHour,sDate,sTime,timeStamp,logMessage]
            dictError.update(logList)
            listError.append(logList)
    pbar.finish()

    linesCounlistError = len(listError)
    bmcs.logStatus("- CSV File Name",csvFileNameError)
    bmcs.logStatus("- CSV File Type","Error")
    bmcs.logStatus("- Log Entries",linesCounlistError)
    
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=linesCounlistError)
    with open(csvFileNameError, 'w',newline='') as csvFile:
        csvColumns = ['Peer','Error_Level',  'Error_Type', 'Adapter' , 'Job_ID', 'Start', 'Date', 'Time', 'TimeStamp','Message']
        writer = csv.DictWriter(csvFile, dialect='excel', fieldnames=csvColumns, delimiter=',')
        writer.writeheader()

        for data in pbar(listError):
                writer.writerow(data)

    linesCounlistWarn = len(listWarn)
    bmcs.logStatus("- CSV File Name",csvFileNameWarn)
    bmcs.logStatus("- CSV File Type","Warn")
    bmcs.logStatus("- Log Entries",linesCounlistWarn)
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=linesCounlistWarn)
    with open(csvFileNameWarn, 'w',newline='') as csvFile:
        csvColumns = ['Peer','Error_Level',  'Error_Type', 'Adapter' , 'Job_ID', 'Start', 'Date', 'Time', 'TimeStamp','Message']
        writer = csv.DictWriter(csvFile, dialect='excel', fieldnames=csvColumns, delimiter=',')
        writer.writeheader()

        for data in pbar(listWarn):
                writer.writerow(data)            
       
    
    

            



             


