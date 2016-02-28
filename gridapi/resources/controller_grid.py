import ast
from flask_restful import Resource, abort
from gridapi.resources.models import GridEntity


class GridHandler(Resource):
    def _abort_if_grid_doesnt_exist(self, grid_name):
        if not GridEntity.select().where(
                        GridEntity.name == grid_name).exists():
            abort(404, message="Grid {} doesn't exist".format(grid_name))

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        return ast.literal_eval(str(grid)), 200

    def delete(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        grid.delete_instance()
        return '', 200
