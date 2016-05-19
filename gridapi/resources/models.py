import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from datetime import datetime
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model

cassandra_hosts = ['cdg-cassandra.service']

connection.setup(cassandra_hosts, 'grids', protocol_version=4)

class GridEntity(Model):
    name = columns.Text(primary_key=True)
    provider = columns.Text(index=True)
    type = columns.Text()

    def __str__(self):
        return str(dict(self))


class ConfigEntity(Model):
    parentgrid = columns.Text(primary_key=True)
    provider = columns.Text(discriminator_column=True)
    vars = columns.Text()

    def __str__(self):
        return str(dict(self))


class AWSConfigEntity(ConfigEntity):
    __discriminator_value__ = 'aws'
    masters = columns.Text()
    master_type = columns.Text()
    region = columns.Text()
    sshkey = columns.Text()
    sshkeydata = columns.Text()
    ssh_user = columns.Text()


class AzureConfigEntity(ConfigEntity):
    __discriminator_value__ = 'azure'
    masters = columns.Text()
    master_type = columns.Text()
    location = columns.Text()
    ssh_user = columns.Text()
    ssh_password = columns.Text()


class GCEConfigEntity(ConfigEntity):
    __discriminator_value__ = 'gce'
    masters = columns.Text()
    master_type = columns.Text()
    project = columns.Text()
    zone = columns.Text()
    sshkeydata = columns.Text()
    ssh_user = columns.Text()


class OpenstackConfigEntity(ConfigEntity):
    __discriminator_value__ = 'openstack'
    masters = columns.Text()
    master_type = columns.Text()
    terminal_type = columns.Text()
    image_name = columns.Text()
    sshkeydata = columns.Text()
    tenant = columns.Text()
    region = columns.Text()
    external_network_uuid = columns.Text()
    floating_ip_pool = columns.Text()
    ssh_user = columns.Text()


class CustomConfigEntity(ConfigEntity):
    __discriminator_value__ = 'custom'
    ssh_user = columns.Text()
    sshkeydata = columns.Text()
    mastersips = columns.Text()
    terminalips = columns.Text()


class DeploymentEntity(Model):
    parentgrid = columns.Text(primary_key=True)
    provider = columns.Text(discriminator_column=True, index=True)
    lock = columns.Boolean(default=False)
    state = columns.Text(default='init')

    def __str__(self):
        return str(dict(self))

class InfrastructureDeploymentEntity(Model):
    parentgrid = columns.Text(primary_key=True)
    provider = columns.Text(discriminator_column=True, index=True)
    accessip = columns.Text()
    state = columns.Text()
    tfstate = columns.Text()

    def __str__(self):
        return str(dict(self))

class ProvisionDeploymentEntity(Model):
    parentgrid = columns.Text(primary_key=True)
    provider = columns.Text(discriminator_column=True, index=True)
    state = columns.Text()

    def __str__(self):
        return str(dict(self))

class AWSDeploymentEntity(DeploymentEntity):
    __discriminator_value__ = 'aws'


class AWSInfrastructureDeploymentEntity(InfrastructureDeploymentEntity):
    __discriminator_value__ = 'aws'


class AWSProvisionDeploymentEntity(ProvisionDeploymentEntity):
    __discriminator_value__ = 'aws'


class AzureDeploymentEntity(DeploymentEntity):
    __discriminator_value__ = 'azure'


class AzureInfrastructureDeploymentEntity(InfrastructureDeploymentEntity):
    __discriminator_value__ = 'azure'


class AzureProvisionDeploymentEntity(ProvisionDeploymentEntity):
    __discriminator_value__ = 'azure'


class GCEDeploymentEntity(DeploymentEntity):
    __discriminator_value__ = 'gce'


class GCEInfrastructureDeploymentEntity(InfrastructureDeploymentEntity):
    __discriminator_value__ = 'gce'


class GCEProvisionDeploymentEntity(ProvisionDeploymentEntity):
    __discriminator_value__ = 'gce'


class OpenstackDeploymentEntity(DeploymentEntity):
    __discriminator_value__ = 'openstack'


class OpenstackInfrastructureDeploymentEntity(InfrastructureDeploymentEntity):
    __discriminator_value__ = 'openstack'


class OpenstackProvisionDeploymentEntity(ProvisionDeploymentEntity):
    __discriminator_value__ = 'openstack'


class CustomDeploymentEntity(DeploymentEntity):
    __discriminator_value__ = 'custom'


class CustomInfrastructureDeploymentEntity(InfrastructureDeploymentEntity):
    __discriminator_value__ = 'custom'


class CustomProvisionDeploymentEntity(ProvisionDeploymentEntity):
    __discriminator_value__ = 'custom'


class GroupEntity(Model):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    parentgrid = columns.Text(index=True, partition_key=True)
    provider = columns.Text(discriminator_column=True)
    slaves = columns.Integer()
    name = columns.Text(index=True, partition_key=True)
    role = columns.Text(default='infra')
    attributes = columns.Text()
    vars = columns.Text(default='{"foo": "bar"}')

    def __str__(self):
        self.id = '{}_{}'.format(self.parentgrid, self.name)
        return str(dict(self))


class AWSGroupEntity(GroupEntity):
    __discriminator_value__ = 'aws'
    instance_type = columns.Text()
    cpus = columns.Integer()
    ram = columns.Integer()
    disk_size = columns.Integer()
    customhwconf = columns.Text(default='')
    enhanced_networking = columns.Boolean(default=False)
    az = columns.Text(default='')
    spot_price = columns.Text(default='')


class AzureGroupEntity(GroupEntity):
    __discriminator_value__ = 'azure'
    instance_type = columns.Text()
    cpus = columns.Integer()
    ram = columns.Integer()
    disk_size = columns.Integer()
    customhwconf = columns.Text(default='')

 
class GCEGroupEntity(GroupEntity):
    __discriminator_value__ = 'gce'
    instance_type = columns.Text()
    cpus = columns.Integer()
    ram = columns.Integer()
    disk_size = columns.Integer()
    customhwconf = columns.Text(default='')
    preemptible = columns.Boolean(default=False)
    zone = columns.Text(default='')


class OpenstackGroupEntity(GroupEntity):
    __discriminator_value__ = 'openstack'
    instance_type = columns.Text()
    slaves = columns.Integer()
    customhwconf = columns.Text(default='')

class CustomGroupEntity(GroupEntity):
    __discriminator_value__ = 'custom'
    groupips = columns.Text()

configs = {
    'aws': AWSConfigEntity,
    'azure': AzureConfigEntity,
    'gce': GCEConfigEntity,
    'openstack': OpenstackConfigEntity,
    'custom': CustomConfigEntity
}

deployments = {
    'aws': AWSDeploymentEntity,
    'azure': AzureDeploymentEntity,
    'gce': GCEDeploymentEntity,
    'openstack': OpenstackDeploymentEntity,
    'custom': CustomDeploymentEntity
}

infrastructure_deployments = {
    'aws': AWSInfrastructureDeploymentEntity,
    'azure': AzureInfrastructureDeploymentEntity,
    'gce': GCEInfrastructureDeploymentEntity,
    'openstack': OpenstackInfrastructureDeploymentEntity,
    'custom': CustomInfrastructureDeploymentEntity
}

provision_deployments = {
    'aws': AWSProvisionDeploymentEntity,
    'azure': AzureProvisionDeploymentEntity,
    'gce': GCEProvisionDeploymentEntity,
    'openstack': OpenstackProvisionDeploymentEntity,
    'custom': CustomProvisionDeploymentEntity
}

groups = {
    'aws': AWSGroupEntity,
    'azure': AzureGroupEntity,
    'gce': GCEGroupEntity,
    'openstack': OpenstackGroupEntity,
    'custom': CustomGroupEntity
}



def init_db():
    from cassandra.cluster import Cluster

    cluster = Cluster(cassandra_hosts)
    session = cluster.connect()

    session.execute("CREATE KEYSPACE IF NOT EXISTS grids WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }")

    connection.setup(cassandra_hosts, "grids", protocol_version=4)

    sync_table(GridEntity)
    sync_table(ConfigEntity)
    sync_table(AWSConfigEntity)
    sync_table(AzureConfigEntity)
    sync_table(GCEConfigEntity)
    sync_table(OpenstackConfigEntity)
    sync_table(CustomConfigEntity)
    sync_table(DeploymentEntity)
    sync_table(InfrastructureDeploymentEntity)
    sync_table(ProvisionDeploymentEntity)    
    sync_table(AWSDeploymentEntity)
    sync_table(AWSInfrastructureDeploymentEntity)
    sync_table(AWSProvisionDeploymentEntity)
    sync_table(AzureDeploymentEntity)
    sync_table(AzureInfrastructureDeploymentEntity)
    sync_table(AzureProvisionDeploymentEntity)
    sync_table(GCEDeploymentEntity)
    sync_table(GCEInfrastructureDeploymentEntity)
    sync_table(GCEProvisionDeploymentEntity)
    sync_table(OpenstackDeploymentEntity)
    sync_table(OpenstackInfrastructureDeploymentEntity)
    sync_table(OpenstackProvisionDeploymentEntity)
    sync_table(CustomDeploymentEntity)
    sync_table(CustomInfrastructureDeploymentEntity)
    sync_table(CustomProvisionDeploymentEntity)
    sync_table(GroupEntity)
    sync_table(AWSGroupEntity)
    sync_table(AzureGroupEntity)
    sync_table(GCEGroupEntity)
    sync_table(OpenstackGroupEntity)
    sync_table(CustomGroupEntity)

if __name__ == '__main__':
    init_db()
