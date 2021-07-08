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

tsoHealthLogFile = []
tsoHealthLogFile = bmcs.getTsoAnalysisHealthLogFiles(folderTsoLogs)

if __name__ == "__main__":
    print(f"==== TSO Health Log File Anaysis ====")
    processes = []
    processors = cpu_count()
    bmcs.logStatus("- CPU Cores",processors)
    start_time = time.time()
    csvFileNameHealth = bmcs.getCsvFileName("tso-analysis-health.csv")
    bmcs.logStatus("- Report",csvFileNameHealth)

    dictJobs = {}

    with open(csvFileNameHealth, 'w',newline='') as csvfile:
        #          Collector ,Peer,  Type  ,Name,  Metric,  Value,  Start,  Date,  Time,  Recorded,  Measured, Deviation,  Quality
        header = ['Collector','Peer','Type','Name','Metric','Value','Start','Date','Time','Recorded','Measured','Deviation','Quality' ]
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(header)

        for logFile in tsoHealthLogFile:
            bmcs.logStatus("- Analyse",logFile)
            cnt = 0
            collector = bmcs.getParentBaseFolder(logFile)
            linesProcAll = []
            linesProc = []
            linesAdapters = []
            #if "0000.log" in logFile:
            linesProc = bmcs.readTsoLog(logFile)
            for line in linesProc:
                if "HEALTH_STAT" in line:
                    linesProcAll.append(line)

            for line in linesProcAll:
                cnt += 1
                logEntries = re.split(',',line)
                logType = logEntries[0]
                logTimestamp = logEntries[1].strip()
                logEntry = logEntries[2].strip()
                if logType.startswith("G"):
                    logEntryType = logEntry
                else:
                    logEntryType = re.split(':',logEntry)[0]

                # Process log entry type
                # G=Grid
                
                if logEntryType == "A":
                    peer = re.split(':',logEntry)[1]
                    metricType = "Adapter"
                    adapter = re.split(':',logEntry)[2]
                    metricName = logEntries[3].strip()
                    metricVal  = logEntries[4].strip()
                    metricTimeStamp = logEntries[5].strip().split(" ")
                    metricRecorded = logTimestamp
                    metricMeasured = logEntries[5].strip()
                    sDate = metricTimeStamp[0]                  
                    sTime = metricTimeStamp[1]
                    sTimeInHour = str(sTime.split(":")[0] + ":00:00" )

                    timeDateRecord = datetime.strptime(metricRecorded, '%Y-%m-%d %H:%M:%S')
                    timeDateMetric = datetime.strptime(sDate + " " + sTime , '%Y-%m-%d %H:%M:%S')
                    timeDelta = timeDateRecord - timeDateMetric
                    timeDelta = timeDelta.days * 24 * 3600 + timeDelta.seconds

                    if timeDelta < 120:
                        metricQuality = "OK"
                    elif timeDelta < 240:
                        metricQuality = "INFO"
                    elif timeDelta < 480:
                        metricQuality = "WARN"
                    else:
                        metricQuality = "FAIL"
                    #             Collector,Peer,Type      ,Name   ,Metric    ,Value    ,Start      ,Date ,Time ,Recorded      ,Measured      ,Deviation,Quality
                    datapoints = [collector,peer,metricType,adapter,metricName,metricVal,sTimeInHour,sDate,sTime,metricRecorded,metricMeasured,timeDelta,metricQuality] 
                    writer.writerow(datapoints)

                elif logEntryType == "C":
                    peer = re.split(':',logEntry)[1]
                    metricType = "Component"
                    component = re.split(':',logEntry)[2]
                    metricName = logEntries[3].strip()
                    metricVal  = logEntries[4].strip()
                    metricTimeStamp = logEntries[5].strip().split(" ")
                    metricRecorded = logTimestamp
                    metricMeasured = logEntries[5].strip()
                    sDate = metricTimeStamp[0]                  
                    sTime = metricTimeStamp[1]
                    sTimeInHour = str(sTime.split(":")[0] + ":00:00" )

                    timeDateRecord = datetime.strptime(metricRecorded, '%Y-%m-%d %H:%M:%S')
                    timeDateMetric = datetime.strptime(sDate + " " + sTime , '%Y-%m-%d %H:%M:%S')
                    timeDelta = timeDateRecord - timeDateMetric
                    timeDelta = timeDelta.days * 24 * 3600 + timeDelta.seconds

                    if timeDelta < 120:
                        metricQuality = "OK"
                    elif timeDelta < 240:
                        metricQuality = "INFO"
                    elif timeDelta < 480:
                        metricQuality = "WARN"
                    else:
                        metricQuality = "FAIL"
                    #             Collector,Peer,Type      ,Name   ,Metric    ,Value    ,Start      ,Date ,Time ,Recorded      ,Measured      ,Deviation,Quality
                    datapoints = [collector,peer,metricType,adapter,metricName,metricVal,sTimeInHour,sDate,sTime,metricRecorded,metricMeasured,timeDelta,metricQuality] 
                    writer.writerow(datapoints)


                elif logEntryType == "G":
                    peer = ""
                    grid = "My-Grid"
                    metricType = "Grid"
                    metricName = logEntries[3].strip()
                    metricVal  = logEntries[4].strip()
                    metricTimeStamp = logEntries[5].strip().split(" ")
                    metricRecorded = logTimestamp
                    metricMeasured = logEntries[5].strip()
                    sDate = metricTimeStamp[0]                  
                    sTime = metricTimeStamp[1]
                    sTimeInHour = str(sTime.split(":")[0] + ":00:00" )

                    timeDateRecord = datetime.strptime(metricRecorded, '%Y-%m-%d %H:%M:%S')
                    timeDateMetric = datetime.strptime(sDate + " " + sTime , '%Y-%m-%d %H:%M:%S')
                    timeDelta = timeDateRecord - timeDateMetric
                    timeDelta = timeDelta.days * 24 * 3600 + timeDelta.seconds

                    if timeDelta < 120:
                        metricQuality = "OK"
                    elif timeDelta < 240:
                        metricQuality = "INFO"
                    elif timeDelta < 480:
                        metricQuality = "WARN"
                    else:
                        metricQuality = "FAIL"
                    #             Collector,Peer,Type      ,Name   ,Metric    ,Value    ,Start      ,Date ,Time ,Recorded      ,Measured      ,Deviation,Quality
                    datapoints = [collector,peer,metricType,grid,metricName,metricVal,sTimeInHour,sDate,sTime,metricRecorded,metricMeasured,timeDelta,metricQuality] 
                    writer.writerow(datapoints)
                elif logEntryType == "P":
                    peer = re.split(':',logEntry)[1]
                    metricType = "Peer"
                    metricName = logEntries[3].strip()

                    if metricName == "HOST_VENDOR":
                        metricVal  = logEntries[4:-1] #.strip()
                        metricVal = ''.join(map(str, metricVal)).strip()
                        metricTimeStamp = logEntries[-1:] 
                        metricTimeStamp = metricTimeStamp[0].strip().split(" ")
                        metricRecorded = logTimestamp
                        metricMeasured = logEntries[-1:] #.strip()
                        metricMeasured = metricMeasured[0].strip()
                    else:
                        metricVal  = logEntries[4].strip()
                        metricTimeStamp = logEntries[5].strip().split(" ")
                        metricRecorded = logTimestamp
                        metricMeasured = logEntries[5].strip()

                    sDate = metricTimeStamp[0]                  
                    sTime = metricTimeStamp[1]
                    sTimeInHour = str(sTime.split(":")[0] + ":00:00" )

                    timeDateRecord = datetime.strptime(metricRecorded, '%Y-%m-%d %H:%M:%S')
                    timeDateMetric = datetime.strptime(sDate + " " + sTime , '%Y-%m-%d %H:%M:%S')
                    timeDelta = timeDateRecord - timeDateMetric
                    timeDelta = timeDelta.days * 24 * 3600 + timeDelta.seconds

                    if timeDelta < 120:
                        metricQuality = "OK"
                    elif timeDelta < 240:
                        metricQuality = "INFO"
                    elif timeDelta < 480:
                        metricQuality = "WARN"
                    else:
                        metricQuality = "FAIL"
                    #             Collector,Peer,Type      ,Name   ,Metric    ,Value    ,Start      ,Date ,Time ,Recorded      ,Measured      ,Deviation,Quality
                    datapoints = [collector,peer,metricType,peer,metricName,metricVal,sTimeInHour,sDate,sTime,metricRecorded,metricMeasured,timeDelta,metricQuality] 
                    writer.writerow(datapoints)
                else:
                    pass



                # for logEntry in logEntries:
                #     logKey = ""
                #     logVal = ""
                #     if logEntry != "":
                #        pass 
                          
                            
                #  ['Peer','Module','Workflow','Process','Root_Job_ID','Start','Duration','Date','Time','TimeStamp','Status' ]

                #jobList =  {'Peer': peer, 'Module': procModule, 'Workflow':procWorkflow , 'Process':procName, 'Root_Job_ID':rootJobID, 'Start':sTimeInHour, 'Duration':procTime, 'Date':sDate, 'Time':sTime, 'TimeStamp':procTimestamp,'Status':procTermState} 
                #dictJobs.update(jobList)
                #datapoints = [peer,procModule,procWorkflow,procName,rootJobID,sTimeInHour,procTime,sDate,sTime,procTimestamp,procTermState]                                       
                #writer.writerow(datapoints)

            



             


