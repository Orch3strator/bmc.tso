#!/usr/bin/env python3
import os, sys, time, re, json
from multiprocessing import cpu_count
from datetime import datetime
import bmcs_core as bmcs
import csv
from collections import Counter
from itertools import chain

modVer = "1.0"

folderTsoLogs = bmcs.getAnalysisPath()
scriptPath = os.getcwd() 
peers = bmcs.getTsoPeers(folderTsoLogs)

tsoProcessLogFile = []
tsoProcessLogFile = bmcs.getTsoAnalysisProcessLogFiles(folderTsoLogs)

if __name__ == "__main__":
    print(f"==== TSO Process Log File Anaysis ====")
    processes = []
    processors = cpu_count()
    bmcs.logStatus("- CPU Cores",processors)
    start_time = time.time()
    csvFileName = bmcs.getCsvFileName("tso-analysis.csv")

    dictJobs = {}

    with open(csvFileName, 'w',newline='') as csvfile:
        header = ['Peer','Module','Workflow','Process','Root_Job_ID','Start','Duration','Date','Time','TimeStamp','Status' ]
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(header)

        for logFile in tsoProcessLogFile:
            bmcs.logStatus("- Analyse",logFile)
            cnt = 0
            peer = bmcs.getParentBaseFolder(logFile)
            linesProcAll = []
            linesProc = []
            #if "0000.log" in logFile:
            linesProc = bmcs.readTsoLog(logFile)
            
            for line in linesProc:
                linesProcAll.append(line)

            for line in linesProcAll:
                cnt += 1
                logEntries = re.split('#',line)
                for logEntry in logEntries:
                    logKey = ""
                    logVal = ""
                    if logEntry != "":
                        if logEntry.find("[") == 0:
                            logEntry = logEntry[1:-1]
                        if "=" in logEntry:
                            logKV = re.split('=',logEntry)
                            logKey = logKV[0]
                            logVal = logKV[1]
                        
                        lineCounter = cnt

                        if "Current Time" in logKey:
                            timestamp = logVal                            
                        if "Process Name" in logKey:
                            procMod = logVal.split(":")
                            procModule = procMod[1]
                            procWorkflow = procMod[-1]
                            procName = logVal
                        if "Root Job Id" in logKey:
                            rootJobID = logVal
                        if "Job Id" in logKey:
                            jobID = logVal    
                        if "ProcessTermination" in logKey:
                            procTermination = logVal
                            procTime = logVal[logVal.index("took") + len("took"):].split("m")[0].strip().replace(',', '')
                            procTermState = logVal[logVal.index("The process terminated in the") + len("The process terminated in the"):].split("state")[0].strip()
                            procTimestamp = logVal[logVal.index("The process started at") + len("The process started at"):].split("terminated")[0].strip()
                            # 21 Feb 2019 08:15:19,033,
                            sTime = bmcs.getTimeFromStr(procTimestamp)
                            sDate = bmcs.getDateFromStr(procTimestamp)
                            sTimeInHour = bmcs.getTimeInHourFromStr(procTimestamp)                            
                            
                #  ['Peer','Module','Workflow','Process','Root_Job_ID','Start','Duration','Date','Time','TimeStamp','Status' ]

                jobList =  {'Peer': peer, 'Module': procModule, 'Workflow':procWorkflow , 'Process':procName, 'Root_Job_ID':rootJobID, 'Start':sTimeInHour, 'Duration':procTime, 'Date':sDate, 'Time':sTime, 'TimeStamp':procTimestamp,'Status':procTermState} 
                dictJobs.update(jobList)
                datapoints = [peer,procModule,procWorkflow,procName,rootJobID,sTimeInHour,procTime,sDate,sTime,procTimestamp,procTermState]                                       
                writer.writerow(datapoints)

            



             


