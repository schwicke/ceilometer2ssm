#!/usr/bin/python
import os
import sys
sys.path.insert(0, '/usr/lib64/python2.6/site-packages/SQLAlchemy-0.7.8-py2.6-linux-x86_64.egg')
from sqlalchemy import Date, DateTime, Float, Column, ForeignKey, Integer, String, schema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from config import MYSQL_URL 
Base = declarative_base()
 
class Daily_Resource_Record(Base):
    #Represents a resource in OpenStack.

    __tablename__ = 'daily_resource_record'
    __table_args__ = (
        schema.UniqueConstraint("resource_id", "date",
                        name="uniq_daily_resource_record0resource_id00resource_id"),
    )
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    project_id = Column(String(255))
    resource_id = Column(String(255), nullable=False)
    tenant_id=Column(String(255))
    vo_name=Column(String(225))
    date =  Column(Date, nullable=False)
    tenant_name=Column(String(255))
    vmuuid=Column(String(255))
    vcpus=Column(Integer)
    memory_mb=Column(Integer)
    disk_gb=Column(Integer)
    created_at = Column(DateTime)
    launched_at = Column(DateTime)
    deleted_at = Column(DateTime)
    terminated_at = Column(DateTime)
    host_name = Column(String(255))
    host_hs06 = Column(String(32))
    host_lcores = Column(String(32))
    host_pcores = Column(String(32))

    #cpu_counter_source = Column(String(64))
    cpu_counter_unit = Column(String(32))
    cpu_start_counter_volume = Column(Integer, nullable=True)
    cpu_end_counter_volume = Column(Integer, nullable=True)
    cpu_counter_type = Column(String(32))
    #cpu_counter_sample_time = Column(DateTime)
    
    #net_in_counter_source = Column(String(64))
    net_in_counter_unit = Column(String(32))
    net_in_start_counter_volume = Column(Integer, nullable=True)
    net_in_end_counter_volume = Column(Integer, nullable=True)
    net_in_counter_type = Column(String(32))
    #net_in_counter_sample_time = Column(DateTime)

    #net_out_counter_source = Column(String(64))
    net_out_counter_unit = Column(String(32))
    net_out_start_counter_volume = Column(Integer, nullable=True)
    net_out_end_counter_volume = Column(Integer, nullable=True)
    net_out_counter_type = Column(String(32))
    #net_out_counter_sample_time = Column(DateTime)
 
# sqlalchemy_example.db file.
engine = create_engine(MYSQL_URL)
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
