import ast
from flask_restful import Resource
from gridapi.resources.parsers import grid_parser
from gridapi.resources.models import GridEntity, configs, deployments


class GridListHandler(Resource):
    def _abort_if_grid_already_exist(self, grid_name):
        if len(GridEntity.objects(name=grid_name)):
            abort(409, message="Grid {} doesn't exist".format(grid_name))

    def get(self):
        grids = []
        for grid in GridEntity.objects.all():
            grids.append({'name': grid.name, 'provider': grid.provider})
        return grids

    def post(self):
        args = grid_parser.parse_args()
        grid_name = args['name'].lower()
        self._abort_if_grid_already_exist(grid_name)
        grid = GridEntity.create(name=grid_name, provider=args['provider'], type=args['type'])
        grid.config = configs[grid.provider].create(parentgrid=grid_name)
        grid.deployment = deployments[grid.provider].create(parentgrid=grid_name)
        return ast.literal_eval(str(grid)), 200
