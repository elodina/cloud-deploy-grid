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


class gcs_infrastructure_generator(object):
    def __init__(self, grid_name, credentials, **kwargs):
        self.grid_name = grid_name
        self.credentials = urllib.unquote(credentials)
        self.current_grid = GridEntity.objects(name=grid_name).get()
        grid = self.current_grid
        self.current_config = configs[grid.provider].objects(parentgrid=grid_name).get()
        self.private_key_text = urllib.unquote(self.current_config.sshkeydata)
        self.private_key = RSA.importKey(self.private_key_text.strip())
        self.public_key_text = self.private_key.publickey().exportKey('OpenSSH')
        self.current_groups = []
        if not os.path.exists('result/{}/infrastructure'.format(grid_name)):
            os.makedirs('result/{}/infrastructure'.format(grid_name))
        for group in groups[grid.provider].objects(parentgrid=grid_name):
            self.current_groups.append(group)
        self.config = AutoDict()
        self.networking = AutoDict()
        self.security = AutoDict()
        self.terminal = AutoDict()
        self.masters = AutoDict()

    def generate_config(self):
        self.config['provider']['google']['credentials'] = self.credentials
        self.config['provider']['google']['project'] = self.current_config.project
        self.config['provider']['google']['region'] = self.current_config.zone
        self.config['variable']['region']['default'] = self.current_config.zone
        self.config['variable']['grid_name']['default'] = self.current_config.parentgrid
        self.config['variable']['ssh_user']['default'] = self.current_config.ssh_user
        self.config['variable']['ssh_key']['default'] = self.public_key_text
        self.config['variable']['vm_image']['default'] = 'centos-7-v20160301'
        with open('result/{}/infrastructure/config.tf'.format(self.grid_name), 'w') as config_file:
            json.dump(self.config, config_file)

    def generate_networking(self):
        self.networking['resource']['google_compute_network']['{}-network'.format(self.grid_name)]['name'] = '${var.grid_name}-network'
        self.networking['resource']['google_compute_network']['{}-network'.format(self.grid_name)]['ipv4_range'] = '172.27.0.0/16'
        with open('result/{}/infrastructure/networking.tf'.format(self.grid_name), 'w') as networking_file:
            json.dump(self.networking, networking_file)

    def generate_security(self):
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['name'] = '${var.grid_name}-gridwide'
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['network'] = '${var.grid_name}-network'
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['depends_on'] = ['google_compute_network.{}-network'.format(self.grid_name)]
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['allow'] = []
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['allow'].append({'protocol': 'tcp', 'ports': ['0-65535']})
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['allow'].append({'protocol': 'udp', 'ports': ['0-65535']})
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['allow'].append({'protocol': 'icmp'})
        self.security['resource']['google_compute_firewall']['{}-gridwide'.format(self.grid_name)]['source_ranges'] = ['${{google_compute_network.{}-network.ipv4_range}}'.format(self.grid_name)]
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['name'] = '${var.grid_name}-terminal'
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['network'] = '${var.grid_name}-network'
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['depends_on'] = ['google_compute_network.{}-network'.format(self.grid_name)]
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['allow'] = []
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['allow'].append({'protocol': 'tcp', 'ports': ['0-65535']})
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['allow'].append({'protocol': 'udp', 'ports': ['655-65535']})
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['allow'].append({'protocol': 'icmp'})
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['source_ranges'] = ['0.0.0.0/0']
        self.security['resource']['google_compute_firewall']['{}-terminal'.format(self.grid_name)]['target_tags'] = ['terminal']
        with open('result/{}/infrastructure/security.tf'.format(self.grid_name), 'w') as security_file:
            json.dump(self.security, security_file)

    def generate_terminal(self):
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['name'] = '${var.grid_name}-terminal'
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['machine_type'] = 'g1-small'
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['zone'] = '{}'.format(self.current_config.zone)
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['tags'] = []
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['tags'].append('terminal')
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['disk'] = []
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['disk'].append({'image':'${var.vm_image.default}', 'size': '20','type': 'pd-ssd'})
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['network_interface'] = []
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['network_interface'].append({'network':'${var.grid_name}-network','access_config':{}})
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['can_ip_forward'] = 'true'
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['metadata']['ssh_user'] = '${var.ssh_user}'
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['metadata']['sshKeys'] = '${var.ssh_user}:${var.ssh_key} ${var.ssh_user}'
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['metadata']['dc'] = '${var.grid_name}'
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['metadata']['role'] = '{}_terminal'.format(self.grid_name)
        self.terminal['resource']['google_compute_instance']['{}-terminal'.format(self.grid_name)]['depends_on'] = ['google_compute_network.{}-network'.format(self.grid_name)]
        with open('result/{}/infrastructure/terminal.tf'.format(self.grid_name), 'w') as terminal_file:
            json.dump(self.terminal, terminal_file)

    def generate_masters(self):
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['count'] = '{}'.format(self.current_config.masters)
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['name'] = '${var.grid_name}-mesos-master-${count.index}'
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['machine_type'] = '{}'.format(self.current_config.master_type)
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['zone'] = '{}'.format(self.current_config.zone)
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['tags'] = []
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['tags'].append('master')
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['disk'] = []
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['disk'].append({'image':'${var.vm_image.default}', 'size': '50','type': 'pd-ssd'})
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['network_interface'] = []
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['network_interface'].append({'network':'${var.grid_name}-network','access_config':{}})
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['metadata']['ssh_user'] = '${var.ssh_user}'
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['metadata']['sshKeys'] = '${var.ssh_user}:${var.ssh_key} ${var.ssh_user}'
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['metadata']['dc'] = '${var.grid_name}'
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['metadata']['role'] = '{}_mesos_master'.format(self.grid_name)
        self.masters['resource']['google_compute_instance']['{}-mesos_master'.format(self.grid_name)]['depends_on'] = ['google_compute_network.{}-network'.format(self.grid_name)]
        with open('result/{}/infrastructure/masters.tf'.format(self.grid_name), 'w') as masters_file:
            json.dump(self.masters, masters_file)

    def generate_groups(self):
        for group in self.current_groups:
            group_export = AutoDict()
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['count'] = '{}'.format(group.slaves)
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['name'] = '${{var.grid_name}}-{}-${{count.index}}'.format(group.name)
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['machine_type'] = '{}'.format(group.instance_type)
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['zone'] = '{}'.format(group.zone)
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['tags'] = []
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['tags'].append('slave')
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['disk'] = []
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['disk'].append({'image':'${var.vm_image.default}', 'size': '{}'.format(group.disk_size), 'type': 'pd-ssd'})
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['network_interface'] = []
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['network_interface'].append({'network':'${var.grid_name}-network','access_config':{}})
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['ssh_user'] = '${var.ssh_user}'
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['sshKeys'] = '${var.ssh_user}:${var.ssh_key} ${var.ssh_user}'
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['dc'] = '${var.grid_name}'
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['metadata']['role'] = '{}_{}'.format(self.grid_name, group.role)
            group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['depends_on'] = ['google_compute_network.{}-network'.format(self.grid_name)]
            if group.preemptible:
                group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)]['scheduling']['preemptible'] = 'true'
            if group.customhwconf is not None:
                group_export['resource']['google_compute_instance']['{}-mesos_group_{}'.format(self.grid_name, group.name)].update(ast.literal_eval(group.customhwconf))
            with open('result/{}/infrastructure/group_{}.tf'.format(self.grid_name, group.name), 'w') as group_file:
                json.dump(group_export, group_file)

    def generate_ssh_key(self):
        with open('result/{}/grid.pem'.format(self.grid_name), 'w+') as ssh_key:
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
        subprocess.check_call(['ssh-add', 'result/{}/grid.pem'.format(self.grid_name)])
