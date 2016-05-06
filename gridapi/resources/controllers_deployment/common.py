import ast
from flask_restful import Resource, abort
from gridapi.resources.models import GridEntity, configs, deployments

class DeploymentHandler(Resource):
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

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        deployment = deployments[grid.provider].objects(parentgrid=grid_name).get()
        return ast.literal_eval(str(deployment)), 200
