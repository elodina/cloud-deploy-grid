from flask import Flask
from flask_restful import Api
from gridapi.resources.controller_grid import GridHandler
from gridapi.resources.controller_gridlist import GridListHandler
from gridapi.resources.controller_config import ConfigHandler
from gridapi.resources.controller_group import GroupHandler
from gridapi.resources.controller_grouplist import GroupListHandler
from gridapi.resources.controllers_deployment.common import\
    DeploymentHandler
from gridapi.resources.controllers_deployment.infrastructure import\
    InfrastructureDeploymentHandler, ExportInfrastructureDeploymentHandler
from gridapi.resources.controllers_deployment.provision import\
    ProvisionDeploymentHandler, GroupProvisionDeploymentHandler
from gridapi.resources.controllers_deployment.vpn import\
    VpnHandler

app = Flask(__name__)
api = Api(app)

api.add_resource(GridListHandler, '/api/v2.0/grids')
api.add_resource(GridHandler, '/api/v2.0/grids/<grid_name>')
api.add_resource(ConfigHandler, '/api/v2.0/grids/<grid_name>/config')
api.add_resource(GroupListHandler, '/api/v2.0/grids/<grid_name>/groups')
api.add_resource(GroupHandler,
                 '/api/v2.0/grids/<grid_name>/groups/<group_name>')
api.add_resource(GroupProvisionDeploymentHandler,
                 '/api/v2.0/grids/<grid_name>/groups/<group_name>/provision')
api.add_resource(DeploymentHandler,
                 '/api/v2.0/grids/<grid_name>/deployment')
api.add_resource(InfrastructureDeploymentHandler,
                 '/api/v2.0/grids/<grid_name>/deployment/infrastructure')
api.add_resource(ExportInfrastructureDeploymentHandler,
                 '/api/v2.0/grids/<grid_name>/deployment/infrastructure/export')
api.add_resource(ProvisionDeploymentHandler,
                 '/api/v2.0/grids/<grid_name>/deployment/provision')
api.add_resource(VpnHandler,
                 '/api/v2.0/grids/<grid_name>/deployment/vpn')
