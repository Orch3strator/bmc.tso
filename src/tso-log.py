#!/usr/bin/env python3
from re import compile, search, split
from sys import exit
from time import strptime
from datetime import datetime, timedelta, tzinfo
import sys  
import os
import json
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

infra_host_address = ""
infra_host_port = "8086"
infra_user = ""
infra_password = ""
infra_db_name = "tso"


#change this variable to point to the location of the TrueSight Orchestration Log file(s)
LOG_FILE_LOCATION = 'D:\\Data\\TSO\\Logs\\'
CFG_FILE_LOCATION = 'D:\\Data\\TSO\\Analysis\\'
LINES_PROCESSED = 0

class Timezone(tzinfo):
    
    def __init__(self, name="+0000"):
        self.name = name
        seconds = int(name[:-2])*3600 + int(name[-2:])*60
        self.offset = timedelta(seconds=seconds)

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return self.name

def process_tso_grid_log(log_file_location=LOG_FILE_LOCATION):
    log_name = "grid.log"
    log_file_location = log_file_location + log_name
    cnt = 0
    try:
        log_file = open(log_file_location, 'r')
        print ("- Processing log file: "+log_file_location)
        metric_grid = "tso-grid"
        for line in log_file:
            line = line.strip('\n')
            if line.startswith("HEALTH_STAT"): 
               metric_values = line.split(",")
               metric_temp = metric_values[2].split(":")
               metric_log_timestamp = metric_values[1].lstrip()
               metric_timestamp = metric_values[5].lstrip()
               metric_peer = ""
               metric_name = ""
               metric_value = ""
               metric_instance = ""

               if metric_temp[0].startswith(" A"):
                   metric_type = "Adapter"
                   metric_peer = metric_temp[1].lstrip()
                   metric_instance = metric_temp[2].lstrip()
                   metric_name = metric_values[3].lstrip()
                   metric_value = metric_values[4].lstrip()
               if metric_temp[0].startswith(" C"):
                   metric_type = "Component"
                   metric_peer = metric_temp[1].lstrip()
                   metric_instance = ""
                   metric_name =  metric_temp[2].lstrip()
                   metric_value = metric_values[4].lstrip()
               if metric_temp[0].startswith(" P"):
                   metric_type = "Peer"
                   metric_peer = metric_temp[1].lstrip()
                   metric_instance = "" 
                   metric_name = metric_values[3].lstrip()
                   metric_value = metric_values[4].lstrip()                        
               if metric_temp[0].startswith(" G"):
                   metric_type = "Grid"
                   metric_name = metric_values[3].lstrip()
                   metric_value = metric_values[4].lstrip()      

               datapoints = [
                    {
                        "measurement": "health",
                        "tags": {"topic":"health","grid": metric_grid,"peer": metric_peer},
                        "time": metric_timestamp,
                        "fields": {"grid":metric_grid,"peer": metric_peer,"entry":metric_log_timestamp,"type": metric_type,
                                   "instance": metric_instance,"name": metric_name,"value":metric_value,
                                   "timestamp":metric_timestamp,"message":line
                                   }
                        }
                ]
               datapoints = json.dumps(datapoints, indent=4)
               print("- Health Metric {0} ".format(datapoints))
               
               
               

            #    if not submit_datapoints(datapoints):
            #        print("- Influx submit failed {0}".format(cnt))
            #        print("- Write metrics {0} ".format(datapoints))
            #    else:
            #         print("- processing {0}".format(cnt))

               cnt += 1

    except IOError:
        exit("Log file not found at "+log_file_location)

    finally:
        log_file.close()

def extract_infrastructure(log_file_location=LOG_FILE_LOCATION):
    log_name = "grid.log"
    log_file_location = log_file_location + log_name
    host_name = ""
    host_is_virtual = ""
    host_peer_name = ""
    host_toal_ram = ""
    host_vendor = ""
    host_ipv4 = ""
    host_max_heap = ""
    host_os_arch = ""
    host_os_name =""
    host_tso_version = ""
    compute_host = False
    cnt = 0
    host_cnt = 1
    peer_list = []
    datapoints = []
    try:
        log_file = open(log_file_location, 'r')
        print ("- Processing log file: "+log_file_location)
        metric_grid = "tso-grid"
        for line in log_file:
            line = line.strip('\n')
            if line.startswith("HEALTH_STAT"): 
               metric_values = line.split(",")
               metric_temp = metric_values[2].split(":")
               metric_name = metric_values[3].lstrip()
               metric_value = metric_values[4].lstrip()
               metric_timestamp = metric_values[5].lstrip()

               if metric_temp[0].startswith(" P"):  
                    host_peer_name = metric_temp[1].lstrip()           
                    if metric_name.startswith("HOSTNAME"):
                        host_name = metric_value
                    if metric_name.startswith("HOST_IS_VIRTUAL"):
                        host_is_virtual = metric_value
                    if metric_name.startswith("HOST_TOTAL_RAM"):
                        host_toal_ram = metric_value
                    if metric_name.startswith("HOST_VENDOR"):
                        host_vendor = metric_value
                    if metric_name.startswith("IPV4_ADDRESS"):
                        host_ipv4 = metric_value
                    if metric_name.startswith("MAX_HEAP_SIZE"):
                        host_max_heap = metric_value
                    if metric_name.startswith("OS_ARCH"):
                        host_os_arch = metric_value
                    if metric_name.startswith("OS_NAME"):
                        host_os_name = metric_value                                                                            
                    if metric_name.startswith("PRODUCT_VERSION"):
                        host_tso_version = metric_value
                        compute_host = True

            if compute_host:
                if host_name not in peer_list:
                    peer_list.append(host_name)

                    datapoints = [
                        {
                            "computersystem": host_name,
                            "tags": {"topic":"infrastructure","grid": metric_grid,"peer": host_peer_name,"hostname": host_name},
                            "time": metric_timestamp,
                            "id": host_cnt,
                            "peer":host_peer_name,
                            "hostname":host_name,
                            "is_virtual":host_is_virtual,
                            "ram":host_toal_ram,
                            "vendor":host_vendor,
                            "ipv4":host_ipv4,
                            "max_heap":host_max_heap,
                            "os_arch":host_os_arch,
                            "os_name":host_os_name,
                            "version":host_tso_version
                            }
                    ]
                    
                    datapoints = json.dumps(datapoints, indent=4)
                    save_cfg(json_body=datapoints,hostname=host_name)                
                    host_cnt += 1
                   
                compute_host = False
            cnt += 1
        

           

    except IOError:
        exit("Log file not found at "+log_file_location)

    finally:
        log_file.close()



def process_tso_log(log_file_location=LOG_FILE_LOCATION):
    print ("Processing TSO log files ")
    process_tso_grid_log()

def save_cfg(cfg_file_location=CFG_FILE_LOCATION,json_body="",hostname=""):
    # CFG_FILE_LOCATION
    cfg_name = hostname.lower() +".json"
    cfg_file_location = cfg_file_location + cfg_name
    
    try:
        with open(cfg_file_location, 'w') as cfg_file:
            json_body = json.loads(json_body)
            # json.dump(json_body, cfg_file, indent=4, separators=(',', ': '), sort_keys=True)
            cfg_file.write(json.dumps(json_body, indent=4) + "\n")
            cfg_file.close()
            
        print(cfg_file_location + " created. ")    
    except FileNotFoundError:
        print(cfg_file_location + " not found. ") 


def submit_datapoints(json_body):
    try:
     infraClient = InfluxDBClient(host=infra_host_address, port=infra_host_port, username=infra_user, password=infra_password)
     
    except Exception as err:
        print("- Influx connection error: %s" % str(err))
   
    if infraClient:
        try:
            influx_data = json.loads(json_body)
            infraClient.switch_database(infra_db_name)
            bResult = infraClient.write_points(influx_data, protocol=u'json')
            
        except Exception as err:
            print("- Entry was not recorded. Influx write error: %s" % str(err))	
            print("- Submit metrics {0} ".format(influx_data))
    infraClient.close()  
    return bResult 
    
# HEALTH_STAT, 2019-02-21 00:51:39, A:CDPPGRID01:DSVC_DSA_P_BMCPortalMLM6, RUNNING_STATE, running, 2019-02-15 08:39:20

if __name__ == "__main__":
   extract_infrastructure()
   # process_tso_log()


