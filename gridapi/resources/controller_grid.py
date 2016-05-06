import ast
from flask_restful import Resource, abort
from gridapi.resources.models import GridEntity, ConfigEntity, DeploymentEntity, InfrastructureDeploymentEntity, ProvisionDeploymentEntity, GroupEntity


class GridHandler(Resource):
    def _abort_if_grid_doesnt_exist(self, grid_name):
        if not len(GridEntity.objects(name=grid_name)):
            abort(404, message="Grid {} doesn't exist".format(grid_name))

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        return ast.literal_eval(str(grid)), 200

    def delete(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        try:
            GridEntity.objects(name=grid_name).if_exists().delete()
        except:
            pass
        try:
            ConfigEntity.objects(parentgrid=grid_name).if_exists().delete()
        except:
            pass
        try:
            DeploymentEntity.objects(parentgrid=grid_name).if_exists().delete()
        except:
            pass
        try:
            GroupEntity.objects(parentgrid=grid_name).if_exists().delete()
        except:
            pass
        try:
            InfrastructureDeploymentEntity.objects(parentgrid=grid_name).if_exists().delete()
        except:
            pass
        try:
            ProvisionDeploymentEntity.objects(parentgrid=grid_name).if_exists().delete()
        except:
            pass
        return '', 200
