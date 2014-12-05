#!/usr/bin/python
import sys
sys.path.insert(0, '/usr/lib64/python2.6/site-packages/SQLAlchemy-0.7.8-py2.6-linux-x86_64.egg')
import json
import re
import os
import argparse
from itertools import groupby
from datetime import date, datetime, timedelta
from calendar import monthrange
from time import localtime, strftime
#from cloudaccounting import api as db_api
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from db_declarative import Base, Daily_Resource_Record
import logging
from prettytable import PrettyTable
from config import read_config


# getting the sample volume and sampling time of the first sample
config=read_config()
dbuser=config['database']['user']
dbpwd=config['database']['password']
database_name=config['database']['database_name']
MYSQL_URL = "mysql://"+dbuser+":"+dbpwd+"@localhost:3306/cloudaccounting"    

def db_init():
    engine = create_engine(MYSQL_URL)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

# getting the sample volume and sampling time of the first sample

def get_start_sample_info(row_list, key1, key2, key3):
    start_sample_value_key1= row_list[0][key1] 
    start_sample_value_key2= row_list[0][key2]
    start_sample_value_key3= row_list[0][key3]
    for row in row_list:
        sample_value_key1=row[key1]
        sample_value_key2=row[key2]
        sample_value_key3=row[key3]
        if not start_sample_value_key1:
            start_sample_value_key1 = row[key1]
        if not start_sample_value_key2:
            start_sample_value_key2 = row[key2]
        if not start_sample_value_key3:
            start_sample_value_key3 = row[key3]    
        if sample_value_key1:
            if(int(sample_value_key1) < int(start_sample_value_key1)):
                start_sample_value_key1 = sample_value_key1
        if sample_value_key2:
            if(int(sample_value_key2) < int(start_sample_value_key2)):
                start_sample_value_key2 = sample_value_key2
        if sample_value_key3:
            if(int(sample_value_key3) < int(start_sample_value_key3)):
                start_sample_value_key3 = sample_value_key3
    if not start_sample_value_key1:
        start_sample_value_key1 = 0
    if not start_sample_value_key2:
        start_sample_value_key2 = 0
    if not start_sample_value_key3:
        start_sample_value_key3 = 0    
    return int(start_sample_value_key1),int(start_sample_value_key2),int(start_sample_value_key3)

# getting the sample volume and sampling time of the last sample

def get_end_sample_info(row_list, key1, key2, key3):
    end_sample_value_key1 = row_list[0][key1]
    end_sample_value_key2 = row_list[0][key2]
    end_sample_value_key3 = row_list[0][key3]
    for row in row_list:
            sample_value_key1 = row[key1]
            sample_value_key2 = row[key2]
            sample_value_key3 = row[key3]
            if not end_sample_value_key1:
                end_sample_value_key1 = sample_value_key1
            if not end_sample_value_key2:
                end_sample_value_key2 = sample_value_key2
            if not end_sample_value_key3:
                end_sample_value_key3 = sample_value_key3

            if sample_value_key1:
                if(int(sample_value_key1) > int(end_sample_value_key1)):
                    end_sample_value_key1 = sample_value_key1
            if sample_value_key2:
                if(int(sample_value_key2) > int(end_sample_value_key2)):
                    end_sample_value_key2 = sample_value_key2
            if sample_value_key3:
                if(int(sample_value_key3) > int(end_sample_value_key3)):
                    end_sample_value_key3 = sample_value_key3
    if not end_sample_value_key1:
        end_sample_value_key1 = 0
    if not end_sample_value_key2:
        end_sample_value_key2 = 0
    if not end_sample_value_key3:
        end_sample_value_key3 = 0
    return end_sample_value_key1, end_sample_value_key2, end_sample_value_key3


# getting the ceilometer data stored the database

def get_vo_data(start_time, end_time, vo_info):
    #print "Get VO Data"
    logging.info("Contacting the database")
    session = db_init()
    #db_api.create_session(mysql_url) # starts the database session
    resource_data={}
    sorted_resource_data={}
    sorted_metric_data={}
    vos = session.query(distinct(Daily_Resource_Record.vo_name)).filter(Daily_Resource_Record.date>=start_time,Daily_Resource_Record.date<=end_time).all()
    data = {}
    for vo in vos:
        voname = vo[0]
        my_query = session.query(Daily_Resource_Record).filter(Daily_Resource_Record.date>=start_time,Daily_Resource_Record.date<=end_time,Daily_Resource_Record.vo_name==voname)
        data[voname] = [u.__dict__ for u in my_query.all()]
        data[voname] = sorted(data[voname], key=lambda x:x['resource_id'])
    #print data[vos[0][0]]
    #print "db accessed"
    res_data = {}
    for vo in vos:
        tenant_list = []
        voname = vo[0]
        res_data[voname] = {}
        res_data[voname]['no_of_vms'] = 0
        res_data[voname]['no_of_vcpus'] = 0
        res_data[voname]['no_of_tenants'] = 0
        res_data[voname]['memory_mb'] = 0
        res_data[voname]['disk_gb'] = 0
        res_data[voname]['net_in_mb'] = 0
        res_data[voname]['net_out_mb'] = 0
        res_data[voname]['total_cpu_secs'] = 0
        res_data[voname]['total_hs06_cpu_secs'] = 0
        res_data[voname]['total_per_cpu_secs'] = 0
        res_data[voname]['total_hs06_per_cpu_secs'] = 0
        res_data[voname]['total_wall_secs'] = 0
        res_data[voname]['total_hs06_wall_secs'] = 0
        res_data[voname]['tenants_list'] = []
        for rid, row_group in groupby(data[voname], lambda x:x['resource_id']):
             group_list = list(row_group)
             if group_list[0]['tenant_name'] not in tenant_list:
                tenant_list.append(group_list[0]['tenant_name'])
                tenant = {}
                tenant['name'] = group_list[0]['tenant_name']
                tenant['id'] = group_list[0]['tenant_id']
                res_data[voname]['tenants_list'].append(tenant)
                res_data[voname]['no_of_tenants'] += 1 
	     try:
                 hs_06 =  group_list[0]['host_hs06']
                 lcores = group_list[0]['host_lcores']
                 normalization_factor = float(hs_06)/float(lcores)
             except:
                 normalization_factor = 8.0
             wall_duration = 0
             terminated_time = group_list[0]["terminated_at"]
             launched_time = group_list[0]["launched_at"]
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
                 diff = end_time - start_time
                 wall_duration = diff.days * 86400 + diff.seconds
             res_data[voname]['total_wall_secs'] += wall_duration
             res_data[voname]['no_of_vms'] += 1
             vcpus = 0
             try:
                 vcpus = int(group_list[0]['vcpus'])
                 res_data[voname]['no_of_vcpus'] += vcpus                
             except:
                 pass
             try:
                 res_data[voname]['memory_mb'] += int(group_list[0]['memory_mb'])
             except:
                 pass
             try:
                 res_data[voname]['disk_gb'] += int(group_list[0]['disk_gb'])
             except:
                 pass
             cpu_start_counter_volume, net_in_start_counter_volume, net_out_start_counter_volume = get_start_sample_info(group_list, 'cpu_start_counter_volume', 'net_in_start_counter_volume','net_out_start_counter_volume')
             cpu_end_counter_volume, net_in_end_counter_volume, net_out_end_counter_volume = get_end_sample_info(group_list, 'cpu_end_counter_volume', 'net_in_end_counter_volume','net_out_end_counter_volume')
             diff_cpu = 0
             diff_cpu = cpu_end_counter_volume - cpu_start_counter_volume
             res_data[voname]['total_cpu_secs'] += diff_cpu 
             try:
                 total_per_cpu_secs = long(float(diff_cpu) / float(vcpus))
             except:
                 total_per_cpu_secs = 0
             res_data[voname]['total_per_cpu_secs'] += total_per_cpu_secs
             if normalization_factor is not None:
                 res_data[voname]['total_hs06_cpu_secs'] += long(diff_cpu * normalization_factor)
                 res_data[voname]['total_hs06_per_cpu_secs'] += long(total_per_cpu_secs * normalization_factor)
                 res_data[voname]['total_hs06_wall_secs'] += long(wall_duration * normalization_factor)
             res_data[voname]['net_in_mb'] += net_in_end_counter_volume - net_in_start_counter_volume
             res_data[voname]['net_out_mb'] += net_out_end_counter_volume - net_out_start_counter_volume
        #print voname
        #print res_data[voname]
        #print "Result Back"
    jsonx = {}
    if vo_info:
        jsonx = json.dumps(res_data[vo_info], sort_keys=True,indent=4, separators=(',', ': '))
    else:
        jsonx = json.dumps(res_data, sort_keys=True,indent=4, separators=(',', ': '))
    '''if not jsonx:
        jsonx = {}
        jsonx = json.dumps(jsonx)'''
    return jsonx

def get_tenant_data(start_time, end_time, tenant_info):
    logging.info("Contacting the database")
    session = db_init()
    #db_api.create_session(mysql_url) # starts the database session
    resource_data={}
    sorted_resource_data={}
    sorted_metric_data={}
    tenants = session.query(distinct(Daily_Resource_Record.tenant_id)).filter(Daily_Resource_Record.date>=start_time,Daily_Resource_Record.date<=end_time).all()
    data = {}
    for tenant in tenants:
        tenantid = tenant[0]
        my_query = session.query(Daily_Resource_Record).filter(Daily_Resource_Record.date>=start_time,Daily_Resource_Record.date<=end_time,Daily_Resource_Record.tenant_id==tenantid)
        data[tenantid] = [u.__dict__ for u in my_query.all()]
        data[tenantid] = sorted(data[tenantid], key=lambda x:x['resource_id'])
    #print data[vos[0][0]]
    res_data = {}
    for tenant in tenants:
        tenantid = tenant[0]
        res_data[tenantid] = {}
        res_data[tenantid]['tenant_name'] = ""
        res_data[tenantid]['no_of_vms'] = 0
        res_data[tenantid]['no_of_vcpus'] = 0
        res_data[tenantid]['memory_mb'] = 0
        res_data[tenantid]['disk_gb'] = 0
        res_data[tenantid]['net_in_mb'] = 0
        res_data[tenantid]['net_out_mb'] = 0
        res_data[tenantid]['total_cpu_secs'] = 0
        res_data[tenantid]['total_hs06_cpu_secs'] = 0
        res_data[tenantid]['total_per_cpu_secs'] = 0
        res_data[tenantid]['total_hs06_per_cpu_secs'] = 0
        res_data[tenantid]['total_wall_secs'] = 0
        res_data[tenantid]['total_hs06_wall_secs'] = 0
        for rid, row_group in groupby(data[tenantid], lambda x:x['resource_id']):
             group_list = list(row_group)
             res_data[tenantid]['tenant_name'] = group_list[0]["tenant_name"]
             try:
                 hs_06 =  group_list[0]['host_hs06']
                 lcores = group_list[0]['host_lcores']
                 normalization_factor = float(hs_06)/float(lcores)
                 #print normalization_factor
             except:
                 normalization_factor = 8.0
             wall_duration = 0
             terminated_time = group_list[0]["terminated_at"]
             launched_time = group_list[0]["launched_at"]
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
                 diff = end_time - start_time
                 wall_duration = diff.days * 86400 + diff.seconds
             res_data[tenantid]['total_wall_secs'] += wall_duration
             res_data[tenantid]['no_of_vms'] += 1
             vcpus  = 0
              
             try:
                 vcpus  = int(group_list[0]['vcpus'])
                 res_data[tenantid]['no_of_vcpus'] += vcpus
                 group_list[0]
             except:
                pass
             try:
                 res_data[tenantid]['memory_mb'] += int(group_list[0]['memory_mb'])
             except:
                 pass
             try:
                 res_data[tenantid]['disk_gb'] += int(group_list[0]['disk_gb'])
             except:
                 pass
             cpu_start_counter_volume, net_in_start_counter_volume, net_out_start_counter_volume = get_start_sample_info(group_list, 'cpu_start_counter_volume', 'net_in_start_counter_volume','net_out_start_counter_volume')
             cpu_end_counter_volume, net_in_end_counter_volume, net_out_end_counter_volume = get_end_sample_info(group_list, 'cpu_end_counter_volume', 'net_in_end_counter_volume','net_out_end_counter_volume')
             diff_cpu = 0
             diff_cpu  = cpu_end_counter_volume - cpu_start_counter_volume
             res_data[tenantid]['total_cpu_secs'] += diff_cpu
             try:
                 total_per_cpu_secs = long(float(diff_cpu)/ float(vcpus))
             except:
                 total_per_cpu_secs = 0
             res_data[tenantid]['total_per_cpu_secs'] += total_per_cpu_secs
             if normalization_factor is not None:
                 res_data[tenantid]['total_hs06_cpu_secs'] += long(diff_cpu * normalization_factor)
                 res_data[tenantid]['total_hs06_per_cpu_secs'] += long(total_per_cpu_secs * normalization_factor)
                 res_data[tenantid]['total_hs06_wall_secs'] += long(wall_duration * normalization_factor)
             res_data[tenantid]['net_in_mb'] += net_in_end_counter_volume - net_in_start_counter_volume
             res_data[tenantid]['net_out_mb'] += net_out_end_counter_volume - net_out_start_counter_volume
        #print tenantid
        #print res_data[tenantid]
    jsonx = {}
    if tenant_info:
        jsonx = json.dumps(res_data[tenant_info], sort_keys=True,indent=4, separators=(',', ': '))
    else:
        jsonx = json.dumps(res_data, sort_keys=True,indent=4, separators=(',', ': '))
    return jsonx

def daily_resource_tenant_wise(start_time_obj,end_time_obj, tenantinfo = ""):
    jsonx = {}
    jsonx = json.dumps(jsonx)
    jsonx = get_tenant_data(start_time_obj,end_time_obj, tenantinfo)
    return jsonx

def daily_resource_vo_wise(start_time_obj,end_time_obj, voinfo = ""):
    jsonx = {}
    jsonx = json.dumps(jsonx)
    #mysql_url = connect_db() 
    jsonx = get_vo_data(start_time_obj,end_time_obj, voinfo)
    return jsonx

'''starttime = "2014-05-14 00:00:00"
endtime = "2014-06-11 23:59:59"

start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")

print daily_resource_vo_wise(start_time_obj, end_time_obj)'''
