import ast
import json
import os
import urllib
from gridapi.resources.models import GridEntity, configs, groups


class AutoDict(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class azure_infrastructure_generator(object):
    def __init__(self, grid_name, credentials, **kwargs):
        self.grid_name = grid_name
        self.credentials = urllib.unquote(credentials)
        self.current_grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        self.current_config = configs[
            self.current_grid.provider].select().where(
            configs[self.current_grid.provider].parentgrid ==
            self.current_grid).get()
        self.current_groups = []
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        for group in groups[self.current_grid.provider].select():
            if group.parentgrid.name == grid_name:
                self.current_groups.append(group)
        self.config = AutoDict()
        self.networking = AutoDict()
        self.security = AutoDict()
        self.storage = AutoDict()
        self.terminal = AutoDict()
        self.masters = AutoDict()

    def generate_config(self):
        self.config['provider']['azure']['publish_settings'] = \
            self.credentials
        self.config['variable']['location'][
            'default'] = self.current_config.location
        self.config['variable']['grid_name'][
            'default'] = self.current_config.parentgrid.name
        self.config['variable']['ssh_user'][
            'default'] = self.current_config.ssh_user
        self.config['variable']['ssh_password'][
            'default'] = self.current_config.ssh_password
        self.config['variable']['vm_image']['default'] = 'OpenLogic 7.1'
        with open('result/{}/infrastructure/config.tf'.format(
                self.grid_name), 'w') as config_file:
            json.dump(self.config, config_file)

    def generate_networking(self):
        self.networking['resource']['azure_virtual_network']['{}nts'.format(
            self.grid_name)]['name'] = '${var.grid_name}_net'
        self.networking['resource']['azure_virtual_network']['{}nts'.format(
            self.grid_name)]['address_space'] = ['172.28.0.0/16']
        self.networking['resource']['azure_virtual_network']['{}nts'.format(
            self.grid_name)]['location'] = '${var.location}'
        self.networking['resource']['azure_virtual_network']['{}nts'.format(
            self.grid_name)]['subnet'][
            'name'] = '${var.grid_name}_net_subnet_1'
        self.networking['resource']['azure_virtual_network']['{}nts'.format(
            self.grid_name)]['subnet']['address_prefix'] = '172.28.0.0/20'
        with open('result/{}/infrastructure/networking.tf'.format(
                self.grid_name), 'w') as networking_file:
            json.dump(self.networking, networking_file)

    def generate_security(self):
        self.security['variable']['foo']['default'] = 'bar'
        with open('result/{}/infrastructure/security.tf'.format(
                self.grid_name), 'w') as security_file:
            json.dump(self.security, security_file)

    def generate_storage(self):
        self.storage['resource']['azure_storage_service']['{}sts'.format(
            self.grid_name)]['name'] = '{}sts'.format(self.grid_name)
        self.storage['resource']['azure_storage_service']['{}sts'.format(
            self.grid_name)]['location'] = '${var.location}'
        self.storage['resource']['azure_storage_service']['{}sts'.format(
            self.grid_name)]['account_type'] = 'Premium_LRS'
        with open('result/{}/infrastructure/storage.tf'.format(
                self.grid_name), 'w') as storage_file:
            json.dump(self.storage, storage_file)

    def generate_terminal(self):
        self.terminal['resource']['azure_hosted_service']['terminal'][
            'name'] = '${var.grid_name}-terminal'
        self.terminal['resource']['azure_hosted_service']['terminal'][
            'location'] = '${var.location}'
        self.terminal['resource']['azure_hosted_service']['terminal'][
            'ephemeral_contents'] = 'false'
        self.terminal['resource']['azure_hosted_service']['terminal'][
            'description'] = '${var.grid_name} Terminal Server'
        self.terminal['resource']['azure_hosted_service']['terminal'][
            'label'] = '${var.grid_name}-terminal'
        self.terminal['resource']['azure_instance']['terminal'][
            'name'] = '${var.grid_name}-terminal'
        self.terminal['resource']['azure_instance']['terminal'][
            'description'] = '{{ \"dc\": \"${{var.grid_name}}\", \"role\"' \
                             ': \"{}_terminal\" }}'.format(self.grid_name)
        self.terminal['resource']['azure_instance']['terminal'][
            'hosted_service_name'] = '${azure_hosted_service.terminal.name}'
        self.terminal['resource']['azure_instance']['terminal'][
            'image'] = '${var.vm_image}'
        self.terminal['resource']['azure_instance']['terminal'][
            'size'] = 'Standard_DS1'
        self.terminal['resource']['azure_instance']['terminal'][
            'location'] = '${var.location}'
        self.terminal['resource']['azure_instance']['terminal'][
            'username'] = '${var.ssh_user}'
        self.terminal['resource']['azure_instance']['terminal'][
            'password'] = '${var.ssh_password}'
        self.terminal['resource']['azure_instance']['terminal'][
            'virtual_network'] =\
            '${{azure_virtual_network.{}nts.name}}'.format(self.grid_name)
        self.terminal['resource']['azure_instance']['terminal'][
            'storage_service_name'] =\
            '${{azure_storage_service.{}sts.name}}'.format(self.grid_name)
        self.terminal['resource']['azure_instance']['terminal'][
            'subnet'] = '${var.grid_name}_net_subnet_1'
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'] = []
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'SSH', 'protocol': 'tcp',
                                'public_port': '22', 'private_port': '22'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'HTTP', 'protocol': 'tcp',
                                'public_port': '80', 'private_port': '80'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'HTTPS', 'protocol': 'tcp',
                                'public_port': '443', 'private_port': '443'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'TINCVPNTCP', 'protocol': 'tcp',
                                'public_port': '655', 'private_port': '655'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'TINCVPN', 'protocol': 'udp',
                                'public_port': '655', 'private_port': '655'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'VPN', 'protocol': 'udp',
                                'public_port': '1194', 'private_port': '1194'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'PORT10000',
                                'protocol': 'tcp', 'public_port': '10000',
                                'private_port': '10000'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'PORT11000',
                                'protocol': 'tcp', 'public_port': '11000',
                                'private_port': '11000'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'PORT12000',
                                'protocol': 'tcp', 'public_port': '12000',
                                'private_port': '12000'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'PORT13000',
                                'protocol': 'tcp', 'public_port': '13000',
                                'private_port': '13000'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'PORT14000',
                                'protocol': 'tcp', 'public_port': '14000',
                                'private_port': '14000'})
        self.terminal['resource']['azure_instance']['terminal'][
            'endpoint'].append({'name': 'PORT15000',
                                'protocol': 'tcp', 'public_port': '15000',
                                'private_port': '15000'})
        self.terminal['resource']['azure_instance']['terminal'][
            'depends_on'] = ['azure_virtual_network.{}nts'.format(
                self.grid_name), 'azure_storage_service.{}sts'.format(
                self.grid_name), 'azure_hosted_service.terminal']
        with open('result/{}/infrastructure/terminal.tf'.format(
                self.grid_name), 'w') as terminal_file:
            json.dump(self.terminal, terminal_file)

    def generate_masters(self):
        self.masters['resource']['azure_hosted_service']['mesos_master'][
            'count'] = '{}'.format(self.current_config.masters)
        self.masters['resource']['azure_hosted_service']['mesos_master'][
            'name'] = '${var.grid_name}-mesos-master-${count.index}'
        self.masters['resource']['azure_hosted_service']['mesos_master'][
            'location'] = '${var.location}'
        self.masters['resource']['azure_hosted_service']['mesos_master'][
            'ephemeral_contents'] = 'false'
        self.masters['resource']['azure_hosted_service']['mesos_master'][
            'description'] = '${var.grid_name} Mesos Master'
        self.masters['resource']['azure_hosted_service']['mesos_master'][
            'label'] = '${var.grid_name}-mesos-master-${count.index}'
        self.masters['resource']['azure_instance']['mesos_master'][
            'count'] = '{}'.format(self.current_config.masters)
        self.masters['resource']['azure_instance']['mesos_master'][
            'name'] = '${var.grid_name}-mesos-master-${count.index}'
        self.masters['resource']['azure_instance']['mesos_master'][
            'description'] = '{{ \"dc\": \"${{var.grid_name}}\", \"role\"' \
                             ': \"{}_mesos_master\" }}'.format(
            self.grid_name)
        self.masters['resource']['azure_instance']['mesos_master'][
            'hosted_service_name'] =\
            '${element(azure_hosted_service.mesos_master.*.name, count.index)}'
        self.masters['resource']['azure_instance']['mesos_master'][
            'storage_service_name'] =\
            '${{azure_storage_service.{}sts.name}}'.format(self.grid_name)
        self.masters['resource']['azure_instance']['mesos_master'][
            'image'] = '${var.vm_image}'
        self.masters['resource']['azure_instance']['mesos_master'][
            'size'] = '{}'.format(self.current_config.master_type)
        self.masters['resource']['azure_instance']['mesos_master'][
            'location'] = '${var.location}'
        self.masters['resource']['azure_instance']['mesos_master'][
            'username'] = '${var.ssh_user}'
        self.masters['resource']['azure_instance']['mesos_master'][
            'password'] = '${var.ssh_password}'
        self.masters['resource']['azure_instance']['mesos_master'][
            'virtual_network'] =\
            '${{azure_virtual_network.{}nts.name}}'.format(self.grid_name)
        self.masters['resource']['azure_instance']['mesos_master'][
            'subnet'] = '${var.grid_name}_net_subnet_1'
        self.masters['resource']['azure_instance']['mesos_master'][
            'endpoint']['name'] = 'SSH'
        self.masters['resource']['azure_instance']['mesos_master'][
            'endpoint']['protocol'] = 'tcp'
        self.masters['resource']['azure_instance']['mesos_master'][
            'endpoint']['public_port'] = '22'
        self.masters['resource']['azure_instance']['mesos_master'][
            'endpoint']['private_port'] = '22'
        self.masters['resource']['azure_instance']['mesos_master'][
            'depends_on'] = ['azure_virtual_network.{}nts'.format(
                self.grid_name), 'azure_storage_service.{}sts'.format(
                self.grid_name), 'azure_hosted_service.mesos_master']
        with open('result/{}/infrastructure/masters.tf'.format(
                self.grid_name), 'w') as masters_file:
            json.dump(self.masters, masters_file)

    def generate_groups(self):
        for group in self.current_groups:
            group_export = AutoDict()
            group_export['resource']['azure_hosted_service'][
                'mesos_group_{}'.format(group.name)]['count'] = '{}'.format(
                group._slaves)
            group_export['resource']['azure_hosted_service'][
                'mesos_group_{}'.format(group.name)]['name'] =\
                '${{var.grid_name}}-{}-${{count.index}}'.format(group.name)
            group_export['resource']['azure_hosted_service'][
                'mesos_group_{}'.format(group.name)][
                'location'] = '${var.location}'
            group_export['resource']['azure_hosted_service'][
                'mesos_group_{}'.format(group.name)][
                'ephemeral_contents'] = 'false'
            group_export['resource']['azure_hosted_service'][
                'mesos_group_{}'.format(group.name)][
                'description'] = '${var.grid_name} Mesos Master'
            group_export['resource']['azure_hosted_service'][
                'mesos_group_{}'.format(group.name)][
                'label'] = '${{var.grid_name}}-{}-${{count.index}}'.format(
                group.name)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)]['count'] = '{}'.format(
                group._slaves)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)]['name'] =\
                '${{var.grid_name}}-{}-${{count.index}}'.format(group.name)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)]['description'] =\
                '{{ \"dc\": \"${{var.grid_name}}\", \"role\": \"{}_{}\"' \
                ' }}'.format(self.grid_name, group.role)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)]['hosted_service_name'] =\
                '${{element(azure_hosted_service.mesos_group_{}.*.name,' \
                ' count.index)}}'.format(group.name)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'image'] = '${var.vm_image}'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)]['size'] = '{}'.format(
                group.instance_type)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'location'] = '${var.location}'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'username'] = '${var.ssh_user}'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'password'] = '${var.ssh_password}'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'virtual_network'] =\
                '${{azure_virtual_network.{}nts.name}}'.format(
                    self.grid_name)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'storage_service_name'] =\
                '${{azure_storage_service.{}sts.name}}'.format(
                    self.grid_name)
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'subnet'] = '${var.grid_name}_net_subnet_1'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'endpoint']['name'] = 'SSH'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'endpoint']['protocol'] = 'tcp'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'endpoint']['public_port'] = '22'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)][
                'endpoint']['private_port'] = '22'
            group_export['resource']['azure_instance'][
                'mesos_group_{}'.format(group.name)]['depends_on'] = [
                'azure_virtual_network.{}nts'.format(self.grid_name),
                'azure_storage_service.{}sts'.format(self.grid_name),
                'azure_hosted_service.mesos_group_{}'.format(group.name)]
            if group.customhwconf is not None:
                group_export['resource']['azure_instance'][
                    'mesos_group_{}'.format(group.name)].update(
                    ast.literal_eval(group.customhwconf))
            with open('result/{}/infrastructure/{}.tf'.format(
                    self.grid_name, group.name), 'w') as group_file:
                json.dump(group_export, group_file)

    def generate_all(self):
        self.generate_config()
        self.generate_networking()
        self.generate_security()
        self.generate_storage()
        self.generate_terminal()
        self.generate_masters()
        self.generate_groups()
