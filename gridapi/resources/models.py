import json
from peewee import SqliteDatabase, Model, BooleanField, CharField,\
    ForeignKeyField, IntegerField, TextField

db = SqliteDatabase('grids.db', pragmas=(
    ('foreign_keys', 'ON'),
))


class BaseModel(Model):
    class Meta:
        database = db


class GridEntity(BaseModel):
    name = CharField(unique=True)
    provider = CharField()
    type = CharField()

    def __str__(self):
        dict_representation = {}
        for key in self._data.keys():
            if key != 'id':
                try:
                    dict_representation[key] = str(getattr(self, key))
                except:
                    dict_representation[key] = json.dumps(getattr(self, key))
        return str(dict_representation)


class ConfigEntity(BaseModel):
    parentgrid = ForeignKeyField(
        GridEntity, to_field='id', on_delete='CASCADE', on_update='CASCADE')
    vars = CharField(default='{"foo": "bar"}', null=True)

    def __str__(self):
        dict_representation = {}
        for key in self._data.keys():
            if key != 'id' and key != 'parentgrid':
                try:
                    dict_representation[key] = str(getattr(self, key))
                except:
                    dict_representation[key] = json.dumps(getattr(self, key))
        return str(dict_representation)


class AWSConfigEntity(ConfigEntity):
    masters = IntegerField(null=True)
    master_type = CharField(null=True)
    region = CharField(null=True)
    sshkey = CharField(null=True)
    sshkeydata = TextField(null=True)
    ssh_user = CharField(null=True)


class AzureConfigEntity(ConfigEntity):
    masters = IntegerField(null=True)
    master_type = CharField(null=True)
    location = CharField(null=True)
    ssh_user = CharField(null=True)
    ssh_password = CharField(null=True)


class GCSConfigEntity(ConfigEntity):
    masters = IntegerField(null=True)
    master_type = CharField(null=True)
    project = CharField(null=True)
    zone = CharField(null=True)
    sshkeydata = TextField(null=True)
    ssh_user = CharField(null=True)


class OpenstackConfigEntity(ConfigEntity):
    masters = IntegerField(null=True)
    master_type = CharField(null=True)
    terminal_type = CharField(null=True)
    image_name = CharField(null=True)
    sshkeydata = TextField(null=True)
    tenant = CharField(null=True)
    region = CharField(null=True)
    external_network_uuid = CharField(null=True)
    floating_ip_pool = CharField(null=True)
    ssh_user = CharField(null=True)

class CustomConfigEntity(ConfigEntity):
    ssh_user = CharField(null=True)
    sshkeydata = TextField(null=True)
    mastersips = CharField(null=True)
    terminalips = CharField(null=True)


class DeploymentEntity(BaseModel):
    _lock = BooleanField(default=False)
    _status = CharField(default='init')
    parentgrid = ForeignKeyField(
        GridEntity, to_field='id', on_delete='CASCADE', on_update='CASCADE')

    def __str__(self):
        dict_representation = {}
        for key in self._data.keys():
            if key != 'id' and key != 'parentgrid' and key != '_state':
                try:
                    dict_representation[key] = str(getattr(self, key))
                except:
                    dict_representation[key] = json.dumps(getattr(self, key))
        return str(dict_representation)


class AWSDeploymentEntity(DeploymentEntity):
    pass


class AWSInfrastructureDeploymentEntity(AWSDeploymentEntity):
    _accessip = CharField(null=True)
    _state = TextField(default='{"foo": "bar"}')


class AWSProvisionDeploymentEntity(AWSDeploymentEntity):
    pass


class AzureDeploymentEntity(DeploymentEntity):
    pass


class AzureInfrastructureDeploymentEntity(AzureDeploymentEntity):
    _accessip = CharField(null=True)
    _state = TextField(default='{"foo": "bar"}')


class AzureProvisionDeploymentEntity(AzureDeploymentEntity):
    pass


class GCSDeploymentEntity(DeploymentEntity):
    pass


class GCSInfrastructureDeploymentEntity(GCSDeploymentEntity):
    _accessip = CharField(null=True)
    _state = TextField(default='{"foo": "bar"}')


class GCSProvisionDeploymentEntity(GCSDeploymentEntity):
    pass


class OpenstackDeploymentEntity(DeploymentEntity):
    pass


class OpenstackInfrastructureDeploymentEntity(OpenstackDeploymentEntity):
    _accessip = CharField(null=True)
    _state = TextField(default='{"foo": "bar"}')


class OpenstackProvisionDeploymentEntity(OpenstackDeploymentEntity):
    pass


class CustomDeploymentEntity(DeploymentEntity):
    pass


class CustomInfrastructureDeploymentEntity(CustomDeploymentEntity):
    _accessip = CharField(null=True)
    _state = TextField(default='{"foo": "bar"}')


class CustomProvisionDeploymentEntity(CustomDeploymentEntity):
    pass


class GroupEntity(BaseModel):
    _slaves = IntegerField(null=True)
    parentgrid = ForeignKeyField(
        GridEntity, to_field='id', on_delete='CASCADE', on_update='CASCADE')
    name = CharField()
    role = CharField(default='infra')
    attributes = CharField(null=True)
    vars = CharField(default='{"foo": "bar"}', null=True)

    def __str__(self):
        dict_representation = {}
        for key in self._data.keys():
            if key != 'id' and key != 'parentgrid':
                try:
                    dict_representation[key] = str(getattr(self, key))
                except:
                    dict_representation[key] = json.dumps(getattr(self, key))
        return str(dict_representation)


class AWSGroupEntity(GroupEntity):
    instance_type = CharField(null=True)
    cpus = IntegerField(null=True)
    ram = IntegerField(null=True)
    disk_size = IntegerField(null=True)
    customhwconf = CharField(default='', null=True)
    enhanced_networking = BooleanField(default=False, null=True)
    az = CharField(default='', null=True)
    spot_price = CharField(default='', null=True)


class AzureGroupEntity(GroupEntity):
    instance_type = CharField(null=True)
    cpus = IntegerField(null=True)
    ram = IntegerField(null=True)
    disk_size = IntegerField(null=True)
    customhwconf = CharField(default='', null=True)


class GCSGroupEntity(GroupEntity):
    instance_type = CharField(null=True)
    cpus = IntegerField(null=True)
    ram = IntegerField(null=True)
    disk_size = IntegerField(null=True)
    customhwconf = CharField(default='', null=True)
    preemptible = BooleanField(default=False, null=True)
    zone = CharField(default='', null=True)


class OpenstackGroupEntity(GroupEntity):
    instance_type = CharField(null=True)
    slaves = IntegerField(null=True)
    customhwconf = CharField(default='', null=True)

class CustomGroupEntity(GroupEntity):
    groupips = CharField(null=True)

configs = {
    'aws': AWSConfigEntity,
    'azure': AzureConfigEntity,
    'gcs': GCSConfigEntity,
    'openstack': OpenstackConfigEntity,
    'custom': CustomConfigEntity
}

deployments = {
    'aws': AWSDeploymentEntity,
    'azure': AzureDeploymentEntity,
    'gcs': GCSDeploymentEntity,
    'openstack': OpenstackDeploymentEntity,
    'custom': CustomDeploymentEntity
}

infrastructure_deployments = {
    'aws': AWSInfrastructureDeploymentEntity,
    'azure': AzureInfrastructureDeploymentEntity,
    'gcs': GCSInfrastructureDeploymentEntity,
    'openstack': OpenstackInfrastructureDeploymentEntity,
    'custom': CustomInfrastructureDeploymentEntity
}

provision_deployments = {
    'aws': AWSProvisionDeploymentEntity,
    'azure': AzureProvisionDeploymentEntity,
    'gcs': GCSProvisionDeploymentEntity,
    'openstack': OpenstackProvisionDeploymentEntity,
    'custom': CustomProvisionDeploymentEntity
}

groups = {
    'aws': AWSGroupEntity,
    'azure': AzureGroupEntity,
    'gcs': GCSGroupEntity,
    'openstack': OpenstackGroupEntity,
    'custom': CustomGroupEntity
}

if __name__ == '__main__':
    GridEntity.create_table(fail_silently=True)
    for provider, config in configs.iteritems():
        config.create_table(fail_silently=True)
    for provider, deployment in deployments.iteritems():
        deployment.create_table(fail_silently=True)
    for provider, infrastructure_deployment in infrastructure_deployments.iteritems():
        infrastructure_deployment.create_table(fail_silently=True)
    for provider, provision_deployment in provision_deployments.iteritems():
        provision_deployment.create_table(fail_silently=True)
    for provider, group in groups.iteritems():
        group.create_table(fail_silently=True)
