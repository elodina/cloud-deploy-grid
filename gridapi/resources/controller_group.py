import math
import ast
from flask_restful import Resource, abort
from gridapi.resources.parsers import groupparsers
from gridapi.resources.models import GridEntity, configs, deployments,\
    groups
from gridapi.libs.aws.instances import ec2instances, ec2instances_load
from gridapi.libs.azure.instances import azureinstances


class GroupHandler(Resource):
    def _abort_if_grid_doesnt_exist(self, grid_name):
        if not GridEntity.select().where(
                        GridEntity.name == grid_name).exists():
            abort(404, message="Grid {} doesn't exist".format(grid_name))

    def _abort_if_config_doesnt_exist(self, grid_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not configs[grid.provider].select().where(
                        configs[grid.provider].parentgrid ==
                        grid).exists():
            abort(404, message="Config of grid {} doesn't exist".format(
                grid_name))

    def _abort_if_deployment_doesnt_exist(self, grid_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not deployments[grid.provider].select().where(
                        deployments[grid.provider].parentgrid ==
                        grid).exists():
            abort(404, message="Deployment of grid {} doesn't exist".format(
                grid_name))

    def _abort_if_group_doesnt_exist(self, grid_name, group_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not groups[grid.provider].select().where(
                        groups[grid.provider].name == group_name,
                        groups[grid.provider].parentgrid ==
                        grid).exists():
            abort(404, message="Group {} doesn't exist".format(group_name))

    def _aws_slave_calculator(self, cpus, ram, image):
        ec2instances_load()
        amount_by_cpu = int(math.ceil(
            cpus / float(ec2instances[image]['cpu'])))
        amount_by_ram = int(math.ceil(
            ram / float(ec2instances[image]['ram'])))
        return max(amount_by_cpu, amount_by_ram)

    def _azure_slave_calculator(self, cpus, ram, image):
        amount_by_cpu = int(math.ceil(
            cpus / float(azureinstances[image]['cpu'])))
        amount_by_ram = int(math.ceil(
            ram / float(azureinstances[image]['ram'])))
        return max(amount_by_cpu, amount_by_ram)

    def _custom_slave_calculator(self, groupips):
        return len(groupips.split(','))

    _slave_calculator = {
        'aws': _aws_slave_calculator,
        'azure': _azure_slave_calculator,
        'custom': _custom_slave_calculator
    }

    def get(self, grid_name, group_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_group_doesnt_exist(grid_name, group_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        group = groups[grid.provider].select().where(
            groups[grid.provider].name == group_name,
            groups[grid.provider].parentgrid == grid).get()
        return ast.literal_eval(str(group)), 200

    def delete(self, grid_name, group_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_group_doesnt_exist(grid_name, group_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        group = groups[grid.provider].select().where(
            groups[grid.provider].name == group_name,
            groups[grid.provider].parentgrid == grid).get()
        group.delete_instance()
        return '', 200

    def put(self, grid_name, group_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_group_doesnt_exist(grid_name, group_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        group = groups[grid.provider].select().where(
            groups[grid.provider].name == group_name,
            groups[grid.provider].parentgrid == grid).get()
        oldgroup = group
        args = groupparsers[grid.provider].parse_args()
        for key in group._data.keys():
            if key != 'id' and key != 'parentgrid' and key != '_slaves':
                setattr(group, key, args[key])
        if group.parentgrid.provider == 'custom':
            slaves_args = [args['groupips']]
        else:
            slaves_args = [args['cpus'], args['ram'], args['instance_type']]
        group._slaves = self._slave_calculator[grid.provider](
            self, *slaves_args)
        group.save()
        if args['name'] != oldgroup.name:
            deletegroup = groups[grid.provider].select().where(
                groups[grid.provider].name == oldgroup.name,
                groups[grid.provider].parentgrid == grid).get()
            deletegroup.delete_instance()
        return ast.literal_eval(str(group)), 200


