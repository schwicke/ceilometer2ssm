""" DB Models
SQLAlchemy models for DB Models data.
"""

from api import BASE
from sqlalchemy import Column, Index, Integer,Boolean, String, schema
from sqlalchemy import ForeignKey, DateTime


class Resources(BASE):
    #Represents a resource in OpenStack.

    __tablename__ = 'resources'
    __table_args__ = (
        Index('resources_deleted_idx', 'deleted'),
    )
    #id = Column(String(255), primary_key=True, nullable=False)
    user_id = Column(String(255))
    project_id = Column(String(255))
    resource_id =  Column(String(255), primary_key=True, nullable=False)
    tenant_id=Column(String(255))
    node=Column(String(255))
    host_name=Column(String(255))
    tenant_name=Column(String(255))
    vmuuid=Column(String(255))
    image_ref_url=Column(String(255))
    state=Column(String(255))
    vcpus=Column(Integer)
    memory_mb=Column(Integer)
    disk_gb=Column(Integer)
    hep_spec=Column(String(255))
    created_at = Column(DateTime)
    launched_at = Column(DateTime)
    deleted_at = Column(DateTime)
    terminated_at = Column(DateTime)
    deleted = Column(Boolean, default=False)

    def __init__(self, user_id, project_id, resource_id,tenant_id,tenant_name,
                      node,host_name,vmuuid,image_ref_url,state, vcpus,memory_mb,
                      disk_gb,deleted,hep_spec, created_at, launched_at, deleted_at,
                      terminated_at):
        self.user_id = user_id
        self.project_id = project_id
        self.resource_id = resource_id
        self.tenant_id=tenant_id
        self.tenant_name=tenant_name
        self.node=node
        self.host_name=host_name
        self.vmuuid=vmuuid
        self.image_ref_url=image_ref_url
        self.state=state
        self.vcpus=vcpus
        self.memory_mb=memory_mb
        self.disk_gb=disk_gb
        self.deleted = deleted
        if node is not None and node !="":
            self.hep_spec=hep_spec
        if created_at is not None and created_at != "":
            self.created_at = created_at

        if launched_at is not None and launched_at != "":
            self.launched_at = launched_at

        if deleted_at is not None and deleted_at != "":
            self.deleted_at = deleted_at

        if terminated_at is not None and terminated_at != "":
            self.terminated_at = terminated_at

class CurrentRecord(BASE):
    #Represents a resource in OpenStack.

    __tablename__ = 'current_record'
    __table_args__ = (
        schema.UniqueConstraint("user_id", "project_id", "resource_id",
                        name="uniq_resources0user_id0project_id0resource_id"),
    )
    #id = Column(String(255), primary_key=True, nullable=False)
    user_id = Column(String(255))
    project_id = Column(String(255))
    resource_id = Column(String(255), primary_key=True, nullable=False)
    tenant_id=Column(String(255))
    group_name=Column(String(64))
    node=Column(String(255))
    host_name=Column(String(255))
    tenant_name=Column(String(255))
    vmuuid=Column(String(255))
    image_ref_url=Column(String(255))
    state=Column(String(255))
    vcpus=Column(Integer)
    memory_mb=Column(Integer)
    disk_gb=Column(Integer)
    hep_spec=Column(String(255))
    created_at = Column(DateTime)
    launched_at = Column(DateTime)
    deleted_at = Column(DateTime)
    terminated_at = Column(DateTime)
    deleted = Column(Boolean, default=False)

    cpu_counter_source = Column(String(64))
    cpu_counter_unit = Column(String(32))
    cpu_counter_volume = Column(String(64))
    cpu_counter_type = Column(String(32))
    cpu_counter_sample_time = Column(DateTime)

    instance_counter_source = Column(String(64))
    instance_counter_unit = Column(String(32))
    instance_counter_volume = Column(String(64))
    instance_counter_type = Column(String(32))
    instance_counter_sample_time = Column(DateTime)

    net_in_counter_source = Column(String(64))
    net_in_counter_unit = Column(String(32))
    net_in_counter_volume = Column(String(64))
    net_in_counter_type = Column(String(32))
    net_in_counter_sample_time = Column(DateTime)

    net_out_counter_source = Column(String(64))
    net_out_counter_unit = Column(String(32))
    net_out_counter_volume = Column(String(64))
    net_out_counter_type = Column(String(32))
    net_out_counter_sample_time = Column(DateTime)





    def __init__(self,user_id, project_id, resource_id,tenant_id,group_name,tenant_name,
                                           node,host_name,vmuuid,image_ref_url,state, vcpus,memory_mb,
                                           disk_gb,deleted,hep_spec, created_at, launched_at, deleted_at,
                                           terminated_at,instance_counter_volume,cpu_counter_volume, net_in_counter_volume,
                                           net_out_counter_volume,instance_counter_type,cpu_counter_type,net_in_counter_type,
                                           net_out_counter_type,instance_counter_source,cpu_counter_source,net_in_counter_source,
                                           net_out_counter_source,instance_counter_sample_time,cpu_counter_sample_time,net_in_counter_sample_time,
                                           net_out_counter_sample_time,instance_counter_unit,cpu_counter_unit,net_in_counter_unit,
                                           net_out_counter_unit):
        self.project_id = project_id
        self.resource_id = resource_id
        self.tenant_id=tenant_id
        self.group_name=group_name
        self.tenant_name=tenant_name
        self.node=node
        self.host_name=host_name
        self.vmuuid=vmuuid
        self.image_ref_url=image_ref_url
        self.state=state
        self.vcpus=vcpus
        self.memory_mb=memory_mb
        self.disk_gb=disk_gb
        self.deleted = deleted

        self.cpu_counter_type=cpu_counter_type
        self.cpu_counter_source=cpu_counter_source
        self.cpu_counter_unit=cpu_counter_unit
        self.cpu_counter_volume=cpu_counter_volume
        self.cpu_counter_sample_time=cpu_counter_sample_time

        self.instance_counter_type=instance_counter_type
        self.instance_counter_source=instance_counter_source
        self.instance_counter_unit=instance_counter_unit
        self.instance_counter_volume=instance_counter_volume
        self.instance_counter_sample_time=instance_counter_sample_time

        self.net_in_counter_type=net_in_counter_type
        self.net_in_counter_source=net_in_counter_source
        self.net_in_counter_unit=net_in_counter_unit
        self.net_in_counter_volume=net_in_counter_volume
        self.net_in_counter_sample_time=net_in_counter_sample_time

        self.net_out_counter_type=net_out_counter_type
        self.net_out_counter_source=net_out_counter_source
        self.net_out_counter_unit=net_out_counter_unit
        self.net_out_counter_volume=net_out_counter_volume
        self.net_out_counter_sample_time=net_out_counter_sample_time
        if node is not None and node !="":
            self.hep_spec=hep_spec
        if created_at is not None and created_at != "":
            self.created_at = created_at

        if launched_at is not None and launched_at != "":
            self.launched_at = launched_at

        if deleted_at is not None and deleted_at != "":
            self.deleted_at = deleted_at

        if terminated_at is not None and terminated_at != "":
            self.terminated_at = terminated_at
class MetricData(BASE):
    #Represents a metric of a resource in OpenStack.

    __tablename__ = 'metric_data'
    __table_args__ = (
        schema.UniqueConstraint("r_id", "counter_name", "sample_time",
                    name="uniq_metric_data0r_id0counter_name0sample_time"),
    )

    id = Column(String(255), primary_key=True, nullable=False)
    r_id = Column(String(255), ForeignKey('resources.resource_id'), nullable=False)
    counter_name = Column(String(32))
    source = Column(String(64))
    counter_unit = Column(String(32))
    counter_volume = Column(String(64))
    counter_type = Column(String(32))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    sample_time = Column(DateTime)

    def __init__(self, id, r_id, counter_name, source, counter_unit,
                    counter_volume, counter_type, start_time, end_time,
                    sample_time):
        self.id = id
        self.r_id = r_id
        self.counter_name = counter_name
        self.source = source
        self.counter_unit = counter_unit
        self.counter_volume = counter_volume
        self.counter_type = counter_type
        self.start_time = start_time
        self.end_time = end_time
        self.sample_time = sample_time




