#!/usr/bin/python
import os
import sys
sys.path.insert(0, '/usr/lib64/python2.6/site-packages/SQLAlchemy-0.7.8-py2.6-linux-x86_64.egg')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_declarative import Base, Daily_Resource_Record
from ceilodata_api import daily_resource_data
from config import MYSQL_URL
from datetime import date, datetime, timedelta
from calendar import monthrange
from time import localtime, strftime
import json

engine = create_engine(MYSQL_URL)
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
 
# Insert a Person in the person table
def update(day):
    today=date.today() - timedelta(day - 1)
    starttime = today.strftime("%Y-%m-%d") + " 00:00:00"
    endtime = today.strftime("%Y-%m-%d") + " 23:59:59"
    print starttime 
    print endtime
    start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
    #start_time = start_time_obj.strftime("%Y-%m-%d 00:00:00")
    end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
    #end_time = end_time_obj.strftime("%Y-%m-%d 23:59:59")
    data =  daily_resource_data(start_time_obj, end_time_obj)   
    for row in data:
        #print row
        cpu_counter_unit = None
        cpu_start_counter_volume = None
        cpu_end_counter_volume = None
        cpu_counter_type = None
        try:
            cpu_counter_unit = 's'
            cpu_start_counter_volume = int(float(row['cpu']['start_counter_volume'])/1000000000.0) 
            cpu_end_counter_volume = int(float(row['cpu']['end_counter_volume'])/1000000000.0)
            cpu_counter_type = row['cpu']['counter_type']
        except:
            pass
        net_in_counter_unit = None
        net_in_start_counter_volume = None
        net_in_end_counter_volume = None
        net_in_counter_type = None
        try:
            net_in_counter_unit = 'MB'
            net_in_start_counter_volume = int(float(row['net_in']['start_counter_volume'])/1048576.0)
            net_in_end_counter_volume = int(float(row['net_in']['end_counter_volume'])/1048576.0)
            net_in_counter_type = row['net_in']['counter_type']
        except:
            pass

        net_out_counter_unit = None
        net_out_start_counter_volume = None
        net_out_end_counter_volume = None
        net_out_counter_type = None

        try:
            net_out_counter_unit = 'MB'
            net_out_start_counter_volume = int(float(row['net_out']['start_counter_volume'])/1048576.0) 
            net_out_end_counter_volume = int(float(row['net_out']['end_counter_volume'])/1048576.0)
            net_out_counter_type = row['net_out']['counter_type']
        except:
            pass
        new_row = Daily_Resource_Record(user_id=row['user_id'], project_id=row['project_id'], resource_id=row['resource_id'], tenant_id=row['tenant_id'], vo_name=row['group_name'], date=today, tenant_name=row['tenant_name'], vmuuid=row['vmuuid'], vcpus=row['vcpus'], memory_mb=row['memory_mb'], disk_gb=row['disk_gb'], created_at=row['created_at'], launched_at=row['launched_at'], deleted_at=row['deleted_at'], terminated_at=row['terminated_at'], cpu_counter_unit=cpu_counter_unit, cpu_start_counter_volume=cpu_start_counter_volume,cpu_end_counter_volume=cpu_end_counter_volume ,cpu_counter_type=cpu_counter_type,  net_in_counter_unit=net_in_counter_unit, net_in_start_counter_volume=net_in_start_counter_volume, net_in_end_counter_volume=net_in_end_counter_volume, net_in_counter_type=net_in_counter_type, net_out_counter_unit=net_out_counter_unit, net_out_start_counter_volume=net_out_start_counter_volume, net_out_end_counter_volume=net_out_end_counter_volume, net_out_counter_type = net_out_counter_type)
        session.add(new_row)
    session.commit()
 
for day in range(5, 1, -1):
    update(day)

#session.remove()
