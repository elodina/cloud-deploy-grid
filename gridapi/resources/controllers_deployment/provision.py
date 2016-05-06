import threading
import os
import ast
import subprocess
import shutil
from flask_restful import Resource, abort
from gridapi.resources.parsers import provision_deploymentparsers
from gridapi.resources.models import GridEntity, configs, deployments, infrastructure_deployments, provision_deployments, groups
from gridapi.resources.generators.provision.mesos.aws import aws_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.azure import azure_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.gcs import gcs_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.openstack import openstack_provision_mesos_generator
from gridapi.resources.generators.provision.mesos.custom import custom_provision_mesos_generator
from gridapi.resources.generators.provision.dcos.azure import azure_provision_dcos_generator
from gridapi.resources.generators.provision.dcos.gcs import gcs_provision_dcos_generator
from gridapi.resources.generators.provision.dcos.openstack import openstack_provision_dcos_generator
from gridapi.resources.generators.provision.dcos.aws import aws_provision_dcos_generator
from gridapi.resources.generators.provision.dcos.custom import custom_provision_dcos_generator

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
        'gcs': gcs_provision_dcos_generator,
        'openstack': openstack_provision_dcos_generator,
        'custom': custom_provision_dcos_generator
    }
}

class ProvisionDeploymentHandler(Resource):
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

    def _abort_if_provision_deployment_doesnt_exist(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        if not len(provision_deployments[grid.provider].objects(parentgrid=grid_name)):
            abort(404, message="Provision Deployment of grid {} doesn't exist".format(grid_name))

    def lock(self, deployment):
        if not deployment.lock:
            deployment.lock = True
        else:
            raise Exception('deployment is locked')

    def unlock(self, deployment):
        if deployment.lock:
            deployment.lock = False
        else:
            raise Exception('deployment is already unlocked')

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        provision_deployment = provision_deployments[grid.provider].objects(parentgrid=grid_name).get()
        return ast.literal_eval(str(provision_deployment)), 200

    def put(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_was_not_successful(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        parent_deployment = deployments[grid.provider].objects(parentgrid=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        if not len(provision_deployments[grid.provider].objects(parentgrid=grid_name)):
            provision_deployment = provision_deployments[grid.provider].create(parentgrid=grid_name)
        provision_deployment = provision_deployments[grid.provider].objects(parentgrid=grid_name).get()
        kwargs = provision_deploymentparsers[grid.provider].parse_args()
        cwd = os.getcwd()
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        if grid.provider != 'custom':
            with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'w+') as state_file:
                state_file.write(infrastructure_deployment.tfstate)
        for key in provision_deployment.keys():
            if key != 'parentgrid' and key != 'lock' and key != 'state' and key != 'provider':
                setattr(provision_deployment, key, kwargs[key])
        provision_deployment.save()
        def do_deploy():
            def _run_ansible():
                subprocess.check_call(['ansible-playbook', 'grid.yml'], cwd='result/{}'.format(grid_name))
            parent_deployment.state = 'provision_deploying'
            provision_deployment.state = 'deploying'
            provision_deployment.save()
            parent_deployment.save()
            provision_generator = provision_generators[grid.type][grid.provider](grid_name, **kwargs)
            provision_generator.generate_all(grid_name, infrastructure_deployment.accessip)
            try:
                _run_ansible()
            except:
                provision_deployment.state = 'deploy_failed'
                parent_deployment.state = 'provision_deploy_failed'
            else:
                provision_deployment.state = 'deployed'
                parent_deployment.state = 'provision_finished'
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
            parent_deployment.state = 'lock_failed'
        else:
            deploy_thread = threading.Thread(
                target=do_deploy, args=(), kwargs={})
            deploy_thread.start()
        return ast.literal_eval(str(provision_deployment)), 200


class GroupProvisionDeploymentHandler(ProvisionDeploymentHandler):
    def _abort_if_group_doesnt_exist(self, grid_name, group_name):
        grid = GridEntity.objects(name=grid_name).get()
        if not len(groups[grid.provider].objects(parentgrid=grid_name, name=args['name'])):
            abort(404, message="Group {} doesn't exist".format(group_name))

    def lock(self, deployment):
        if not deployment.lock:
            deployment.lock = True
        else:
            raise Exception('deployment is locked')

    def unlock(self, deployment):
        if deployment.lock:
            deployment.lock = False
        else:
            raise Exception('deployment is already unlocked')

    def get(self, grid_name, group_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        self._abort_if_group_doesnt_exist(grid_name, group_name)
        grid = GridEntity.objects(name=grid_name).get()
        provision_deployment = provision_deployments[grid.provider].objects(parentgrid=grid_name).get()
        return ast.literal_eval(str(provision_deployment)), 200

    def put(self, grid_name, group_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_group_doesnt_exist(grid_name, group_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_was_not_successful(grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        parent_deployment = deployments[grid.provider].objects(parentgrid=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        provision_deployment = provision_deployments[grid.provider].objects(parentgrid=grid_name).get()
        group = groups[grid.provider].objects(parentgrid=grid_name, name=group_name).get()
        kwargs = provision_deploymentparsers[grid.provider].parse_args()
        cwd = os.getcwd()
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        if grid.provider != 'custom':
            with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'w+') as state_file:
                state_file.write(infrastructure_deployment.tfstate)
        provision_deployment.save()
        def do_deploy():
            def _run_ansible():
                subprocess.check_call(['ansible-playbook', 'group_{}.yml'.format(group.role)], cwd='result/{}'.format(grid_name))
            parent_deployment.state = 'group_provision_deploying'
            provision_deployment.state = 'group_deploying'
            provision_deployment.save()
            parent_deployment.save()
            provision_generator = provision_generators[grid.type][grid.provider](grid_name, **kwargs)
            provision_generator.generate_all(grid_name, infrastructure_deployment.accessip)
            try:
                _run_ansible()
            except:
                provision_deployment.state = 'group_deploy_failed'
                parent_deployment.state = 'group_provision_deploy_failed'
            else:
                provision_deployment.state = 'group_deployed'
                parent_deployment.state = 'group_provision_finished'
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
            parent_deployment.state = 'lock_failed'
        else:
            deploy_thread = threading.Thread(target=do_deploy, args=(), kwargs={})
            deploy_thread.start()
        return ast.literal_eval(str(provision_deployment)), 200


class MastersProvisionDeploymentHandler(ProvisionDeploymentHandler):
    def lock(self, deployment):
        if not deployment.lock:
            deployment.lock = True
        else:
            raise Exception('deployment is locked')

    def unlock(self, deployment):
        if deployment.lock:
            deployment.lock = False
        else:
            raise Exception('deployment is already unlocked')

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        provision_deployment = provision_deployments[grid.provider].objects(parentgrid=grid_name).get()
        return ast.literal_eval(str(provision_deployment)), 200

    def put(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_was_not_successful(grid_name)
        self._abort_if_provision_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        parent_deployment = deployments[grid.provider].objects(parentgrid=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        provision_deployment = provision_deployments[grid.provider].objects(parentgrid=grid_name).get()
        kwargs = provision_deploymentparsers[grid.provider].parse_args()
        cwd = os.getcwd()
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        if grid.provider != 'custom':
            with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'w+') as state_file:
                state_file.write(infrastructure_deployment.tfstate)
        provision_deployment.save()

        def do_deploy():
            def _run_ansible():
                subprocess.check_call(['ansible-playbook', 'masters.yml'], cwd='result/{}'.format(grid_name))
            parent_deployment.state = 'masters_provision_deploying'
            provision_deployment.state = 'masters_deploying'
            provision_deployment.save()
            parent_deployment.save()
            provision_generator = provision_generators[grid.type][
                grid.provider](grid_name, **kwargs)
            provision_generator.generate_all(
                grid_name, infrastructure_deployment.accessip)
            try:
                _run_ansible()
            except:
                provision_deployment.state = 'masters_deploy_failed'
                parent_deployment.state = 'masters_provision_deploy_failed'
            else:
                provision_deployment.state = 'masters_deployed'
                parent_deployment.state = 'masters_provision_finished'
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
            parent_deployment.state = 'lock_failed'
        else:
            deploy_thread = threading.Thread(
                target=do_deploy, args=(), kwargs={})
            deploy_thread.start()
        return ast.literal_eval(str(provision_deployment)), 200

