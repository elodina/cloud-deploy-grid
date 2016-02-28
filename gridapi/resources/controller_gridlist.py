import ast
from flask_restful import Resource
from gridapi.resources.parsers import grid_parser
from gridapi.resources.models import GridEntity, configs, deployments


class GridListHandler(Resource):
    def get(self):
        grids = []
        for grid in GridEntity.select():
            grids.append({'name': grid.name,
                             'provider': grid.provider})
        return grids

    def post(self):
        args = grid_parser.parse_args()
        if not GridEntity.select().where(
                        GridEntity.name == args['name']).exists():
            grid = GridEntity.create(
                name=args['name'].lower(),
                provider=args['provider'],
                type=args['type'])
            grid.config = configs[grid.provider].create(
                parentgrid=grid)
            grid.deployment = deployments[grid.provider].create(
                parentgrid=grid)
            return ast.literal_eval(str(grid)), 200
        else:
            return 'Grid {} already exists'.format(args['name']), 409
