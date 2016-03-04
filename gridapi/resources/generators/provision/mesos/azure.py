import json
import jinja2
import os
from gridapi.resources.models import GridEntity, configs, groups

class AutoDict(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class azure_provision_mesos_generator(object):
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

    def copy_templates(self):
        os.system('cp -a -f'
                  ' gridapi/resources/templates/provision/mesos/azure/*'
                  ' result/{}'.format(self.grid_name))

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

    def generate_openvpn_authenticator(self):
        path = 'result/{}/roles/openvpn/templates/etc/openvpn/duoauth.py'.format(self.grid_name)
        variables = {}
        if self.kwargs['duo_ikey'] != '' and self.kwargs['duo_skey'] != 0 and self.kwargs['duo_host'] != 0:
            variables['enable_duo'] = 'True'
            variables['duo_ikey'] = self.kwargs['duo_ikey']
            variables['duo_skey'] = self.kwargs['duo_skey']
            variables['duo_host'] = self.kwargs['duo_host']
        else:
            variables['enable_duo'] = 'False'
            variables['duo_ikey'] = ''
            variables['duo_skey'] = ''
            variables['duo_host'] = ''
        self._generate_template(path, variables)

    def generate_group_vars_all(self):
        path = 'result/{}/group_vars/all'.format(self.grid_name)
        variables = AutoDict()
        hosts_entries = AutoDict()
        vars_json = json.loads(self.current_config.vars)
        with open('result/{}/infrastructure/terraform.tfstate'.format(
                self.grid_name), 'r') as json_file:
            json_data = json.load(json_file)
            for module in json_data['modules']:
                for resource, value in module['resources'].iteritems():
                    if value['type'] == 'azure_instance':
                        host = '{}.node.{}'.format(
                            value['primary']['attributes'][
                                'name'], self.grid_name)
                        ip = value['primary']['attributes']['ip_address']
                        hosts_entries['hosts'][str(host)] = str(ip)
        variables['hosts'] = json.dumps(hosts_entries['hosts'])
        variables['grid_name'] = self.current_grid.name
        variables['other_vars'] = json.dumps(vars_json)
        self._generate_template(path, variables)

    def generate_group_vars_roles(self):
        for role in self.current_roles:
            src = 'result/{}/group_vars/mesos-slaves'.format(self.grid_name)
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
            src = 'result/{}/roles/mesos'.format(self.grid_name)
            dst = 'result/{}/roles/mesos-slave_{}_{}'.format(
                self.grid_name, self.grid_name, role)
            os.system('cp -a -f {src} {dst}'.format(src=src, dst=dst))
            with open('{}/files/etc/mesos-slave/attributes'.format(
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
        variables['vpn_enabled'] = self.kwargs['vpn_enabled']
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

    def generate_all(self, grid_name, accessip):
        self.copy_templates()
        self.generate_ansible_cfg()
        self.generate_openvpn_authenticator()
        self.generate_group_vars_all()
        self.generate_group_vars_roles()
        self.generate_roles_provision()
        self.generate_inventory_grid()
        self.generate_grid_runlist()
        self.generate_groups_runlists()
