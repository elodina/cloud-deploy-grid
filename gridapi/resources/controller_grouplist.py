import math
import ast
from flask_restful import Resource, abort
from gridapi.resources.parsers import groupparsers
from gridapi.resources.models import GridEntity, configs, deployments,\
    groups
from gridapi.libs.aws.instances import ec2instances, ec2instances_load
from gridapi.libs.azure.instances import azureinstances
from gridapi.libs.gce.instances import gceinstances


class GroupListHandler(Resource):
    def _abort_if_grid_doesnt_exist(self, grid_name):
        if not len(GridEntity.objects(name=grid_name)):
            abort(404, message="Grid {} doesn't exist".format(grid_name))

    def _abort_if_config_doesnt_exist(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        if not len(configs[grid.provider].objects(parentgrid=grid_name)):
            abort(404, message="Config of grid {} doesn't exist".format(grid_name))

    def _abort_if_deployment_doesnt_exist(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        if not len(deployments[grid.provider].objects(parentgrid=grid_name)):
            abort(404, message="Deployment of grid {} doesn't exist".format(grid_name))

    def _aws_slave_calculator(self, cpus, ram, image):
        ec2instances_load()
        amount_by_cpu = int(math.ceil(cpus / float(ec2instances[image]['cpu'])))
        amount_by_ram = int(math.ceil(ram / float(ec2instances[image]['ram'])))
        return max(amount_by_cpu, amount_by_ram)

    def _azure_slave_calculator(self, cpus, ram, image):
        amount_by_cpu = int(math.ceil(cpus / float(azureinstances[image]['cpu'])))
        amount_by_ram = int(math.ceil(ram / float(azureinstances[image]['ram'])))
        return max(amount_by_cpu, amount_by_ram)

    def _gce_slave_calculator(self, cpus, ram, image):
        amount_by_cpu = int(math.ceil(cpus / float(gceinstances[image]['cpu'])))
        amount_by_ram = int(math.ceil(ram / float(gceinstances[image]['ram'])))
        return max(amount_by_cpu, amount_by_ram)

    def _openstack_slave_calculator(self, slaves):
        return int(slaves)

    def _custom_slave_calculator(self, groupips):
        return len(groupips.split(','))

    _slave_calculator = {
        'aws': _aws_slave_calculator,
        'azure': _azure_slave_calculator,
        'gce': _gce_slave_calculator,
        'openstack': _openstack_slave_calculator,
        'custom': _custom_slave_calculator
    }

    def get(self, grid_name):
        exportgroups = []
        grid = GridEntity.objects(name=grid_name).get()
        for group in groups[grid.provider].objects(parentgrid=grid_name):
            exportgroups.append({'name': group.name, 'role': group.role})
        return exportgroups

    def post(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        args = groupparsers[grid.provider].parse_args()
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        if not len(groups[grid.provider].objects(parentgrid=grid_name, name=args['name'])):
            group = groups[grid.provider].create(parentgrid=grid_name, name=args['name'])
            group = groups[grid.provider].objects(parentgrid=grid_name, name=args['name']).get()
            if grid.provider == 'custom':
                slaves_args = [args['groupips']]
            elif grid.provider == 'openstack':
                slaves_args = [args['slaves']]
            else:
                slaves_args = [args['cpus'], args['ram'], args['instance_type']]
            group.slaves = self._slave_calculator[grid.provider](self, *slaves_args)
            for key in group.keys():
                if key != 'parentgrid' and key != 'slaves' and key != 'provider' and key != 'id':
                    setattr(group, key, args[key])
            group.save()
            return ast.literal_eval(str(group)), 200
        else:
            return 'Group {} already exists'.format(args['name']), 409
