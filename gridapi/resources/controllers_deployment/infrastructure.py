import threading
import json
import os
import ast
import subprocess
import shutil
import urllib
from retrying import retry
from flask_restful import Resource, abort
from gridapi.resources.parsers import infrastructure_deploymentparsers
from gridapi.resources.models import GridEntity, configs, deployments, groups, infrastructure_deployments
from gridapi.resources.generators.infrastructure.aws import aws_infrastructure_generator
from gridapi.resources.generators.infrastructure.azure import azure_infrastructure_generator
from gridapi.resources.generators.infrastructure.gcs import gcs_infrastructure_generator
from gridapi.resources.generators.infrastructure.openstack import openstack_infrastructure_generator
from gridapi.resources.generators.infrastructure.custom import custom_infrastructure_generator

infrastructure_generators = {
    'aws': aws_infrastructure_generator,
    'azure': azure_infrastructure_generator,
    'gcs': gcs_infrastructure_generator,
    'openstack': openstack_infrastructure_generator,
    'custom': custom_infrastructure_generator
}

class InfrastructureDeploymentHandler(Resource):
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
        print(infrastructure_deployments[grid.provider])
        print(len(infrastructure_deployments[grid.provider].objects(parentgrid=grid_name)))
        if not len(infrastructure_deployments[grid.provider].objects(parentgrid=grid_name)):
            abort(404, message="Infrastructure Deployment of grid {} doesn't exist".format(grid_name))

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
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        infrastructure_deployment['tfstate'] = 'hidden'
        return ast.literal_eval(str(infrastructure_deployment)), 200

    def delete(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        parent_deployment = deployments[grid.provider].objects(parentgrid=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        args = infrastructure_deploymentparsers[grid.provider].parse_args()
        cwd = os.getcwd()
        def do_destroy():
            parent_deployment.state = 'infrastructure_destroying'
            infrastructure_deployment.state = 'destroying'
            infrastructure_deployment.save()
            parent_deployment.save()
            deployment_generator = infrastructure_generators[grid.provider](grid_name, **args)
            deployment_generator.generate_all()

            @retry(stop_max_attempt_number=5, wait_fixed=10000)
            def _run_terraform_destroy():
                subprocess.check_call([
                    'terraform',
                    'destroy',
                    '-force',
                    '-state=result/{}/infrastructure/terraform.tfstate'.format(grid_name),
                    'result/{}/infrastructure'.format(grid_name)])

            try:
                if infrastructure_deployment.tfstate is not None:
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'w+') as state_file:
                        state_file.write(infrastructure_deployment.tfstate)
                _run_terraform_destroy()
                with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as state_file:
                    infrastructure_deployment.tfstate = state_file.read()
                parent_deployment.state = 'destroyed'
                infrastructure_deployment.state = 'destroyed'
            except:
                parent_deployment.state = 'destroy_failed'
                infrastructure_deployment.state = 'destroy_failed'
            finally:
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
            if grid.provider != 'custom':
                destroy_thread = threading.Thread(target=do_destroy, args=(), kwargs={})
                destroy_thread.start()
            infrastructure_deployment.delete()
        return '', 200

    def put(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_deployment_doesnt_exist(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        parent_deployment = deployments[grid.provider].objects(parentgrid=grid_name).get()
        if not len(infrastructure_deployments[grid.provider].objects(parentgrid=grid_name)):
            infrastructure_deployment = infrastructure_deployments[grid.provider].create(parentgrid=grid_name)
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        args = infrastructure_deploymentparsers[grid.provider].parse_args()
        cwd = os.getcwd()
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        for key in infrastructure_deployment.keys():
            if key != 'parentgrid' and key != 'lock' and key != 'state' and key != 'tfstate' and key != 'accessip' and key != 'provider':
                setattr(infrastructure_deployment, key, urllib.unquote(args[key]))
        infrastructure_deployment.save()
        def do_deploy():
            def _aws_get_access_ip(grid_name):
                terminal_ip = 'dummy'
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if resource == 'aws_eip.terminal':
                                    terminal_ip = value['primary']['attributes']['public_ip']
                if terminal_ip == 'dummy':
                    raise Exception('No terminal ip detected')
                else:
                    return terminal_ip

            def _azure_get_access_ip(grid_name):
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if resource == 'azure_instance.terminal':
                                    return value['primary']['attributes']['vip_address']

            def _gcs_get_access_ip(grid_name):
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if resource == 'google_compute_instance.{}-terminal'.format(grid_name):
                                    return value['primary']['attributes']['network_interface.0.access_config.0.assigned_nat_ip']

            def _openstack_get_access_ip(grid_name):
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if resource == 'openstack_compute_instance_v2.{}-terminal'.format(grid_name):
                                    return value['primary']['attributes']['floating_ip']

            def _custom_get_access_ip(grid_name):
                grid_config = configs[grid.provider].objects(parentgrid=grid_name).get()
                terminal_ips = grid_config.terminalips.split(',')
                return terminal_ips[0]

            get_access_ip = {
                'aws': _aws_get_access_ip,
                'azure': _azure_get_access_ip,
                'gcs': _gcs_get_access_ip,
                'openstack': _openstack_get_access_ip,
                'custom': _custom_get_access_ip
            }

            @retry(stop_max_attempt_number=30, wait_fixed=5000)
            def _aws_check_host(host, grid_name):
                try:
                    subprocess.check_call([
                        'ssh', '-F', 'result/{}/ssh_config'.format(grid_name),
                        '-o', 'UserKnownHostsFile=/dev/null',
                        '-o', 'StrictHostKeyChecking=no',
                        '-o', 'PasswordAuthentication=no',
                        '-o', 'ConnectTimeout=10',
                        '{}'.format(host), 'exit'])
                    print('{} is online'.format(host))
                except:
                    print('{} is offline'.format(host))
                    raise Exception('host is offline')

            @retry(stop_max_attempt_number=30, wait_fixed=5000)
            def _azure_check_host(host):
                try:
                    subprocess.check_call(['tcping', '-q', '-t', '1', '{}'.format(host), '22'])
                except:
                    raise Exception('host is offline')

            @retry(stop_max_attempt_number=30, wait_fixed=5000)
            def _gcs_check_host(host):
                try:
                    subprocess.check_call([
                        'ssh', '-F', 'result/{}/ssh_config'.format(grid_name),
                        '-o', 'UserKnownHostsFile=/dev/null',
                        '-o', 'StrictHostKeyChecking=no',
                        '-o', 'PasswordAuthentication=no',
                        '-o', 'ConnectTimeout=10',
                        '{}'.format(host), 'exit'])
                    print('{} is online'.format(host))
                except:
                    print('{} is offline'.format(host))
                    raise Exception('host is offline')

            @retry(stop_max_attempt_number=30, wait_fixed=5000)
            def _openstack_check_host(host):
                try:
                    subprocess.check_call([
                        'ssh', '-F', 'result/{}/ssh_config'.format(grid_name),
                        '-o', 'UserKnownHostsFile=/dev/null',
                        '-o', 'StrictHostKeyChecking=no',
                        '-o', 'PasswordAuthentication=no',
                        '-o', 'ConnectTimeout=10',
                        '{}'.format(host), 'exit'])
                    print('{} is online'.format(host))
                except:
                    print('{} is offline'.format(host))
                    raise Exception('host is offline')

            @retry(stop_max_attempt_number=30, wait_fixed=5000)
            def _custom_check_host(host, grid_name):
                try:
                    subprocess.check_call([
                        'ssh', '-F', 'result/{}/ssh_config'.format(grid_name),
                        '-o', 'UserKnownHostsFile=/dev/null',
                        '-o', 'StrictHostKeyChecking=no',
                        '-o', 'PasswordAuthentication=no',
                        '-o', 'ConnectTimeout=10',
                        '{}'.format(host), 'exit'])
                    print('{} is online'.format(host))
                except:
                    print('{} is offline'.format(host))
                    raise Exception('host is offline')

            check_host = {
                'aws': _aws_check_host,
                'azure': _azure_check_host,
                'gcs': _gcs_check_host,
                'openstack': _openstack_check_host,
                'custom': _custom_check_host
            }

            def _aws_check_hosts_online(grid_name):
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if value['type'] == 'aws_instance':
                                    ip = value['primary']['attributes']['private_ip']
                                    check_host[grid.provider](ip, grid_name)

            def _azure_check_hosts_online(grid_name):
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), "r") as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if value['type'] == 'azure_instance':
                                    ip = value['primary']['attributes']['vip_address']
                                    check_host[grid.provider](ip)

            def _gcs_check_hosts_online(grid_name):
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), "r") as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if value['type'] == 'google_compute_instance':
                                    ip = value['primary']['attributes']['network_interface.0.address']
                                    check_host[grid.provider](ip)

            def _openstack_check_hosts_online(grid_name):
                if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(grid_name), os.R_OK):
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), "r") as json_file:
                        json_data = json.load(json_file)
                        for module in json_data['modules']:
                            for resource, value in module['resources'].iteritems():
                                if value['type'] == 'openstack_compute_instance_v2':
                                    ip = value['primary']['attributes']['network.0.fixed_ip_v4']
                                    check_host[grid.provider](ip)

            def _custom_check_hosts_online(grid_name):
                all_ips = []
                grid_config = configs[grid.provider].objects(parentgrid=grid_name).get()
                all_ips.append(grid_config.terminalips.split(',')[1])
                all_ips.extend(grid_config.mastersips.split(','))
                for group in groups[grid.provider].objects(parentgrid=grid_name):
                    all_ips.extend(group.groupips.split(','))
                for ip in all_ips:
                    check_host[grid.provider](ip, grid_name)

            check_hosts_online = {
                'aws': _aws_check_hosts_online,
                'azure': _azure_check_hosts_online,
                'gcs': _gcs_check_hosts_online,
                'openstack': _openstack_check_hosts_online,
                'custom': _custom_check_hosts_online
            }

            def generate_ssh_config(access_ip):
                import jinja2
                grid_config = configs[grid.provider].objects(parentgrid=grid_name).get()
                ssh_user = grid_config.ssh_user
                os.system('cp -a -f gridapi/resources/templates/infrastructure/* result/{}'.format(grid_name))
                path = 'result/{}/ssh_config'.format(grid_name)
                with open(path, 'r') as src:
                    template = jinja2.Template(src.read())
                template_content = template.render(access_ip=access_ip, user=ssh_user)
                with open(path, 'w') as dst:
                    dst.write(template_content)

            def _run_terraform_deploy():
                command = [
                    'terraform',
                    'apply',
                    '-parallelism={}'.format(args['parallelism']),
                    '-state=result/{}/infrastructure/terraform.'
                    'tfstate'.format(grid_name),
                    'result/{}/infrastructure'.format(grid_name)]
                subprocess.check_call(command)
            parent_deployment.state = 'infrastructure_deploying'
            infrastructure_deployment.state = 'deploying'
            infrastructure_deployment.save()
            parent_deployment.save()
            infrastructure_generator = infrastructure_generators[grid.provider](grid_name, **args)
            infrastructure_generator.generate_all()
            try:
                if grid.provider != 'custom':
                    if infrastructure_deployment.tfstate is not None:
                        with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'w+') as state_file:
                            state_file.write(infrastructure_deployment.tfstate)
                    _run_terraform_deploy()
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as state_file:
                        infrastructure_deployment.tfstate = state_file.read()
                    infrastructure_deployment.save()
                infrastructure_deployment.accessip = get_access_ip[grid.provider](grid_name)
                infrastructure_deployment.save()
                generate_ssh_config(infrastructure_deployment.accessip)
                check_hosts_online[grid.provider](grid_name)
            except:
                infrastructure_deployment.state = 'deploy_failed'
                parent_deployment.state = 'infrastructure_deploy_failed'
            else:
                infrastructure_deployment.state = 'deployed'
                parent_deployment.state = 'infrastructure_deployed'
            finally:
                if grid.provider != 'custom':
                    with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as state_file:
                        infrastructure_deployment.tfstate = state_file.read()
                infrastructure_deployment.save()
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
        return ast.literal_eval(str(infrastructure_deployment)), 200


class ExportInfrastructureDeploymentHandler(InfrastructureDeploymentHandler):
    def _abort_if_infrastructure_deployment_was_not_successful(self, grid_name):
        grid = GridEntity.objects(name=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()
        if infrastructure_deployment.state != 'deployed':
            abort(404, message="Infrastructure Deployment of grid need to be successful first".format(grid_name))

    def get(self, grid_name):
        self._abort_if_grid_doesnt_exist(grid_name)
        self._abort_if_config_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_doesnt_exist(grid_name)
        self._abort_if_infrastructure_deployment_was_not_successful(grid_name)
        grid = GridEntity.objects(name=grid_name).get()
        infrastructure_deployment = infrastructure_deployments[grid.provider].objects(parentgrid=grid_name).get()

        def _aws_hosts_export(grid_name):
            export = []
            with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as input_file:
                state = json.load(input_file)
                for module in state['modules']:
                    for resource, value in module['resources'].iteritems():
                        if value['type'] == 'aws_instance' or value['type'] == 'aws_spot_instance_request':
                            ip = value['primary']['attributes']['private_ip']
                            export.append(('.'.join(resource.split('.')[1:]), ip))
            export.sort(key=lambda(x): x[0])
            return export

        def _azure_hosts_export(grid_name):
            export = []
            with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as input_file:
                state = json.load(input_file)
                for module in state['modules']:
                    for resource, value in module['resources'].iteritems():
                        if value['type'] == 'azure_instance':
                            ip = value['primary']['attributes']['vip_address']
                            export.append(('.'.join(resource.split('.')[1:]), ip))
            export.sort(key=lambda(x): x[0])
            return export

        def _gcs_hosts_export(grid_name):
            export = []
            with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as input_file:
                state = json.load(input_file)
                for module in state['modules']:
                    for resource, value in module['resources'].iteritems():
                        if value['type'] == 'google_compute_instance':
                            ip = value['primary']['attributes']['network_interface.0.address']
                            export.append(('.'.join(resource.split('.')[1:]), ip))
            export.sort(key=lambda(x): x[0])
            return export

        def _openstack_hosts_export(grid_name):
            export = []
            with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as input_file:
                state = json.load(input_file)
                for module in state['modules']:
                    for resource, value in module['resources'].iteritems():
                        if value['type'] == 'openstack_compute_instance_v2':
                            ip = value['primary']['attributes']['network.0.fixed_ip_v4']
                            export.append(('.'.join(resource.split('.')[1:]), ip))
            export.sort(key=lambda(x): x[0])
            return export

        def _custom_hosts_export(grid_name):
            export = []
            grid_config = configs[grid.provider].objects(parentgrid=grid_name).get()
            export.append(('terminal', grid_config.terminalips.split(',')[1]))
            for ip in grid_config.mastersips.split(','):
                export.append(('master', ip))
            for group in groups[grid.provider].objects(parentgrid=grid_name):
                for ip in group.groupips.split(','):
                    export.append(('group_{}_host'.format(group.name), ip))
            return export

        hosts_export = {
            'aws': _aws_hosts_export,
            'azure': _azure_hosts_export,
            'gcs': _gcs_hosts_export,
            'openstack': _openstack_hosts_export,
            'custom': _custom_hosts_export
        }
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'w+') as state_file:
            state_file.write(infrastructure_deployment.tfstate)
        with open('result/{}/infrastructure/terraform.tfstate'.format(grid_name), 'r') as state_file:
            export = hosts_export[grid.provider](grid_name)
        shutil.rmtree('result/{}'.format(grid_name))
        return ast.literal_eval(str(export)), 200
