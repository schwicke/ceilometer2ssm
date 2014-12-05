#!/usr/bin/python
import sys
sys.path.insert(0, '/usr/lib64/python2.6/site-packages/SQLAlchemy-0.7.8-py2.6-linux-x86_64.egg')
import httplib
import urllib
import json
import cStringIO
import pycurl
import re
import os
import copy
from pwd import getpwnam
from dateutil import parser
import urlparse
from dirq.QueueSimple import QueueSimple
import argparse
import subprocess
from itertools import groupby
import shlex
from datetime import date, datetime, timedelta
from calendar import monthrange
from time import localtime, strftime
from cloudaccounting import api as db_api
from collections import defaultdict
import logging
from prettytable import PrettyTable
import json
from caapi.config import read_config


mysql_url=""
start_time=""
end_time=""

config=read_config()
dbuser=config['database']['user']
dbpwd=config['database']['password']
database_name=config['database']['database_name']
MYSQL_URL = "mysql://"+dbuser+":"+dbpwd+"@localhost:3306/cloudaccounting"    


# getting the sample volume and sampling time of the first sample

def get_start_sample_info(row_list):
    result={}
    try:
        #row_list = sorted(row_list,key=lambda x:x["counter_volume"])
        #start_sample_time=row_list[0]["start_time"]
        #start_sample_value=row_list[0]["counter_volume"]
        start_sample_time=row_list[0]["sample_time"]
        start_sample_value=row_list[0]["counter_volume"]
        resource_id=row_list[0]["r_id"]
        for row in row_list:
            sample_time=row["start_time"]
            r_id=row["r_id"]
            sample_value=row["counter_volume"]
            sample_value=float(sample_value)
            start_sample_value=float(start_sample_value)
            if(long(sample_value) < long(start_sample_value)):
                start_sample_value=sample_value
                start_sample_time=sample_time
        result={"start_time":start_sample_time,"start_sample_value":start_sample_value}
    except:
        logging.info("Error Ocuured while calculating the start sample value")
    return result

# getting the sample volume and sampling time of the last sample

def get_end_sample_info(row_list):
     result={}
     try:
        #row_list = sorted(row_list, key=lambda x:x["counter_volume"])
        #end_sample_time=row_list[-1]["end_time"]
        #end_sample_value=row_list[-1]["counter_volume"]
        end_sample_time=row_list[0]["end_time"]
        end_sample_value=row_list[0]["counter_volume"]
        resource_id=row_list[0]["r_id"]
        for row in row_list:
            sample_time=row["end_time"]
            r_id=row["r_id"]
            sample_value=row["counter_volume"]
            sample_value=float(sample_value)
            end_sample_value=float(end_sample_value)
            if(long(sample_value) > long(end_sample_value)):
                end_sample_value=sample_value
                end_sample_time=sample_time

        result={"end_time":end_sample_time,"end_sample_value":end_sample_value}
     except:
        logging.info("Error Ocuured while calculating the end sample value")
     return result

# getting the ceilometer data stored the database

def get_ceilo_data_from_database(start_time, end_time, mysql_url):
    logging.info("Contacting the database")
    logging.info("mysql url is %s ",mysql_url)
    db_api.create_session(mysql_url) # starts the database session
    resource_data={}
    sorted_resource_data={}
    sorted_metric_data={}
    resource_data = db_api.get_resource_info() #get the resource data from the data
    metric_data = db_api.get_metric_info(start_time, end_time) #get the metric data from the database
    db_api.shutdown_session() # close the database session
    logging.info("Database communication over")
    # group the metric data based on resource ids
    ceilo_data={}
    tenant_info={}
    #print metric_data
    try: 
        sorted_resource_data=extract_resource_info(resource_data, end_time)
        metric_data = sorted(metric_data,key=lambda x:x["r_id"])
        for rid, row_group in groupby(metric_data, lambda x:x["r_id"]):
            sorted_metric_data[rid] = {}
            cpu_info = []
            net_in_info = []
            net_out_info = []
            for row in row_group:
                counter_name=row["counter_name"]
                if(counter_name=="cpu"):
                    cpu_info.append(row)
                elif(counter_name=="network.incoming.bytes"):
                    net_in_info.append(row)
                elif(counter_name=="network.outgoing.bytes"):
                    net_out_info.append(row)
            sorted_metric_data[rid] = {"cpu_info":cpu_info,"net_in_info":net_in_info,"net_out_info":net_out_info}
            '''#if rid=="84f51ab5-79a0-45d8-ab8a-88d1ef0f74e3":'''
    except:
        logging.info("Error Occured While Sorting the database info")
    ceilo_data={"resource_data":sorted_resource_data, "metric_data":sorted_metric_data}
    #print ceilo_data["metric_data"]
    return ceilo_data

# extract the resource info and group it based on resource ids

def extract_resource_info(resource_data,end_time):
    sorted_resource_data={}
    resource_id=""
    key_not_required =  "_sa_instance_state"
    for row in resource_data:
        try:
            resource_id=str(row["resource_id"]).strip()
            tmp_resource_info={}
            tmp_resource_info = row 
            sorted_resource_data[resource_id]=tmp_resource_info
        except:
            logging.info("Error occured while finding the resource id")
    return sorted_resource_data

# makes the input for the ssm coversion module

def input_creation(ceilo_data, start_time, end_time):
    input_data=[]
    sorted_resource_data = ceilo_data["resource_data"]
    sorted_metric_data = ceilo_data["metric_data"]
    res_id = 0
    #print sorted_metric_data
    for resource_id in sorted_metric_data.keys():
        logging.info("ssm input creation for historical data started")
        resource_info={}
        info = {}
        tmp = {}
        try:
            resource_info=sorted_resource_data[resource_id]
            sorted_item=sorted_metric_data[resource_id]
            cpu_info=sorted_item["cpu_info"]
            net_in_info=sorted_item["net_in_info"]
            net_out_info=sorted_item["net_out_info"]
            '''if resource_id=="84f51ab5-79a0-45d8-ab8a-88d1ef0f74e3":
               print net_out_info'''
            tmp_cpu={}
            tmp_net_in={}
            tmp_net_out={}
            #tmp = {}
            try:
                tmp["resource_id"]=resource_info["resource_id"]
            except:
                pass
            try:
                tmp["project_id"]=resource_info["project_id"]
            except:
                pass
            try:
                tmp["user_id"]=resource_info["user_id"]
            except:
                pass
            try:
                tmp["tenant_id"]=resource_info["tenant_id"]
            except:
                pass
            try:
                tmp["tenant_name"]=resource_info["tenant_name"]
            except:
                pass
            try:
                group_name="default"
                try:
                    tenant_name=resource_info["tenant_name"]
                    group_name=tenant_name.split()[0]
                except:
                    logging.info("Group name is default")
                tmp["group_name"]=group_name
            except:
                pass
            try:
                tmp["node"]=resource_info["node"]
            except:
                pass
            try:
                tmp["hep_spec"]=resource_info["hep_spec"]
            except:
                pass
            try:
                tmp["host_name"]=resource_info["host_name"]
            except:
                pass
            try:
                tmp["vmuuid"]=resource_info["vmuuid"]
            except:
                pass
            try:
                tmp["image_id"]=resource_info["image_ref_url"]
            except:
                pass
            try:
                tmp["vcpus"]=resource_info["vcpus"]
            except:
                pass
            try:
                tmp["memory_mb"]=resource_info["memory_mb"]
            except:
                pass
            try:
                tmp["disk_gb"]=resource_info["disk_gb"]
            except:
                pass
            try:
                tmp["state"]=resource_info["state"]
            except:
                pass
            try:
                tmp["deleted"]=resource_info["deleted"]
            except:
                pass
            try:
                tmp["start_time"]=resource_info["launched_at"]
            except:
                pass
            try:
                tmp["end_time"]=resource_info["terminated_at"]
            except:
                pass
            # These four fields are required for daily_resource_data
            try:
                tmp["created_at"]=resource_info["created_at"]
            except:
                pass
            try:
                tmp["launched_at"]=resource_info["launched_at"]
            except:
                pass
            try:
                tmp["deleted_at"]=resource_info["deleted_at"]
            except:
                pass
            try:
                tmp["terminated_at"]=resource_info["terminated_at"]
            except:
                pass

            if(cpu_info):
                start_sample_info = {}
                end_sample_info = {}
                #tmp_cpu = {}
                start_sample_info=get_start_sample_info(cpu_info)
                end_sample_info=get_end_sample_info(cpu_info)
                try:
                    wall_duration=0
                    terminated_time=resource_info["terminated_at"]
                    launched_time=resource_info["launched_at"]
                    if(terminated_time is not None and launched_time is not None):
                        if launched_time > start_time:
                            time_start = launched_time
                        else:
                            time_start = start_time
                        if terminated_time > end_time:
                            time_end = end_time
                        else:
                            time_end = terminated_time
                        diff = time_end - time_start
                        wall_duration = diff.days * 86400 + diff.seconds
                    elif launched_time is not None:
                        if launched_time > start_time:
                            time_start = launched_time
                        else:
                            time_start = start_time
                        diff = end_time - time_start
                        wall_duration = diff.days * 86400 + diff.seconds
                    elif(launched_time is None ):
                        diff = end_sample_info["end_time"] - start_sample_info["start_time"]
                        wall_duration = diff.days * 86400 + diff.seconds
                    logging.info("Launch Time is not available for resource %s" %(resource_id))
                    tmp_cpu["wall_duration"] = wall_duration
                except:
                    print "Some Error in CPU wall"
                    tmp_cpu["wall_duration"] = wall_duration
                    logging.info("Error Occured while calculating wall duration")
                try:
                    tmp_cpu["counter_unit"]=cpu_info[0]["counter_unit"]
                except:
                    pass
                try:
                    tmp_cpu["source"]=cpu_info[0]["source"]
                except:
                    pass
                try:
                    tmp_cpu["counter_type"]=cpu_info[0]["counter_type"]
                except:
                    pass
                try:
                    tmp_cpu["start_counter_volume"]=start_sample_info["start_sample_value"]
                except:
                    pass
                try:
                    tmp_cpu["start_sample_time"]=start_sample_info["start_time"]
                except:
                    pass
                try:
                    tmp_cpu["end_counter_volume"]=end_sample_info["end_sample_value"]
                except:
                    pass
                try:
                    tmp_cpu["end_sample_time"]=end_sample_info["end_time"]
                except:
                    pass

            if(net_in_info):
                start_sample_info = {}
                end_sample_info = {}
                #tmp_net_in = copy.deepcopy(tmp)
                #tmp_net_in = {}
                start_sample_info=get_start_sample_info(net_in_info)
                end_sample_info=get_end_sample_info(net_in_info)
                try:
                    wall_duration=0
                    terminated_time=resource_info["terminated_at"]
                    launched_time=resource_info["launched_at"]
                    if(terminated_time is not None and launched_time is not None):
                        if launched_time > start_time:
                            time_start = launched_time
                        else:
                            time_start = start_time
                        if terminated_time > end_time:
                            time_end = end_time
                        else:
                            time_end = terminated_time
                        diff = time_end - time_start
                        wall_duration = diff.days * 86400 + diff.seconds
                    elif launched_time is not None:
                        if launched_time > start_time:
                            time_start = launched_time
                        else:
                            time_start = start_time
                        diff = end_time - time_start
                        wall_duration = diff.days * 86400 + diff.seconds
                    elif(launched_time is None):
                        diff = end_sample_info["end_time"] - start_sample_info["start_time"]
                        wall_duration = diff.days * 86400 + diff.seconds
                    logging.info("Launch Time is not available for resource %s" %(resource_id))
                    tmp_net_in["wall_duration"]=wall_duration
                except:
                    print "SOme Error in Net INwall"
                    logging.info("Error Occured while calculating wall duration")
                    tmp_net_in["wall_duration"]=wall_duration
                try:
                    tmp_net_in["counter_unit"]=net_in_info[0]["counter_unit"]
                except:
                    pass
                try:
                    tmp_net_in["source"]=net_in_info[0]["source"]
                except:
                    pass
                try:
                    tmp_net_in["counter_type"]=net_in_info[0]["counter_type"]
                except:
                    pass
                try:
                    tmp_net_in["start_counter_volume"]=start_sample_info["start_sample_value"]
                except:
                    pass
                try:
                    tmp_net_in["start_sample_time"]=start_sample_info["start_time"]
                except:
                    pass
                try:
                    tmp_net_in["end_counter_volume"]=end_sample_info["end_sample_value"]
                except:
                    pass
                try:
                    tmp_net_in["end_sample_time"]=end_sample_info["end_time"]
                except:
                    pass

            if(net_out_info):
                #tmp_net_out = copy.deepcopy(tmp)
                #tmp_net_out = {} 
                start_sample_info = {}
                end_sample_info = {}
                start_sample_info = get_start_sample_info(net_out_info)
                end_sample_info = get_end_sample_info(net_out_info)
                try:
                    wall_duration = 0
                    terminated_time = resource_info["terminated_at"]
                    launched_time = resource_info["launched_at"]
                    if(terminated_time is not None and launched_time is not None):
                        if launched_time > start_time:
                            time_start = launched_time
                        else:
                            time_start = start_time
                        if terminated_time > end_time:
                            time_end = end_time
                        else:
                            time_end = terminated_time
                        diff = time_end - time_start
                        wall_duration = diff.days * 86400 + diff.seconds
                    elif launched_time is not None:
                        if launched_time > start_time:
                            time_start = launched_time
                        else:
                            time_start = start_time
                        diff = end_time - time_start
                        wall_duration = diff.days * 86400 + diff.seconds
                    elif(launched_time is None):
                        diff = end_sample_info["end_time"] - start_sample_info["start_time"]
                        wall_duration = diff.days * 86400 + diff.seconds
                    logging.info("Launch Time is not available for resource %s" %(resource_id))
                    tmp_net_out["wall_duration"]=wall_duration
                except:
                        print "Some Error in NET OUT wall"
                        logging.info("Error Occured while calculating wall duration")
                        tmp_net_out["wall_duration"]=wall_duration

                try:
                    tmp_net_out["counter_unit"] = net_out_info[0]["counter_unit"]
                except:
                    pass

                try:
                    tmp_net_out["source"]=net_out_info[0]["source"]
                except:
                    pass

                try:
                    tmp_net_out["counter_type"]=net_out_info[0]["counter_type"]
                except:
                    pass

                try:
                    tmp_net_out["start_counter_volume"]=start_sample_info["start_sample_value"]
                except:
                    pass

                try:
                    tmp_net_out["start_sample_time"]=start_sample_info["start_time"]
                except:
                    pass

                try:
                    tmp_net_out["end_counter_volume"]=end_sample_info["end_sample_value"]
                except:
                    pass

                try:
                    tmp_net_out["end_sample_time"]=end_sample_info["end_time"]
                except:
                    pass
        except:
            logging.info("Possible database corruption detected ! %s",resource_id)
            print "error---------------"
        info = {}
        info = tmp
        info["cpu"] = tmp_cpu
        info["net_in"] = tmp_net_in
        info["net_out"] = tmp_net_out
        #input_data[resource_id]=info
        #print info
        input_data.append(info)
        #res_id=resource_id
    logging.info("ssm input creation for historical data finished")
    #print input_data
    return input_data


def report_generation_tenant(sorted_metric_info, tenantinfo = ""):
    x = PrettyTable(["Tenant", "VMs", "VCPUs", "Memory(MB)", "Disk Space(GB)", "VM Wall Time(s)", "CPU Wall Time(s)", "Avg. CPU Usage", "Net In(GB)", "Net Out(GB)", "Cores * CPU Time", "Cores * Wall Time"])

    x.align["Accounting Group"] = "l" # Left align city names
    x.padding_width = 1 # One space between column edges and contents (default)
    y=PrettyTable(["Accounting Group", "Tenant List"])
    y.align["Accounting Group"] = "l" # Left align city names
    y.padding_width = 1 # One space between column edges and contents (default)
    by_accgroup = {}
    by_tenant = {}
    counter=0
    error_message=""
    sort_tenant_wise = sorted(sorted_metric_info, key=lambda x:x["tenant_name"])
    tenant_wise = {}
    for tenant, row_list in groupby(sort_tenant_wise, lambda x:x["tenant_name"]):
        #tenant_wise[tenant] = {}
        no_of_vms = 0
        no_of_vcpus = 0
        total_wall_time = 0
        memory_mb = 0
        disk_gb = 0
        cpu_count_start = 0
        cpu_count_end = 0
        total_cores_x_cpu_wall_time = 0
        total_cpu_wall_time = 0
        total_cores_x_wall_time = 0
        total_avg_usage_per_core = 0
        total_net_in_mb = 0
        total_net_out_mb = 0
        tenant_dict = {}
        tenant_id = ""
        vo_name = ""
        vo_name = tenant.split()[0] 
        #print tenant
        for row in row_list:
            res_id = row["resource_id"]
            cpu_info = row["cpu"]
            net_in_info = row["net_in"]
            net_out_info = row["net_out"]
            start_counter_volume = 0
            end_counter_volume = 0
            vm_wall_time_list = []
            try:
                tenant_id = row["tenant_id"]
            except:
                pass

            try:
                vcpus = int(row["vcpus"])
            except:
                vcpus = 0

            try:
                memory = int(row["memory_mb"])
            except:
                memory = 0

            try:
                disk = int(row["disk_gb"])
            except:
                disk = 0

            vm_wall_time_cpu = 0
            if cpu_info:
                try:
                    vm_wall_time_cpu = cpu_info["wall_duration"]
                    vm_wall_time_list.append(vm_wall_time_cpu)
                except:
                    vm_wall_time_list.append(vm_wall_time_cpu)

            vm_wall_time_netin = 0
            if  net_in_info:
                try:
                    vm_wall_time_netin = net_in_info["wall_duration"]
                    vm_wall_time_list.append(vm_wall_time_netin)
                except:
                    vm_wall_time_list.append(vm_wall_time_netin)

            vm_wall_time_netout = 0
            if  net_out_info:
                try:
                    vm_wall_time_netout = net_out_info["wall_duration"]
                    vm_wall_time_list.append(vm_wall_time_netout)
                except:
                    vm_wall_time_list.append(vm_wall_time_netout)

            vm_wall_time = max(vm_wall_time_cpu,vm_wall_time_netin, vm_wall_time_netout)

            if vcpus is not None and vcpus >0:
                no_of_vms += 1
                no_of_vcpus += vcpus
                memory_mb += memory
                disk_gb += disk
                total_wall_time += vm_wall_time
                total_cores_x_wall_time += (vcpus * vm_wall_time)

            if(cpu_info):
                try:
                    start_counter_volume = long(cpu_info['start_counter_volume'])
                except:
                    pass

                cpu_count_start = start_counter_volume
                try:
                    end_counter_volume = long(cpu_info['end_counter_volume'])
                except:
                    end_counter_volume=0
                cpu_count_end = end_counter_volume

                cpu_wall_time = 0
                cpu_wall_time =  float(end_counter_volume - start_counter_volume) / 1000000000.0

                total_cores_x_cpu_wall_time += (no_of_vcpus * cpu_wall_time)
                total_cpu_wall_time += long(cpu_wall_time)

                #usage_per_core = 0 # in seconds
                avg_usage_per_core = 0
                try:
                    cpu_wall_time_per_core = float(cpu_wall_time) / float(no_of_vcpus)
                    avg_usage_per_core = (cpu_wall_time_per_core / float(vm_wall_time))
                except:
                    avg_usage_per_core = 0

                total_avg_usage_per_core += avg_usage_per_core

            if(net_in_info):
                counter_volume_start = 0
                try:
                    counter_volume_start = float(net_in_info['start_counter_volume']) / 1048576.0
                except:
                    pass
                counter_volume_end = 0
                try:
                    counter_volume_end = float(net_in_info['end_counter_volume'])/ 1048576.0
                except:
                    counter_volume_end = 0
                total_net_in_mb += (counter_volume_end - counter_volume_start)
            if(net_out_info):
                counter_volume_start = 0
                try:
                    counter_volume_start = float(net_out_info['start_counter_volume']) / 1048576.0
                except:
                    counter_volume_start = 0

                counter_volume_end = 0
                try:
                    counter_volume_end = float(net_out_info['end_counter_volume']) / 1048576.0
                except:
                    counter_volume_end = 0
                total_net_out_mb += (counter_volume_end - counter_volume_start)
        tenant_wise[tenant_id] = {}
        tenant_wise[tenant_id]['tenant_id'] = tenant_id
        tenant_wise[tenant_id]['tenant_name'] = tenant
        tenant_wise[tenant_id]['vo_name'] = vo_name
        #tenant_wise[tenant_id]['no_of_tenants'] = tenantcount
        tenant_wise[tenant_id]['no_of_vms'] = no_of_vms
        tenant_wise[tenant_id]['no_of_vcpus'] = no_of_vcpus
        tenant_wise[tenant_id]['memory_mb'] = memory_mb
        tenant_wise[tenant_id]['disk_gb'] = disk_gb
        tenant_wise[tenant_id]['total_wall_time'] = total_wall_time
        tenant_wise[tenant_id]['total_cpu_wall_time'] = total_cpu_wall_time
        tenant_wise[tenant_id]['total_cores_x_cpu_wall_time'] = total_cores_x_cpu_wall_time
        tenant_wise[tenant_id]['total_avg_usage_per_core'] = float(total_avg_usage_per_core) / float(no_of_vcpus)
        tenant_wise[tenant_id]['total_net_in_mb'] = long(total_net_in_mb)
        tenant_wise[tenant_id]['total_net_out_mb'] = long(total_net_out_mb)
        tenant_wise[tenant_id]['total_cores_x_wall_time'] = total_cores_x_wall_time
        x.add_row([tenant, no_of_vms, no_of_vcpus, memory_mb, disk_gb, total_wall_time, total_cpu_wall_time, "{0:.4f}".format(tenant_wise[tenant_id]['total_avg_usage_per_core']), \
total_net_in_mb, total_net_out_mb, total_cores_x_cpu_wall_time, total_cores_x_wall_time])
    #print x
    if tenantinfo:
        jsonx = json.dumps(tenant_wise[tenantinfo], sort_keys=True,indent=4, separators=(',', ': '))
    else:
        jsonx = json.dumps(tenant_wise, sort_keys=True,indent=4, separators=(',', ': '))
    return jsonx, x


def report_generation_vo(sorted_metric_info, voinfo =  ""):
    x = PrettyTable(["VO", "Tenants","VMs", "VCPUs", "Memory(MB)", "Disk Space(GB)", "VM Wall Time(s)", "CPU Wall Time(s)", "Avg. CPU Usage", "Net In(GB)", "Net Out(GB)", "Cores * CPU Time", "Cores * Wall Time"])
    
    x.align["Accounting Group"] = "l" # Left align city names
    x.padding_width = 1 # One space between column edges and contents (default)
    y=PrettyTable(["Accounting Group", "Tenant List"])
    y.align["Accounting Group"] = "l" # Left align city names
    y.padding_width = 1 # One space between column edges and contents (default)
    by_accgroup = {}
    by_tenant = {}
    counter=0
    error_message=""
    sort_vo_wise = sorted(sorted_metric_info, key=lambda x:x["group_name"])
    #sort_tenant_wise = sorted(sorted_metric_info, key=lambda x:x["tenant_name"])
    vo_wise = {}
    #print sort_vo_wise
    #print sort_tenant_wise
    #for vo, row_list in groupby(sort_tenant_wise, lambda x:x["tenant_name"]):
    for vo, row_list in groupby(sort_vo_wise, lambda x:x["group_name"]):
        vo_wise[vo] = {}
        no_of_vms = 0
        no_of_vcpus = 0
        total_wall_time = 0
        memory_mb = 0
        disk_gb = 0
        cpu_count_start = 0
        cpu_count_end = 0
        total_cores_x_cpu_wall_time = 0
        total_cpu_wall_time = 0
        total_cores_x_wall_time = 0 
        total_avg_usage_per_core = 0
        total_net_in_mb = 0
        total_net_out_mb = 0
        tenant_dict = {}
        tenantcount = 0
        #print vo
        for row in row_list:
            res_id = row["resource_id"]
            cpu_info = row["cpu"]
            net_in_info = row["net_in"]
            net_out_info = row["net_out"]
            start_counter_volume = 0
            end_counter_volume = 0
            vm_wall_time_list = []
            try:
                tenant_name = row["tenant_name"]
                tenant_id = row["tenant_id"]
            except:
                pass
               
            if tenant_name not in  tenant_dict.keys():
                tenant_dict[tenant_name] = {}
                tenantcount += 1            

            try:
                vcpus = int(row["vcpus"])
            except:
                vcpus = 0
            
            try:
                memory = int(row["memory_mb"])
            except:
                memory = 0

            try:
                disk = int(row["disk_gb"])
            except:
                disk = 0
            
            vm_wall_time_cpu = 0
            if cpu_info:
                try:
                    vm_wall_time_cpu = cpu_info["wall_duration"]
                    vm_wall_time_list.append(vm_wall_time_cpu)
                except:
                    vm_wall_time_list.append(vm_wall_time_cpu)

            vm_wall_time_netin = 0
            if  net_in_info:
                try:
                    vm_wall_time_netin = net_in_info["wall_duration"]
                    vm_wall_time_list.append(vm_wall_time_netin)
                except:
                    vm_wall_time_list.append(vm_wall_time_netin)

            vm_wall_time_netout = 0
            if  net_out_info:
                try:
                    vm_wall_time_netout = net_out_info["wall_duration"]
                    vm_wall_time_list.append(vm_wall_time_netout)
                except:
                    vm_wall_time_list.append(vm_wall_time_netout)

            vm_wall_time = max(vm_wall_time_cpu, vm_wall_time_netin, vm_wall_time_netout)

            if vcpus is not None and vcpus >0:
                no_of_vms += 1
                no_of_vcpus += vcpus
                memory_mb += memory
                disk_gb += disk
                total_wall_time += vm_wall_time
                total_cores_x_wall_time += (vcpus * vm_wall_time)

            if(cpu_info):
                try:
                    start_counter_volume = long(cpu_info['start_counter_volume'])
                except:
                    pass
            
                cpu_count_start = start_counter_volume
                try:
                    end_counter_volume = long(cpu_info['end_counter_volume'])
                except:
                    end_counter_volume=0
                cpu_count_end = end_counter_volume
            
                cpu_wall_time = 0
                cpu_wall_time =  float(end_counter_volume - start_counter_volume) / 1000000000.0
                  
                total_cores_x_cpu_wall_time += (no_of_vcpus * cpu_wall_time)
                total_cpu_wall_time += long(cpu_wall_time)

                #usage_per_core = 0 # in seconds
                avg_usage_per_core = 0
                try:
                    cpu_wall_time_per_core = float(cpu_wall_time) / float(no_of_vcpus)
                    avg_usage_per_core = (cpu_wall_time_per_core / float(vm_wall_time))
                except:
                    avg_usage_per_core = 0

                total_avg_usage_per_core += avg_usage_per_core
 
            if(net_in_info):
                counter_volume_start = 0
                try:
                    counter_volume_start = float(net_in_info['start_counter_volume']) / 1048576.0
                except:
                    pass
                
                counter_volume_end = 0
                try:
                    counter_volume_end = float(net_in_info['end_counter_volume'])/ 1048576.0
                except:
                    counter_volume_end = 0
                total_net_in_mb += (counter_volume_end - counter_volume_start)
            if(net_out_info):
                counter_volume_start = 0
                try:
                    counter_volume_start = float(net_out_info['start_counter_volume']) / 1048576.0
                except:
                    counter_volume_start = 0
                
                counter_volume_end = 0
                try:
                    counter_volume_end = float(net_out_info['end_counter_volume']) / 1048576.0
                except:
                    counter_volume_end = 0
                total_net_out_mb += (counter_volume_end - counter_volume_start)
        vo_wise[vo]['vo_name'] = vo
        vo_wise[vo]['no_of_tenants'] = tenantcount
        vo_wise[vo]['no_of_vms'] = no_of_vms
        vo_wise[vo]['no_of_vcpus'] = no_of_vcpus
        vo_wise[vo]['memory_mb'] = memory_mb
        vo_wise[vo]['disk_gb'] = disk_gb
        vo_wise[vo]['total_wall_time'] = total_wall_time
        vo_wise[vo]['total_cpu_wall_time'] = total_cpu_wall_time
        vo_wise[vo]['total_cores_x_cpu_wall_time'] = total_cores_x_cpu_wall_time
        vo_wise[vo]['total_avg_usage_per_core'] = float(total_avg_usage_per_core) / float(no_of_vcpus)
        vo_wise[vo]['total_net_in_mb'] = long(total_net_in_mb)
        vo_wise[vo]['total_net_out_mb'] = long(total_net_out_mb)
        vo_wise[vo]['total_cores_x_wall_time'] = total_cores_x_wall_time
        x.add_row([vo, tenantcount, no_of_vms, no_of_vcpus, memory_mb, disk_gb, total_wall_time, total_cpu_wall_time, "{0:.2f}".format(vo_wise[vo]['total_avg_usage_per_core']), \
total_net_in_mb, total_net_out_mb, total_cores_x_cpu_wall_time, total_cores_x_wall_time])
    #print x
    if voinfo:
        jsonx = json.dumps(vo_wise[voinfo], sort_keys=True,indent=4, separators=(',', ': '))
    else:
        jsonx = json.dumps(vo_wise, sort_keys=True,indent=4, separators=(',', ': '))
    return jsonx, x

def tenant_wise(start_time_obj,end_time_obj, tenantinfo = ""):
    #print MYSQL_URL
    ceilo_data = get_ceilo_data_from_database(start_time_obj,end_time_obj, MYSQL_URL)
    #print "Ceilo data complete"
    input_data = input_creation(ceilo_data, start_time_obj, end_time_obj)
    #print "Input Creation Complete"
    jsonx, reports = report_generation_tenant(input_data, tenantinfo)  
    return jsonx

def vo_wise(start_time_obj,end_time_obj, voinfo = ""):
    ceilo_data = get_ceilo_data_from_database(start_time_obj,end_time_obj, MYSQL_URL)
    #print "Ceilo data complete"
    input_data = input_creation(ceilo_data, start_time_obj, end_time_obj)
    #print "Input Creation Complete"
    jsonx, reports = report_generation_vo(input_data, voinfo)
    return jsonx

def daily_resource_data(start_time_obj,end_time_obj):
    ceilo_data = get_ceilo_data_from_database(start_time_obj,end_time_obj, MYSQL_URL)
    print "Ceilo data complete"
    input_data = input_creation(ceilo_data, start_time_obj, end_time_obj)
    print "Input Creation Complete"
    #input_data = json.dumps(input_data, sort_keys=True,indent=4, separators=(',', ': '))
    #print input_data
    return input_data 
