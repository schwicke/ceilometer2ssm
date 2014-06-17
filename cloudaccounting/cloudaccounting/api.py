""" SQLAlchemy Database connections
and database functions
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select
import uuid
import sqlalchemy
#from models import Resources, MetricData
#logging.basicConfig(filename='db.log')
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
#Configuration
#mysql_url = 'mysql://meterdev:meterdev@localhost:3306/meterdev'

# Global variables
engine = None
db_session = None
BASE = declarative_base()
#BASE.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will e registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    BASE.metadata.create_all(bind=engine)

def create_session(mysql_url):
    global engine, db_session
    engine = create_engine(mysql_url, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                        autoflush=False,
                                        bind=engine))

def shutdown_session(exception=None):
    db_session.remove()


def store_data(resource_info,metric_info, start_time, end_time,lgr):
    from models import Resources, MetricData,CurrentRecord
    try:
        user_id = resource_info["user_id"]
        project_id =resource_info["project_id"]
        resource_id = resource_info["resource_id"]
        hep_spec=resource_info["hep_spec"]
        tenant_id=resource_info["tenant_id"]
        tenant_name=resource_info["tenant_name"]
        node=resource_info["node"]
        host_name=resource_info["host_name"]
        vmuuid=resource_info["vmuuid"]
        image_ref_url =resource_info["image_ref_url"]
        state=resource_info["state"]
        vcpus=resource_info["vcpus"]
        memory_mb=resource_info["memory_mb"]
        disk_gb=resource_info["disk_gb"]
        created_at = resource_info["created_at"]
        launched_at = resource_info["launched_at"]
        deleted_at = resource_info["deleted_at"]
        terminated_at = resource_info["terminated_at"]
        counter_name = metric_info["counter_name"]
        source = metric_info["source"]
        counter_unit = metric_info["counter_unit"]
        counter_volume = metric_info["counter_volume"]
        counter_type = metric_info["counter_type"]
        sample_time = metric_info["sample_time"]


        cpu_counter_volume=None
        net_in_counter_volume=None
        net_out_counter_volume=None

        cpu_counter_type=None
        net_in_counter_type=None
        net_out_counter_type=None

        cpu_counter_source=None
        net_in_counter_source=None
        net_out_counter_source=None

        cpu_counter_sample_time=None
        net_in_counter_sample_time=None
        net_out_counter_sample_time=None

        cpu_counter_unit=None
        net_in_counter_unit=None
        net_out_counter_unit=None

        # check if resouce info exists
        res_resources = db_session.query(Resources).filter(Resources.resource_id == resource_id).first()

        if counter_name=="cpu":
            cpu_counter_source=source
            cpu_counter_type=counter_type
            cpu_counter_unit=counter_unit
            cpu_counter_volume=counter_volume
            cpu_counter_sample_time=sample_time
        elif counter_name=="network.incoming.bytes":
            net_in_counter_source=source
            net_in_counter_type=counter_type
            net_in_counter_unit=counter_unit
            net_in_counter_volume=counter_volume
            net_in_counter_sample_time=sample_time
        else:
            net_out_counter_source=source
            net_out_counter_type=counter_type
            net_out_counter_unit=counter_unit
            net_out_counter_volume=counter_volume
            net_out_counter_sample_time=sample_time

        try:
            if res_resources is not None:
                # If record exists, update the following four fields, if available
                if user_id is not None and user_id != "":
                    if res_resources.user_id is None:
                        res_resources.user_id = user_id
                if project_id is not None and project_id != "":
                    if res_resources.project_id is None:
                        res_resources.project_id =project_id
                if vcpus is not None and vcpus != "":
                    res_resources.vcpus = vcpus
                if hep_spec is not None and hep_spec != "":
                    if res_resources.hep_spec is None:
                        res_resources.hep_spec =hep_spec
                if image_ref_url is not None and image_ref_url != "":
                    if res_resources.image_ref_url is None:
                        res_resources.image_ref_url = image_ref_url
                if state is not None and state != "":
                    res_resources.state = state
                if node is not None and node != "":
                    if res_resources.node is None:
                        res_resources.node = node
                if memory_mb is not None and memory_mb != "":
                    res_resources.memory_mb = memory_mb
                if disk_gb is not None and disk_gb != "":
                    res_resources.disk_gb = disk_gb

                if created_at is not None and created_at != "":
                    res_resources.created_at = created_at
                if launched_at is not None and launched_at != "":
                    res_resources.launched_at = launched_at
                if deleted_at is not None and deleted_at != "":
                    res_resources.deleted_at = deleted_at
                if terminated_at is not None and terminated_at != "":
                    res_resources.terminated_at = terminated_at
                    res_resources.deleted = True
                db_session.commit()

            else:
                # Generate a new UUID and add new record
                new_resource = Resources(user_id, project_id, resource_id,tenant_id,tenant_name,
                                           node,host_name,vmuuid,image_ref_url,state, vcpus,memory_mb,
                                           disk_gb,False,hep_spec, created_at, launched_at, deleted_at,
                                           terminated_at)
                db_session.add(new_resource)
                db_session.commit()
        except IntegrityError,message:
            lgr.info('DB Error Occured %s', message[0])
            db_session.rollback()
        try:
            group_name="default"
            try:
                if("-" in tenant_name):
                    group_name=tenant_name.split("-")[0]
                group_name=tenant_name.split()[0]
            except:
                logging.info("Group name is default")
            wall_duration=0
            res_current_record=None
            res_current_record = db_session.query(CurrentRecord).filter(CurrentRecord.resource_id == resource_id).first()
            if res_current_record is not None:
                # If record exists, update the following four fields, if available
                if user_id is not None and user_id != "":
                    if res_current_record.user_id is None:
                        res_current_record.user_id = user_id
                if project_id is not None and project_id != "":
                    if res_current_record.project_id is None:
                        res_current_record.project_id = project_id
                if vcpus is not None and vcpus != "":
                    res_current_record.vcpus = vcpus
                if hep_spec is not None and hep_spec != "":
                    if  res_current_record.hep_spec is None:
                        res_current_record.hep_spec = hep_spec
                if image_ref_url is not None and image_ref_url != "":
                    if res_current_record.image_ref_url is None:
                        res_current_record.image_ref_url = image_ref_url
                if memory_mb is not None and memory_mb != "":
                    res_current_record.memory_mb = memory_mb
                if disk_gb is not None and disk_gb != "":
                    res_current_record.disk_gb = disk_gb
                if node is not None and node != "":
                    if res_current_record.node is None:
                        res_current_record.node = node

                if state is not None and state != "":
                    res_current_record.state = state

                if created_at is not None and created_at != "":
                    res_current_record.created_at = created_at
                if launched_at is not None and launched_at != "":
                    res_current_record.launched_at = launched_at
                if deleted_at is not None and deleted_at != "":
                    res_current_record.deleted_at = deleted_at
                if terminated_at is not None and terminated_at != "":
                    res_current_record.terminated_at = terminated_at
                    res_current_record.deleted = True

                if cpu_counter_volume is not None and cpu_counter_volume != "":
                    if (res_current_record.cpu_counter_volume is not None):
                        try:
                            tmp=float(res_current_record.cpu_counter_volume)
                            counter_volume_in_db=long(tmp)
                            counter_volume_poll=long(cpu_counter_volume)
                            if(counter_volume_poll>counter_volume_in_db):
                                res_current_record.cpu_counter_volume = cpu_counter_volume
                                if cpu_counter_sample_time is not None and cpu_counter_sample_time != "":
                                    res_current_record.cpu_counter_sample_time = cpu_counter_sample_time
                        except:
                             res_current_record.cpu_counter_volume = cpu_counter_volume
                             if cpu_counter_sample_time is not None and cpu_counter_sample_time != "":
                                res_current_record.cpu_counter_sample_time = cpu_counter_sample_time
                    else:
                        res_current_record.cpu_counter_volume = cpu_counter_volume
                        if cpu_counter_sample_time is not None and cpu_counter_sample_time != "":
                            res_current_record.cpu_counter_sample_time = cpu_counter_sample_time
                if cpu_counter_source is not None and cpu_counter_source != "":
                    res_current_record.cpu_counter_source =cpu_counter_source
                if cpu_counter_type is not None and cpu_counter_type != "":
                    res_current_record.cpu_counter_type = cpu_counter_type
                if cpu_counter_unit is not None and cpu_counter_unit != "":
                    res_current_record.cpu_counter_unit = cpu_counter_unit


                if net_in_counter_volume is not None and net_in_counter_volume != "":
                    if res_current_record.net_in_counter_volume is not None:
                        try:
                            tmp=float(res_current_record.net_in_counter_volume)
                            counter_volume_in_db=long(tmp)
                            counter_volume_poll=long(net_in_counter_volume)
                            if(counter_volume_poll>counter_volume_in_db):
                                res_current_record.net_in_counter_volume = net_in_counter_volume
                                if net_in_counter_sample_time is not None and net_in_counter_sample_time != "":
                                    res_current_record.net_in_counter_sample_time = net_in_counter_sample_time
                        except:
                             res_current_record.net_in_counter_volume = net_in_counter_volume
                             if net_in_counter_sample_time is not None and net_in_counter_sample_time != "":
                                res_current_record.net_in_counter_sample_time = net_in_counter_sample_time
                    else:
                        res_current_record.net_in_counter_volume = net_in_counter_volume
                        if net_in_counter_sample_time is not None and net_in_counter_sample_time != "":
                            res_current_record.net_in_counter_sample_time = net_in_counter_sample_time

                if net_in_counter_type is not None and net_in_counter_type != "":
                    res_current_record.net_in_counter_type = net_in_counter_type
                if net_in_counter_unit is not None and net_in_counter_unit != "":
                    res_current_record.net_in_counter_unit = net_in_counter_unit
                if net_in_counter_source is not None and net_in_counter_source != "":
                    res_current_record.net_in_counter_source = net_in_counter_source

                if net_out_counter_volume is not None and net_out_counter_volume != "":
                    if res_current_record.net_out_counter_volume is not None:
                        try:
                            tmp=float(res_current_record.net_out_counter_volume)
                            counter_volume_in_db=long(tmp)
                            counter_volume_poll=long(net_out_counter_volume)
                            if(counter_volume_poll>counter_volume_in_db):
                                res_current_record.net_out_counter_volume = net_out_counter_volume
                                if net_out_counter_sample_time is not None and net_out_counter_sample_time != "":
                                    res_current_record.net_out_counter_sample_time = net_out_counter_sample_time
                        except:
                            res_current_record.net_out_counter_volume = net_out_counter_volume
                            if net_out_counter_sample_time is not None and net_out_counter_sample_time != "":
                                    res_current_record.net_out_counter_sample_time = net_out_counter_sample_time
                    else:
                        res_current_record.net_out_counter_volume = net_out_counter_volume
                        if net_out_counter_sample_time is not None and net_out_counter_sample_time != "":
                                    res_current_record.net_out_counter_sample_time = net_out_counter_sample_time


                if net_out_counter_type is not None and net_out_counter_type != "":
                    res_current_record.net_out_counter_type = net_out_counter_type
                if net_out_counter_unit is not None and net_out_counter_unit != "":
                    res_current_record.net_out_counter_unit = net_out_counter_unit
                if net_out_counter_source is not None and net_out_counter_source != "":
                    res_current_record.net_out_counter_source = net_out_counter_source

                db_session.commit()

            else:
                # Generate a new UUID and add new record
                new_record=CurrentRecord(user_id, project_id, resource_id,tenant_id,group_name,tenant_name,
                                           node,host_name,vmuuid,image_ref_url,state, vcpus,memory_mb,
                                           disk_gb,False,hep_spec, created_at, launched_at, deleted_at,
                                           terminated_at,cpu_counter_volume, net_in_counter_volume,
                                           net_out_counter_volume,cpu_counter_type,net_in_counter_type,
                                           net_out_counter_type,cpu_counter_source,net_in_counter_source,
                                           net_out_counter_source,cpu_counter_sample_time,net_in_counter_sample_time,
                                           net_out_counter_sample_time,cpu_counter_unit,net_in_counter_unit,
                                           net_out_counter_unit)
                db_session.add(new_record)
                db_session.commit()
        except IntegrityError,message:
            lgr.error('DB Error Occured %s', message[0])
            db_session.rollback()


        try:
            new_id = uuid.uuid4()
            r_id = resource_id
            new_metric_data = MetricData(new_id, r_id, counter_name, source,
                                  counter_unit, counter_volume, counter_type,
                                  start_time, end_time, sample_time)
            db_session.add(new_metric_data)
            db_session.commit()
        except IntegrityError, message:
            db_session.rollback()
            lgr.error('DB Error Occured %s', message[0])
        db_session.flush()
    except:
        lgr.debug("Error Occured while storing the data in the database")
# retrieval of resource data

def get_resource_info():
    from models import Resources, MetricData
    result=[]
    try:
        rows=db_session.query(Resources).all()
        for row in rows:
          row=row.__dict__
          result.append(row)
    except:
        print "Error occured while retrieving the resource data"
    return result
# retrieval of  metric data

def get_metric_info(start_time,end_time):
    result=[]
    from models import MetricData
    try:
        rows=db_session.query(MetricData).filter(MetricData.sample_time >=start_time).\
         filter(MetricData.sample_time <=end_time).all()
        for row in rows:
            row=row.__dict__
            result.append(row)
    except:
        print "Error occured while retrieving the metric information"
    return result
# retrieval of current resource record

def get_current_resource_record():
    from models import CurrentRecord
    result=[]
    try:
        rows=db_session.query(CurrentRecord).all()
        for row in rows:
          row=row.__dict__
          result.append(row)
    except:
        print "Error occured while retrieving the current record"
    return result





