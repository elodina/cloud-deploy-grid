import threading
import os
import ast
import subprocess
import shutil
from flask_restful import Resource, abort
from gridapi.resources.parsers import provision_deploymentparsers
from gridapi.resources.models import GridEntity, configs,\
    deployments, infrastructure_deployments, provision_deployments, groups
from gridapi.resources.generators.provision.mesos.aws import\
    aws_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.azure import\
    azure_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.gcs import\
    gcs_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.openstack import\
    openstack_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.custom import\
    custom_provision_mesos_generator
from gridapi.resources.generators.provision.dcos.azure import\
    azure_provision_dcos_generator
from gridapi.resources.generators.provision.dcos.aws import\
    aws_provision_dcos_generator
from gridapi.resources.generators.provision.dcos.custom import\
    custom_provision_dcos_generator

provision_generators = {
    'mesos': {
        'aws': aws_provision_mesos_generator,
        'azure': azure_provision_mesos_generator,
        'gcs': gcs_provision_mesos_generator,
        'openstack': openstack_provision_mesos_generator,
        'custom': custom_provision_mesos_generator
    },
    'dcos': {
        'aws': aws_provision_dcos_generator,
        'azure': azure_provision_dcos_generator,
        'custom': custom_provision_dcos_generator
    }
}

class ProvisionDeploymentHandler(Resource):
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
            abort(404, message="Deployment of grid {} "
                               "doesn't exist".format(grid_name))

    def _abort_if_infrastructure_deployment_doesnt_exist(self, grid_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not infrastructure_deployments[grid.provider].select().where(
                        infrastructure_deployments[grid.provider
                        ].parentgrid == grid).exists():
            abort(404, message="Infrastructure Deployment of grid {} "
                               "doesn't exist".format(grid_name))

    def _abort_if_infrastructure_deployment_was_not_successful(
            self, grid_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        infrastructure_deployment = infrastructure_deployments[
            grid.provider].select().where(
            infrastructure_deployments[
                grid.provider].parentgrid == grid).get()
        if infrastructure_deployment._status != 'deployed':
            abort(404, message="Infrastructure Deployment of grid need to"
                               " be successful first".format(grid_name))

    def _abort_if_provision_deployment_doesnt_exist(self, grid_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not provision_deployments[grid.provider].select().where(
                        provision_deployments[grid.provider
                        ].parentgrid == grid).exists():
            abort(404, message="Provision Deployment of grid {} "
                               "doesn't exist".format(grid_name))

    def lock(self, deployment):
        if not deployment._lock:
            deployment._lock = True
        else:
            raise Exception('deployment is locked')

    def unlock(self, deployment):
        if deployment._lock:
            deployment._lock = False
        else:
            raise Exception('deployment is already unlocked')

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        provision_deployment = provision_deployments[
            grid.provider].select().where(
            provision_deployments[
                grid.provider].parentgrid == grid).get()
        return ast.literal_eval(str(provision_deployment)), 200

    def put(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_was_not_successful(
            grid_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        parent_deployment = deployments[grid.provider].select().where(
            deployments[grid.provider].parentgrid == grid).get()
        infrastructure_deployment = infrastructure_deployments[
            grid.provider].select().where(
            infrastructure_deployments[
                grid.provider].parentgrid == grid).get()
        if not provision_deployments[grid.provider].select().where(
                        provision_deployments[grid.provider
                        ].parentgrid == grid).exists():
            provision_deployment = provision_deployments[
                grid.provider].create(parentgrid=grid)
        provision_deployment = provision_deployments[
            grid.provider].select().where(
             provision_deployments[
                 grid.provider].parentgrid == grid).get()
        kwargs = provision_deploymentparsers[grid.provider].parse_args()
        cwd = os.getcwd()
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        if grid.provider != 'custom':
            with open('result/{}/infrastructure/terraform.tfstate'.format(
                    grid_name), 'w+') as state_file:
                state_file.write(infrastructure_deployment._state)
        for key in provision_deployment._data.keys():
            if key != 'id' and key != 'parentgrid' and key !=\
                    '_lock' and key != '_status' and key !=\
                    '_accessip' and key != '_state':
                setattr(provision_deployment, key, kwargs[key])
        provision_deployment.save()
        def do_deploy():
            def _run_ansible():
                subprocess.check_call(['ansible-playbook', 'grid.yml'],
                                      cwd='result/{}'.format(grid_name))
            parent_deployment._status = 'provision_deploying'
            provision_deployment._status = 'deploying'
            provision_deployment.save()
            parent_deployment.save()
            provision_generator = provision_generators[grid.type][
                grid.provider](grid_name, **kwargs)
            provision_generator.generate_all(
                grid_name, infrastructure_deployment._accessip)
            try:
                _run_ansible()
            except:
                provision_deployment._status = 'deploy_failed'
                parent_deployment._status = 'provision_deploy_failed'
            else:
                provision_deployment._status = 'deployed'
                parent_deployment._status = 'provision_finished'
            finally:
                provision_deployment.save()
                self.unlock(parent_deployment)
                parent_deployment.save()
                os.chdir(cwd)
                try:
                    del os.environ['AWS_ACCESS_KEY_ID']
                except:
                    print('no such env')
                try:
                    del os.environ['AWS_SECRET_ACCESS_KEY']
                except:
                    print('no such env')
                shutil.rmtree('result/{}'.format(grid_name))
        try:
            self.lock(parent_deployment)
            parent_deployment.save()
        except:
            parent_deployment._status = 'lock_failed'
        else:
            deploy_thread = threading.Thread(
                target=do_deploy, args=(), kwargs={})
            deploy_thread.start()
        return ast.literal_eval(str(provision_deployment)), 200


class GroupProvisionDeploymentHandler(ProvisionDeploymentHandler):
    def _abort_if_group_doesnt_exist(self, grid_name, group_name):
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        if not groups[grid.provider].select().where(
                        groups[grid.provider].name == group_name,
                        groups[grid.provider].parentgrid ==
                        grid).exists():
            abort(404, message="Group {} doesn't exist".format(group_name))

    def lock(self, deployment):
        if not deployment._lock:
            deployment._lock = True
        else:
            raise Exception('deployment is locked')

    def unlock(self, deployment):
        if deployment._lock:
            deployment._lock = False
        else:
            raise Exception('deployment is already unlocked')

    def get(self, grid_name, group_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        self._abort_if_group_doesnt_exist(grid_name, group_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        provision_deployment = provision_deployments[
            grid.provider].select().where(
            provision_deployments[
                grid.provider].parentgrid == grid).get()
        return ast.literal_eval(str(provision_deployment)), 200

    def put(self, grid_name, group_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_group_doesnt_exist(grid_name, group_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_was_not_successful(
            grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        parent_deployment = deployments[grid.provider].select().where(
            deployments[grid.provider].parentgrid == grid).get()
        infrastructure_deployment = infrastructure_deployments[
            grid.provider].select().where(
            infrastructure_deployments[
                grid.provider].parentgrid == grid).get()
        provision_deployment = provision_deployments[
            grid.provider].select().where(
             provision_deployments[
                 grid.provider].parentgrid == grid).get()
        group = groups[grid.provider].select().where(
            groups[grid.provider].name == group_name,
            groups[grid.provider].parentgrid == grid).get()
        kwargs = provision_deploymentparsers[grid.provider].parse_args()
        cwd = os.getcwd()
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        if grid.provider != 'custom':
            with open('result/{}/infrastructure/terraform.tfstate'.format(
                    grid_name), 'w+') as state_file:
                state_file.write(infrastructure_deployment._state)
        provision_deployment.save()
        def do_deploy():
            def _run_ansible():
                subprocess.check_call(['ansible-playbook', 'group_{}.yml'.format(group.role)],
                                      cwd='result/{}'.format(grid_name))
            parent_deployment._status = 'group_provision_deploying'
            provision_deployment._status = 'group_deploying'
            provision_deployment.save()
            parent_deployment.save()
            provision_generator = provision_generators[grid.type][
                grid.provider](grid_name, **kwargs)
            provision_generator.generate_all(
                grid_name, infrastructure_deployment._accessip)
            try:
                _run_ansible()
            except:
                provision_deployment._status = 'group_deploy_failed'
                parent_deployment._status = 'group_provision_deploy_failed'
            else:
                provision_deployment._status = 'group_deployed'
                parent_deployment._status = 'group_provision_finished'
            finally:
                provision_deployment.save()
                self.unlock(parent_deployment)
                parent_deployment.save()
                os.chdir(cwd)
                try:
                    del os.environ['AWS_ACCESS_KEY_ID']
                except:
                    print('no such env')
                try:
                    del os.environ['AWS_SECRET_ACCESS_KEY']
                except:
                    print('no such env')
                shutil.rmtree('result/{}'.format(grid_name))
        try:
            self.lock(parent_deployment)
            parent_deployment.save()
        except:
            parent_deployment._status = 'lock_failed'
        else:
            deploy_thread = threading.Thread(
                target=do_deploy, args=(), kwargs={})
            deploy_thread.start()
        return ast.literal_eval(str(provision_deployment)), 200

