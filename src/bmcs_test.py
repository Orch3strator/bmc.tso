#!/usr/bin/env python3
import bmcs_core as bmcs
import os

timestamp = "21 Feb 2019 08:15:19,033,"

if __name__ == "__main__":
    print(f"==== BMC Test ====")
    sTime = bmcs.getTimeInHourFromStr(timestamp)
    sDate = bmcs.getDateFromStr(timestamp)
    sFolder = bmcs.getLocalFolder()
    sOsType = bmcs.getOsType()
    sPath = bmcs.getAnalysisPath()
    sPeers = bmcs.getFolders(sPath)
    csvFileName = bmcs.getCsvFileName("tso-analysis.csv")

    timeStamp = "21 Feb 2019 00:47:43,616"
    timeLen = len(timeStamp)

    print(f"Date={sDate} Time={sTime}")
    print(f"Local Folder={sFolder}")
    print(f"OS Type={sOsType}")
    print(f"File Name={csvFileName}")
    #print(f"Length={timeLen}")

    if timeStamp[0].isdigit() and len(timeStamp) == 24 and  "2019" in timeStamp:
        print(f"Time={timeStamp}")
        print(f"Length={timeLen}")






