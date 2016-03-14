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


class gcs_infrastructure_generator(object):
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
        self.terminal = AutoDict()
        self.masters = AutoDict()

    def generate_config(self):
        self.config['provider']['google']['credentials'] = self.credentials
        self.config['provider']['google']['project'] = self.current_config.project
        self.config['variable']['region']['default'] = self.current_config.zone
        self.config['variable']['grid_name'][
            'default'] = self.current_config.parentgrid.name
        self.config['variable']['ssh_user'][
            'default'] = self.current_config.ssh_user
        self.config['variable']['ssh_key'][
            'default'] = self.current_config.sshkeydata
        self.config['variable']['vm_image']['default'] = 'centos-7-v20160301'
        with open('result/{}/infrastructure/config.tf'.format(
                self.grid_name), 'w') as config_file:
            json.dump(self.config, config_file)

    def generate_networking(self):
        self.networking['resource']['google_compute_network']['{}_network'.format(self.grid_name)]['name'] = '${var.grid_name}_network'
        self.networking['resource']['google_compute_network']['{}_network'.format(self.grid_name)]['ipv4_range'] = ['172.27.0.0/16']
        with open('result/{}/infrastructure/networking.tf'.format(
                self.grid_name), 'w') as networking_file:
            json.dump(self.networking, networking_file)

    def generate_security(self):
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['name'] = '${var.grid_name}_gridwide'
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['network'] = '${var.grid_name}_network'
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['depends_on'] = ['google_compute_firewall.{}_network'.format(self.grid_name)]
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['allow'] = []
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['allow'].append({'protocol': 'tcp', 'ports': '0-65535'})
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['allow'].append({'protocol': 'udp', 'ports': '0-65535'})
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['allow'].append({'protocol': 'icmp'})
        self.security['resource']['google_compute_firewall']['{}_gridwide'.format(self.grid_name)]['source_ranges'] = ['${{google_compute_network.{}_network.ipv4_range}}'.format(self.grid_name)]
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['name'] = '${var.grid_name}_terminal'
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['network'] = '${var.grid_name}_network'
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['depends_on'] = ['google_compute_firewall.{}_network'.format(self.grid_name)]
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['allow'] = []
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['allow'].append({'protocol': 'tcp', 'ports': '0-65535'})
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['allow'].append({'protocol': 'udp', 'ports': '1194'})
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['allow'].append({'protocol': 'icmp'})
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['source_ranges'] = ['${{google_compute_network.{}_network.ipv4_range}}'.format(self.grid_name)]
        self.security['resource']['google_compute_firewall']['{}_terminal'.format(self.grid_name)]['target_tags'] = ['terminal']
        with open('result/{}/infrastructure/security.tf'.format(
                self.grid_name), 'w') as security_file:
            json.dump(self.security, security_file)

    def generate_terminal(self):
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['name'] = '${var.grid_name}-terminal'
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['machine_type'] = 'g1-small'
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['zone'] = '{}'.format(self.current_config.zone)
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['tags'] = []
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['tags'].append('terminal')
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['disk'] = []
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['disk'].append({'image':'${var.vm_image.default}', 'size': '20','type': 'pd-ssd'})
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['network_interface'] = []
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['network_interface'].append({'network':'${var.grid_name}_network','access_config':{}})
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['can_ip_forward'] = 'true'
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['metadata']['ssh_user'] = '${var.ssh_user}'
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['metadata']['sshKeys'] = '${var.ssh_user}:${var.ssh_key} ${var.ssh_user}'
        self.terminal['resource']['google_compute_instance']['{}_terminal'.format(self.grid_name)]['depends_on'] = ['google_compute_firewall.{}_network'.format(self.grid_name)]
        with open('result/{}/infrastructure/terminal.tf'.format(
                self.grid_name), 'w') as terminal_file:
            json.dump(self.terminal, terminal_file)

    def generate_masters(self):
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['count'] = '{}'.format(self.current_config.masters)
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['name'] = '${var.grid_name}-mesos-master-${count.index}'
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['machine_type'] = '{}'.format(self.current_config.master_type)
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['zone'] = '{}'.format(self.current_config.zone)
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['tags'] = []
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['tags'].append('master')
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['disk'] = []
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['disk'].append({'image':'${var.vm_image.default}', 'size': '50','type': 'pd-ssd'})
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['network_interface'] = []
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['network_interface'].append({'network':'${var.grid_name}_network','access_config':{}})
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['metadata']['ssh_user'] = '${var.ssh_user}'
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['metadata']['sshKeys'] = '${var.ssh_user}:${var.ssh_key} ${var.ssh_user}'
        self.masters['resource']['google_compute_instance']['{}_mesos_master'.format(self.grid_name)]['depends_on'] = ['google_compute_firewall.{}_network'.format(self.grid_name)]
        with open('result/{}/infrastructure/masters.tf'.format(
                self.grid_name), 'w') as masters_file:
            json.dump(self.masters, masters_file)

    def generate_groups(self):
        for group in self.current_groups:
            group_export = AutoDict()
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['count'] = '{}'.format(group._slaves)
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['name'] = '${{var.grid_name}}-{}-${{count.index}}'.format(group.name)
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['machine_type'] = '{}'.format(group.instance_type)
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['zone'] = '{}'.format(group.region)
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['tags'] = []
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['tags'].append('slave')
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['disk'] = []
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['disk'].append({'image':'${var.vm_image.default}', 'size': '{}'.format(group.disk_size), 'type': 'pd-ssd'})
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['network_interface'] = []
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['network_interface'].append({'network':'${var.grid_name}_network','access_config':{}})
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['ssh_user'] = '${var.ssh_user}'
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['sshKeys'] = '${var.ssh_user}:${var.ssh_key} ${var.ssh_user}'
            group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)]['depends_on'] = ['google_compute_firewall.{}_network'.format(self.grid_name)]
            if group.customhwconf is not None:
                group_export['resource']['google_compute_instance']['{}_mesos_group_{}'.format(self.grid_name, group.name)].update(ast.literal_eval(group.customhwconf))
            with open('result/{}/infrastructure/{}.tf'.format(
                    self.grid_name, group.name), 'w') as group_file:
                json.dump(group_export, group_file)

    def generate_all(self):
        self.generate_config()
        self.generate_networking()
        self.generate_security()
        self.generate_terminal()
        self.generate_masters()
        self.generate_groups()
