#!/usr/bin/env python3
import os
import sys
import time
from multiprocessing import Pool, Process, cpu_count, current_process
from multiprocessing.dummy import Pool as ThreadPool

import bmcs_core as bmcs

folderTsoLogs = "D:\\Data\\TSO\\Logs\\Grid"
scriptPath = os.getcwd()   
peers = bmcs.getTsoPeers(folderTsoLogs)

tsoProcessLogFile = []
tsoProcessLogFile = bmcs.getTsoProcessLogFiles(folderTsoLogs)

tsoGridLogFile = []
tsoGridLogFile = bmcs.getTsoGridLogFiles(folderTsoLogs)

tsoHealthLogFile = []
tsoHealthLogFile = bmcs.getTsoHealthLogFiles(folderTsoLogs)

cpuCount = bmcs.getCpuCount()
cpuUtil = bmcs.getCpuUtil()



if __name__ == "__main__":
    print(f"==== TSO Log File Collection ====")
    processesProc = []
    processesGrid = []
    processors = cpu_count()
    bmcs.logStatus("- CPU Cores",processors)
    start_time = time.time()

    bmcs.logStatus("- Centralize","Process Logs")
    for logFileProc in tsoProcessLogFile:
        fileStatus = bmcs.getTsoAnalysisFileStatus(logFileProc)
        # if not fileStatus:
        #     if "log.0" in logFileProc:
        #         status = bmcs.centralizeTsoProc(logFileProc)

        # Check if target analysis file exists already
        
        if not fileStatus:
            processProc = Process(target=bmcs.centralizeTsoProc, args=(logFileProc,))
            processesProc.append(processProc)
            processProc.start()
            bmcs.logStatus("- File Process Log",logFileProc)

    for proc in processesProc:
            proc.join()

    bmcs.logStatus("- Centralize","Grid Logs")
    for logFileGrid in tsoGridLogFile:
        fileStatus = bmcs.getTsoAnalysisFileStatusGrid(logFileGrid)
        
        # bmcs.logStatus("- Grid Log",logFileGrid)
        # if "log.0" in logFile:
        #     status = bmcs.centralizeTsoGrid(logFile)

        # Check if target analysis file exists already
        
        if not fileStatus:
            processGrid = Process(target=bmcs.centralizeTsoGrid, args=(logFileGrid,))
            processesGrid.append(processGrid)
            processGrid.start()
            bmcs.logStatus("- File Grid Log",logFileGrid)

    for proc in processesGrid:
        proc.join()

    bmcs.logStatus("- Centralize","Health Logs")
    for logFileHealth in tsoHealthLogFile:
        fileStatus = bmcs.getTsoAnalysisFileStatusHealth(logFileHealth)
        if not fileStatus:
            bmcs.copyTsoLogFile(logFileHealth)



    duration = time.time() - start_time
    bmcs.logStatus("- Duration",duration)
