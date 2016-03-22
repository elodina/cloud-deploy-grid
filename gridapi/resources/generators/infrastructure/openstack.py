import ast
import json
import os
import urllib
import subprocess
from gridapi.resources.models import GridEntity, configs, groups
from Crypto.PublicKey import RSA

class AutoDict(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class openstack_infrastructure_generator(object):
    def __init__(self, grid_name, api_user, api_pass, api_url, **kwargs):
        self.grid_name = grid_name
        self.api_user = urllib.unquote(api_user)
        self.api_pass = urllib.unquote(api_pass)
        self.api_url = urllib.unquote(api_url)
        self.current_grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        self.current_config = configs[
            self.current_grid.provider].select().where(
            configs[self.current_grid.provider].parentgrid ==
            self.current_grid).get()
        self.private_key_text = urllib.unquote(self.current_config.sshkeydata)
        self.private_key = RSA.importKey(self.private_key_text.strip())
        self.public_key_text = self.private_key.publickey().exportKey('OpenSSH')
        self.current_groups = []
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        for group in groups[self.current_grid.provider].select():
            if group.parentgrid.name == grid_name:
                self.current_groups.append(group)
        self.config = AutoDict()
        self.networking = AutoDict()
        self.security = AutoDict()
        self.terminal = AutoDict()
        self.masters = AutoDict()

    def generate_config(self):
        self.config['provider']['openstack']['user_name'] = self.api_user
        self.config['provider']['openstack']['password'] = self.api_pass
        self.config['provider']['openstack']['auth_url'] = self.api_url
        self.config['provider']['openstack']['tenant_name'] = self.current_config.tenant
        self.config['variable']['grid_name']['default'] = self.current_config.parentgrid.name
        self.config['resource']['openstack_compute_keypair_v2']['{}-ssh_key'.format(self.grid_name)]['name'] = '{}-ssh_key'.format(self.grid_name)
        self.config['resource']['openstack_compute_keypair_v2']['{}-ssh_key'.format(self.grid_name)]['public_key'] = self.public_key_text
        with open('result/{}/infrastructure/config.tf'.format(
                self.grid_name), 'w') as config_file:
            json.dump(self.config, config_file)

    def generate_networking(self):
        self.networking['resource']['openstack_networking_network_v2']['{}-network'.format(self.grid_name)]['name'] = '${var.grid_name}-network'
        self.networking['resource']['openstack_networking_network_v2']['{}-network'.format(self.grid_name)]['admin_state_up'] = 'true'
        self.networking['resource']['openstack_networking_subnet_v2']['{}-subnet'.format(self.grid_name)]['name'] = '${var.grid_name}-network'
        self.networking['resource']['openstack_networking_subnet_v2']['{}-subnet'.format(self.grid_name)]['network_id'] = '${{openstack_networking_network_v2.{}-network.id}}'.format(self.grid_name)
        self.networking['resource']['openstack_networking_subnet_v2']['{}-subnet'.format(self.grid_name)]['cidr'] = '172.26.0.0/16'
        self.networking['resource']['openstack_networking_subnet_v2']['{}-subnet'.format(self.grid_name)]['ip_version'] = '4'
        self.networking['resource']['openstack_networking_router_v2']['{}-router'.format(self.grid_name)]['name'] = '${var.grid_name}-router'
        self.networking['resource']['openstack_networking_router_v2']['{}-router'.format(self.grid_name)]['region'] = self.current_config.region
        self.networking['resource']['openstack_networking_router_v2']['{}-router'.format(self.grid_name)]['external_gateway'] = self.current_config.external_network_uuid
        self.networking['resource']['openstack_networking_router_interface_v2']['{}-router-internal-interface'.format(self.grid_name)]['region'] = self.current_config.region
        self.networking['resource']['openstack_networking_router_interface_v2']['{}-router-internal-interface'.format(self.grid_name)]['router_id'] = '${{openstack_networking_router_v2.{}-router.id}}'.format(self.grid_name)
        self.networking['resource']['openstack_networking_router_interface_v2']['{}-router-internal-interface'.format(self.grid_name)]['subnet_id'] = '${{openstack_networking_subnet_v2.{}-subnet.id}}'.format(self.grid_name)
        self.networking['resource']['openstack_networking_port_v2']['{}-internal-port'.format(self.grid_name)]['name'] = '${var.grid_name}-internal-port'
        self.networking['resource']['openstack_networking_port_v2']['{}-internal-port'.format(self.grid_name)]['network_id'] = '${{openstack_networking_network_v2.{}-network.id}}'.format(self.grid_name)
        self.networking['resource']['openstack_networking_port_v2']['{}-internal-port'.format(self.grid_name)]['admin_state_up'] = 'true'
        self.networking['resource']['openstack_networking_port_v2']['{}-internal-port'.format(self.grid_name)]['security_group_ids'] = []
        self.networking['resource']['openstack_networking_port_v2']['{}-internal-port'.format(self.grid_name)]['security_group_ids'].append('${{openstack_compute_secgroup_v2.{}-gridwide.id}}'.format(self.grid_name))
        self.networking['resource']['openstack_networking_port_v2']['{}-internal-port'.format(self.grid_name)]['security_group_ids'].append('${{openstack_compute_secgroup_v2.{}-terminal.id}}'.format(self.grid_name))
        with open('result/{}/infrastructure/networking.tf'.format(
                self.grid_name), 'w') as networking_file:
            json.dump(self.networking, networking_file)

    def generate_security(self):
        self.security['resource']['openstack_compute_secgroup_v2']['{}-gridwide'.format(self.grid_name)]['name'] = '${var.grid_name}-gridwide'
        self.security['resource']['openstack_compute_secgroup_v2']['{}-gridwide'.format(self.grid_name)]['description'] = '${var.grid_name}-gridwide'
        self.security['resource']['openstack_compute_secgroup_v2']['{}-gridwide'.format(self.grid_name)]['rule'] = []
        self.security['resource']['openstack_compute_secgroup_v2']['{}-gridwide'.format(self.grid_name)]['rule'].append({'ip_protocol': 'tcp', 'from_port': '0', 'to_port': '65535', 'cidr': '${{openstack_networking_subnet_v2.{}-subnet.cidr}}'.format(self.grid_name)})
        self.security['resource']['openstack_compute_secgroup_v2']['{}-gridwide'.format(self.grid_name)]['rule'].append({'ip_protocol': 'udp', 'from_port': '0', 'to_port': '65535', 'cidr': '${{openstack_networking_subnet_v2.{}-subnet.cidr}}'.format(self.grid_name)})
        self.security['resource']['openstack_compute_secgroup_v2']['{}-gridwide'.format(self.grid_name)]['rule'].append({'ip_protocol': 'icmp', 'from_port': '-1', 'to_port': '-1', 'cidr': '${{openstack_networking_subnet_v2.{}-subnet.cidr}}'.format(self.grid_name)})
        self.security['resource']['openstack_compute_secgroup_v2']['{}-terminal'.format(self.grid_name)]['name'] = '${var.grid_name}-terminal'
        self.security['resource']['openstack_compute_secgroup_v2']['{}-terminal'.format(self.grid_name)]['description'] = '${var.grid_name}-terminal'
        self.security['resource']['openstack_compute_secgroup_v2']['{}-terminal'.format(self.grid_name)]['rule'] = []
        self.security['resource']['openstack_compute_secgroup_v2']['{}-terminal'.format(self.grid_name)]['rule'].append({'ip_protocol': 'tcp', 'from_port': '0', 'to_port': '65535', 'cidr': '0.0.0.0/0'})
        self.security['resource']['openstack_compute_secgroup_v2']['{}-terminal'.format(self.grid_name)]['rule'].append({'ip_protocol': 'udp', 'from_port': '1194', 'to_port': '1194', 'cidr': '0.0.0.0/0'})
        self.security['resource']['openstack_compute_secgroup_v2']['{}-terminal'.format(self.grid_name)]['rule'].append({'ip_protocol': 'icmp', 'from_port': '-1', 'to_port': '-1', 'cidr': '0.0.0.0/0'})
        with open('result/{}/infrastructure/security.tf'.format(
                self.grid_name), 'w') as security_file:
            json.dump(self.security, security_file)


    def generate_terminal(self):
        self.terminal['resource']['openstack_compute_floatingip_v2']['{}-terminal'.format(self.grid_name)]['region'] = self.current_config.region
        self.terminal['resource']['openstack_compute_floatingip_v2']['{}-terminal'.format(self.grid_name)]['pool'] = self.current_config.floating_ip_pool
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['name'] = '${var.grid_name}-terminal'
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['image_name'] = self.current_config.image_name
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['flavor_name'] = self.current_config.terminal_type
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['floating_ip'] = "${{openstack_compute_floatingip_v2.{}-terminal.address}}".format(self.grid_name)
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['security_groups'] = []
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['security_groups'].append('${{openstack_compute_secgroup_v2.{}-terminal.id}}'.format(self.grid_name))
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['security_groups'].append('${{openstack_compute_secgroup_v2.{}-gridwide.id}}'.format(self.grid_name))
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['network']['name'] = '${{openstack_networking_network_v2.{}-network.name}}'.format(self.grid_name)
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['key_pair'] = '{}-ssh_key'.format(self.grid_name)
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['user_data'] = '#cloud-config\r\n disable_root: false\r\n'
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['metadata']['dc'] = '${var.grid_name}'
        self.terminal['resource']['openstack_compute_instance_v2']['{}-terminal'.format(self.grid_name)]['metadata']['role'] = '{}_terminal'.format(self.grid_name)
        with open('result/{}/infrastructure/terminal.tf'.format(
                self.grid_name), 'w') as terminal_file:
            json.dump(self.terminal, terminal_file)

    def generate_masters(self):
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['count'] = '{}'.format(self.current_config.masters)
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['name'] = '${var.grid_name}-mesos-master-${count.index}'
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['image_name'] = self.current_config.image_name
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['flavor_name'] = self.current_config.master_type
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['security_groups'] = []
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['security_groups'].append('${{openstack_compute_secgroup_v2.{}-gridwide.id}}'.format(self.grid_name))
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['network']['name'] = '${{openstack_networking_network_v2.{}-network.name}}'.format(self.grid_name)
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['key_pair'] = '{}-ssh_key'.format(self.grid_name)
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['user_data'] = '#cloud-config\r\n disable_root: false\r\n'
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['metadata']['dc'] = '${var.grid_name}'
        self.masters['resource']['openstack_compute_instance_v2']['{}-mesos_master'.format(self.grid_name)]['metadata']['role'] = '{}_mesos_master'.format(self.grid_name)
        with open('result/{}/infrastructure/masters.tf'.format(
                self.grid_name), 'w') as masters_file:
            json.dump(self.masters, masters_file)

    def generate_groups(self):
        for group in self.current_groups:
            group_export = AutoDict()
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['count'] = '{}'.format(group._slaves)
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['name'] = '${{var.grid_name}}-{}-${{count.index}}'.format(group.name)
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['image_name'] = self.current_config.image_name
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['flavor_name'] = '{}'.format(group.instance_type)
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['security_groups'] = []
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['security_groups'].append('${{openstack_compute_secgroup_v2.{}-gridwide.id}}'.format(self.grid_name))
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['network']['name'] = '${{openstack_networking_network_v2.{}-network.name}}'.format(self.grid_name)
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['key_pair'] = '{}-ssh_key'.format(self.grid_name)
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['user_data'] = '#cloud-config\r\n disable_root: false\r\n'
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['dc'] = '${var.grid_name}'
            group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['role'] = '{}_{}'.format(self.grid_name, group.role)
            if group.customhwconf is not None:
                group_export['resource']['openstack_compute_instance_v2']['{}-mesos_group_{}'.format(self.grid_name, group.name)].update(ast.literal_eval(group.customhwconf))
            with open('result/{}/infrastructure/group_{}.tf'.format(
                    self.grid_name, group.name), 'w') as group_file:
                json.dump(group_export, group_file)

    def generate_ssh_key(self):
        with open('result/{}/grid.pem'.format(
                self.grid_name), 'w+') as ssh_key:
            ssh_key.write(self.private_key_text)

    def generate_all(self):
        self.generate_config()
        self.generate_networking()
        self.generate_security()
        self.generate_terminal()
        self.generate_masters()
        self.generate_groups()
        self.generate_ssh_key()
        os.chmod('result/{}/grid.pem'.format(self.grid_name), 0600)
        subprocess.check_call(['ssh-add', 'result/{}/grid.pem'.format(
            self.grid_name)])
