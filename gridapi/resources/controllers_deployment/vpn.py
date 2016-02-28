import jinja2
from flask_restful import Resource, abort
from gridapi.resources.models import GridEntity, configs, deployments

class VpnHandler(Resource):
    def _abort_if_grid_doesnt_exist(self, grid_name):
        if not GridEntity.select().where(
                        GridEntity.name == grid_name).exists():
            abort(404, message="Grid {} doesn't exist".format(grid_name))

    def _abort_if_config_doesnt_exist(self, grid_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not configs[
            grid.provider].select().where(
                    configs[
                        grid.provider].parentgrid == grid).exists():
            abort(404,
                  message="Config of grid {} doesn't exist".format(
                      grid_name))

    def _abort_if_deployment_doesnt_exist(self, grid_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not deployments[
            grid.provider].select().where(
                    deployments[
                        grid.provider].parentgrid == grid).exists():
            abort(404, message="Deployment of grid {} doesn't exist".format(
                grid_name))

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        deployment = deployments[grid.provider].select().where(
            deployments[grid.provider].parentgrid == grid).get()
        with open('gridapi/resources/templates/vpn/vpn.ovpn', 'r') as src:
            template = jinja2.Template(src.read())
        template_content = template.render(accessip=deployment._accessip)
        return template_content, 200
