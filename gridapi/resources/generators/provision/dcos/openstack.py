import json
import jinja2
import os
import yaml
import subprocess
import urllib
from gridapi.resources.models import GridEntity, configs, groups

class AutoDict(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class openstack_provision_dcos_generator(object):
    def __init__(self, grid_name, **kwargs):
        self.grid_name = grid_name
        self.kwargs = kwargs
        self.current_grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        self.current_config = configs[
            self.current_grid.provider].select().where(
            configs[self.current_grid.provider].parentgrid ==
            self.current_grid).get()
        self.current_groups = []
        self.current_roles = []
        for group in groups[self.current_grid.provider].select():
            if group.parentgrid.name == grid_name:
                self.current_groups.append(group)
                self.current_roles.append(group.role)

    def _nameserver(self):
        if os.path.isfile('result/{}/infrastructure/terraform.tfstate'.format(self.grid_name)) and os.access('result/{}/infrastructure/terraform.tfstate'.format(self.grid_name), os.R_OK):
            with open('result/{}/infrastructure/terraform.tfstate'.format(self.grid_name), 'r') as json_file:
                json_data = json.load(json_file)
                for module in json_data['modules']:
                    for resource, value in module['resources'].iteritems():
                        if resource == 'openstack_compute_instance_v2.{}-terminal'.format(self.grid_name):
                            return value['primary']['attributes']['network.0.fixed_ip_v4']

    def copy_templates(self):
        os.system('cp -a -f gridapi/resources/templates/provision/dcos/openstack/* result/{}'.format(self.grid_name))

    def _generate_template(self, filepath, variables):
        with open(filepath, 'r') as src:
            template = jinja2.Template(src.read())
        template_content = template.render(**variables)
        with open(filepath, 'w') as dst:
            dst.write(template_content)

    def generate_ansible_cfg(self):
        path = 'result/{}/ansible.cfg'.format(self.grid_name)
        variables = {}
        variables['ssh_user'] = self.current_config.ssh_user
        self._generate_template(path, variables)

    def generate_ansible_ssh_config(self, access_ip):
        path = 'result/{}/ansible/ssh_config'.format(self.grid_name)
        variables = {}
        variables['ssh_user'] = self.current_config.ssh_user
        variables['access_ip'] = access_ip
        self._generate_template(path, variables)

    def generate_ssh_key(self):
        with open('result/{}/grid.pem'.format(
                self.grid_name), 'w+') as ssh_key:
            ssh_key.write(urllib.unquote(self.current_config.sshkeydata))

    def generate_group_vars_all(self):
        path = 'result/{}/group_vars/all'.format(self.grid_name)
        variables = AutoDict()
        hosts_entries = AutoDict()
        with open('result/{}/infrastructure/terraform.tfstate'.format(
                self.grid_name), 'r') as json_file:
            json_data = json.load(json_file)
            for module in json_data['modules']:
                for resource, value in module['resources'].iteritems():
                    if value['type'] == 'openstack_compute_instance_v2':
                        host = '{}.node.{}'.format(
                            value['primary']['attributes'][
                                'name'], self.grid_name)
                        ip = value['primary']['attributes']['network.0.fixed_ip_v4']
                        hosts_entries['hosts'][str(host)] = str(ip)
        variables['hosts'] = json.dumps(hosts_entries['hosts'])
        variables['grid_name'] = self.current_grid.name
        variables['terminal_ip'] = self._nameserver()
        self._generate_template(path, variables)
        vars_json = json.loads(self.current_config.vars)
        vars_yaml = yaml.safe_dump(vars_json, default_flow_style=False)
        with open(path, "a") as yaml_file:
            yaml_file.write(vars_yaml)

    def generate_group_vars_roles(self):
        for role in self.current_roles:
            src = 'result/{}/group_vars/dcos_slaves'.format(self.grid_name)
            dst = 'result/{}/group_vars/tag_role_{}_{}'.format(
                self.grid_name, self.grid_name, role)
            os.system('cp -a -f {src} {dst}'.format(src=src, dst=dst))

    def _generate_attributes_for_group(self, group):
        content = []
        content.append('role: {}'.format(group.role))
        attributes_json = json.loads(group.attributes)
        for attribute, value in attributes_json.iteritems():
            content.append('{}: {}'.format(attribute, value))
        return '\n'.join(content)

    def generate_roles_provision(self):
        for group in self.current_groups:
            role = group.role
            src = 'result/{}/roles/dcos'.format(self.grid_name)
            dst = 'result/{}/roles/dcos-slave_{}_{}'.format(
                self.grid_name, self.grid_name, role)
            os.system('cp -a -f {src} {dst}'.format(src=src, dst=dst))
            with open('{}/files/etc/mesos_slave/attributes'.format(
                    dst), 'w+') as attributes_file:
                attributes_file.write(
                    self._generate_attributes_for_group(group))

    def generate_inventory_grid(self):
        path = 'result/{}/inventory/grid'.format(self.grid_name)
        variables = {}
        variables['grid_name'] = self.current_grid.name
        variables['roles'] = self.current_roles
        self._generate_template(path, variables)

    def generate_grid_runlist(self):
        path = 'result/{}/grid.yml'.format(self.grid_name)
        variables = {}
        variables['grid_name'] = self.grid_name
        variables['roles'] = self.current_roles
        self._generate_template(path, variables)

    def generate_groups_runlists(self):
        for group in self.current_groups:
            src = 'result/{}/group.yml'.format(self.grid_name)
            dst = 'result/{}/group_{}.yml'.format(
                self.grid_name, group.role)
            os.system('cp -a -f {src} {dst}'.format(src=src, dst=dst))
            variables = {}
            variables['grid_name'] = self.grid_name
            variables['role'] = group.role
            self._generate_template(dst, variables)

    def generate_all(self, grid_name, access_ip):
        self.copy_templates()
        self.generate_ansible_cfg()
        self.generate_ansible_ssh_config(access_ip)
        self.generate_ssh_key()
        self.generate_group_vars_all()
        self.generate_group_vars_roles()
        self.generate_roles_provision()
        self.generate_inventory_grid()
        self.generate_grid_runlist()
        self.generate_groups_runlists()
        os.chmod('result/{}/grid.pem'.format(self.grid_name), 0600)
        subprocess.check_call(['ssh-add', 'result/{}/grid.pem'.format(
            self.grid_name)])