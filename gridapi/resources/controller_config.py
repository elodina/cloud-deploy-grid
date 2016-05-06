import ast
from flask_restful import Resource, abort
from gridapi.resources.parsers import configparsers
from gridapi.resources.models import GridEntity, configs


class ConfigHandler(Resource):
    def _abort_if_grid_doesnt_exist(self, grid_name):
        if not len(GridEntity.objects(name=grid_name)):
            abort(404, message="Grid {} doesn't exist".format(grid_name))

    def _abort_if_config_doesnt_exist(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        if not len(configs[grid.provider].objects(parentgrid=grid_name)):
            abort(404, message="Config of grid {} doesn't exist".format(grid_name))

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        config = configs[grid.provider].objects(parentgrid=grid_name).get()
        return ast.literal_eval(str(config)), 200

    def delete(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        config = configs[grid.provider].objects(parentgrid=grid_name).get()
        config.delete()
        return '', 200

    def put(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        args = configparsers[grid.provider].parse_args()
        config = configs[grid.provider].objects(parentgrid=grid_name).get()

        for key in config.keys():
            if key != 'parentgrid' and key != 'provider':
                setattr(config, key, args[key])
        config.save()
        return ast.literal_eval(str(config)), 200
