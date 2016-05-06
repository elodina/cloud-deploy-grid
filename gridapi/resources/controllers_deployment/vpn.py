import jinja2
from flask_restful import Resource, abort
from gridapi.resources.models import GridEntity, configs, deployments, infrastructure_deployments

class VpnHandler(Resource):
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

    def _abort_if_infrastructure_deployment_doesnt_exist(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        if not len(infrastructure_deployments[grid.provider].objects(parentgrid=grid_name)):
            abort(404, message="Infrastructure Deployment of grid {} doesn't exist".format(grid_name))

    def _abort_if_infrastructure_deployment_was_not_successful(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        if infrastructure_deployment.state != 'deployed':
            abort(404, message="Infrastructure Deployment of grid need to be successful first".format(grid_name))

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_was_not_successful(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        with open('gridapi/resources/templates/vpn/vpn.ovpn', 'r') as src:
            template = jinja2.Template(src.read())
        template_content = template.render(accessip=infrastructure_deployment.accessip)
        return template_content, 200
