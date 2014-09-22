#!/usr/bin/python
import os
import sys
sys.path.insert(0, '/usr/lib64/python2.6/site-packages/SQLAlchemy-0.7.8-py2.6-linux-x86_64.egg')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_declarative import Base, Daily_Resource_Record
from ceilodata_api import daily_resource_data
#from config import MYSQL_URL
from datetime import date, datetime, timedelta
from calendar import monthrange
from time import localtime, strftime
import json
from cloudaccounting import hwdbquery  # queries hwdb database
from cloudaccounting import landbquery

def read_config():
    filename="/etc/ceilodata.conf"
    try:
        f = open(filename,"r")
        try:
            result= json.loads(f.read())
            f.close
            return result
        except:
            print >> sys.stderr, 'ERROR: Cannot parse configuration file ' + filename
            exit(1)
    except IOError:
        print >> sys.stderr, 'ERROR: Cannot open configuration file ' + filename
        exit(1)


config = read_config()
try:
    secrets = config["secrets"]
    try:
        landb_user_name=secrets["landb_user_name"]
        landb_password=secrets["landb_password"]
    except KeyError:
        print >>sys.stderr,"ERROR:LAN_DB user name and password not set"
except:
    print >> sys.stderr, "ERROR: No secrets defined in the configuration file"

try:
    database_info=config["database"]
    try:
        mysql_user_name=database_info["user"]
        mysql_password=database_info["password"]
        database_name=database_info["database_name"]
        mysql_url="mysql://"+mysql_user_name+":"+mysql_password+"@localhost:3306/"+database_name
    except:
        print >> sys.stderr, "ERROR: My sql user name and password has not been properly set"

except:
     print >> sys.stderr, "ERROR: No database info in the file"

engine = create_engine(mysql_url)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# querying the hwdb database
# serial number hep-spec value combination data is saved

def getHepSpecData():
    hep_spec_data_id = {}
    hep_spec_data_host_name = {}
 
    hwData = hwdbquery.getDataFromHwDb()
    decoded = json.loads(hwData)
    for server in decoded["rows"]:
        id = server['id'];
        host_name = server['key'];
        values = server['value']
        host_hs06 = ''
        host_lcores = ''
        host_pcores = ''
        try:
            host_name = server['key'];
        except:
            host_name = ""
        try:
            host_hs06 = values['HEP-SPEC06']
        except:
            host_hs06 = '8'
        try:
            host_lcores = values['Logical Cores']
        except:
            print >> sys.stderr, "ERROR: Populate Daily Resource Table: No logical core value for the host"
        try:
            host_pcores = values['Physical Cores']
        except:
            print >> sys.stderr, "ERROR: Populate Daily Resource Table: No physical core value for the host"
        
        hep_spec_data_host_name[host_name] = {}       
        hep_spec_data_host_name[host_name]["host_hs06"] = host_hs06
        hep_spec_data_host_name[host_name]["host_lcores"] = host_lcores
        hep_spec_data_host_name[host_name]["host_pcores"] = host_pcores

        hep_spec_data_id[id]= {}
        hep_spec_data_id[id]["host_name"] = host_name
        hep_spec_data_id[id]["host_hs06"] = host_hs06
        hep_spec_data_id[id]["host_lcores"] = host_lcores
        hep_spec_data_id[id]["host_pcores"] = host_pcores
    return hep_spec_data_id, hep_spec_data_host_name

 
# Insert a Person in the person table
def update_resource_record():
    hep_spec_data_id_wise,hep_spec_data_host_name_wise = getHepSpecData()
    #print hep_spec_data_host_name_wise
    today=date.today() - timedelta(1)
    starttime = today.strftime("%Y-%m-%d") + " 00:00:00"
    endtime = today.strftime("%Y-%m-%d") + " 23:59:59"
    print starttime 
    print endtime
    start_time_obj = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
    end_time_obj = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
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

        host_name = None
        host_hs06 = None
        host_lcores = None
        host_pcores = None

        res_record = None
        res_record = session.query(Daily_Resource_Record).filter(Daily_Resource_Record.resource_id == row['resource_id'], Daily_Resource_Record.date==today).first()
        if res_record is not None:
            host_name = res_record.host_name
            host_hs06 = res_record.host_hs06
            host_lcores = res_record.host_lcores
            host_pcores = res_record.host_pcores
        else:
            host_name = row["node"]
            if host_name is not None and host_name!="" and host_name!="None":
                hostname=host_name.split(".")[0]
                serial_number = ""
                try:
                    serial_number = landbquery.getSerialNumber(landb_user_name,landb_password,hostname)
                    if serial_number is not None:
                        serial_number=serial_number.replace("-"," ",1)
                        try:
                            host_lcores=hep_spec_data_id_wise[serial_number]['host_lcores']
                            host_pcores=hep_spec_data_id_wise[serial_number]['host_pcores']
                            try:
                                host_hs06 = hep_spec_data_id_wise[serial_number]['host_hs06']
                            except KeyError:
                                pass
                        except:
                            host_hs06 = None
                            host_lcores = None
                            host_pcores = None
                            print >> sys.stderr, "ERROR: Populate Daily Resource Table: Unable to get no. of pcores or lcores for a host: " + host_name + " (serial number: "+ serial_number +")"
                    else:
                        try:
                            host_lcores=hep_spec_data_host_name_wise[host_name]['host_lcores']
                            host_pcores=hep_spec_data_host_name_wise[host_name]['host_pcores']
                            try:
                                host_hs06 = hep_spec_data_host_name_wise[host_name]['host_hs06']
                            except KeyError:
                                pass
                        #print "NO serial number for host: %s, but got by host name\n" % host_name
                        except:
                            host_hs06 = None
                            host_lcores = None
                            host_pcores = None
                            print >> sys.stderr, "ERROR: Populate Daily Resource Table: Unable to get no. of pcores or lcores for a host(name:"+ host_name +")"
                except:
                    print >> sys.stderr, "ERROR: Populate Daily Resource Table: Error occured while determining serial number for host"
            else:
                pass
        res_current_record = None
        res_current_record = session.query(Daily_Resource_Record).filter(Daily_Resource_Record.resource_id == row['resource_id'], Daily_Resource_Record.date==today).first()
        if res_current_record is not None:
            res_current_record.tenant_id = row['tenant_id']
            res_current_record.vo_name = row['group_name']
            res_current_record.tenant_name = row['tenant_name']
            res_current_record.vmuuid = row['vmuuid']
            res_current_record.vcpus = row['vcpus']
            res_current_record.memory_mb = row['memory_mb']
            res_current_record.disk_gb = row['disk_gb']
            res_current_record.created_at = row['created_at']
            res_current_record.launched_at = row['launched_at']
            res_current_record.deleted_at = row['deleted_at']
            res_current_record.terminated_at = row['terminated_at']
            res_current_record.host_name = host_name
            res_current_record.host_hs06 = host_hs06
            res_current_record.host_lcores = host_lcores
            res_current_record.host_pcores = host_pcores
            
            res_current_record.cpu_counter_unit = cpu_counter_unit 
            res_current_record.cpu_start_counter_volume = cpu_start_counter_volume
            res_current_record.cpu_end_counter_volume = cpu_end_counter_volume
            res_current_record.cpu_counter_type = cpu_counter_type
            
            res_current_record.net_in_counter_unit = net_in_counter_unit
            res_current_record.net_in_start_counter_volume = net_in_start_counter_volume
            res_current_record.net_in_end_counter_volume = net_in_end_counter_volume
            res_current_record.net_in_counter_type = net_in_counter_type
    
            res_current_record.net_out_counter_unit = net_out_counter_unit
            res_current_record.net_out_start_counter_volume = net_out_start_counter_volume
            res_current_record.net_out_end_counter_volume = net_out_end_counter_volume
            res_current_record.net_out_counter_type = net_out_counter_type

            session.commit()
        else:
            new_row = Daily_Resource_Record(user_id=row['user_id'], project_id=row['project_id'], resource_id=row['resource_id'], tenant_id=row['tenant_id'], vo_name=row['group_name'], date=today, tenant_name=row['tenant_name'], vmuuid=row['vmuuid'], vcpus=row['vcpus'], memory_mb=row['memory_mb'], disk_gb=row['disk_gb'], created_at=row['created_at'], launched_at=row['launched_at'], deleted_at=row['deleted_at'], terminated_at=row['terminated_at'], cpu_counter_unit=cpu_counter_unit, cpu_start_counter_volume=cpu_start_counter_volume,cpu_end_counter_volume=cpu_end_counter_volume ,cpu_counter_type=cpu_counter_type,  net_in_counter_unit=net_in_counter_unit, net_in_start_counter_volume=net_in_start_counter_volume, net_in_end_counter_volume=net_in_end_counter_volume, net_in_counter_type=net_in_counter_type, net_out_counter_unit=net_out_counter_unit, net_out_start_counter_volume=net_out_start_counter_volume, net_out_end_counter_volume=net_out_end_counter_volume, net_out_counter_type = net_out_counter_type, host_name=host_name, host_hs06=host_hs06, host_lcores=host_lcores, host_pcores=host_pcores)
            session.add(new_row)
            session.commit()

#for day in range(130, 1, -1):
update_resource_record()

