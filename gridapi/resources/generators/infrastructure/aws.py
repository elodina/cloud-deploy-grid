import ast
import json
import os
import subprocess
import re
import urllib
from gridapi.resources.models import GridEntity, configs, groups


basic_amis = {
    'us-east-1': 'ami-61bbf104',
    'us-west-1': 'ami-f77fbeb3',
    'us-west-2': 'ami-d440a6e7'
}

az_nets = {
    'a': '172.29.16.0/20',
    'b': '172.29.32.0/20',
    'c': '172.29.48.0/20',
    'd': '172.29.64.0/20',
    'e': '172.29.80.0/20',
    'f': '172.29.96.0/20',
    'g': '172.29.16.0/20',
    'h': '172.29.16.0/20'
}


class AutoDict(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class aws_infrastructure_generator(object):
    def __init__(self, grid_name, aws_access_key_id,
                 aws_secret_access_key, **kwargs):
        self.grid_name = grid_name
        self.aws_access_key_id = urllib.unquote(aws_access_key_id)
        self.aws_secret_access_key = urllib.unquote(aws_secret_access_key)
        self.current_grid = GridEntity.select().where(
            GridEntity.name == grid_name).get()
        self.current_config =\
            configs[self.current_grid.provider].select().where(
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

    def generate_ami(self, region):
        ami_config = AutoDict()
        launch_block_device_mappings = AutoDict()
        launch_block_device_mappings['device_name'] = '/dev/sda1'
        launch_block_device_mappings['volume_size'] = '8'
        launch_block_device_mappings['volume_type'] = 'gp2'
        launch_block_device_mappings['delete_on_termination'] = 'true'
        builder = AutoDict()
        builder['type'] = 'amazon-ebs'
        builder['access_key'] = self.aws_access_key_id
        builder['secret_key'] = self.aws_secret_access_key
        builder['region'] = self.current_config.region
        builder['source_ami'] = basic_amis[self.current_config.region]
        builder['instance_type'] = 'c3.large'
        builder['ssh_username'] = 'centos'
        builder['ssh_pty'] = 'true'
        builder['ami_name'] = 'dexter_{}'.format(self.current_config.region)
        builder['launch_block_device_mappings'] = [
            launch_block_device_mappings]
        provisioner = AutoDict()
        provisioner['execute_command'] =\
            "echo 'packer' | {{ .Vars }} sudo -E -S sh '{{ .Path }}'"
        provisioner['type'] = 'shell'
        provisioner['inline'] = [
            "yum -y update",
            "rpm -Uvh "
            "http://www.elrepo.org/elrepo-release-7.0-2.el7.elrepo.noarch.rpm",
            "yum -y install kmod-ixgbevf",
            "cp -ax /etc/sysconfig/network-scripts/ifcfg-eth0 "
            "/etc/sysconfig/network-scripts/ifcfg-ens3",
            "sed -i 's/eth0/ens3/g' /etc/sysconfig/network-scripts/ifcfg-ens3"]
        ami_config['builders'] = [builder]
        ami_config['provisioners'] = [provisioner]
        with open('result/{}/ami.json'.format(
                self.grid_name), 'w') as ami_json_file:
            json.dump(ami_config, ami_json_file)
        command = ['packer', 'build', '-machine-readable',
                   'result/{}/ami.json'.format(self.grid_name)]
        packer = subprocess.Popen(command, stdout=subprocess.PIPE)
        packer_output = packer.stdout.read()
        retcode = packer.wait()
        packer_output = packer_output.decode('utf-8')
        print(packer_output)
        pattern = re.compile('ami-.*', re.MULTILINE)
        result = pattern.findall(packer_output)
        os.system('rm -f result/{}/ami.json'.format(self.grid_name))
        return result[0]

    def generate_ami_en(self, region, parent_ami):
        ami_config = AutoDict()
        launch_block_device_mappings = AutoDict()
        launch_block_device_mappings['device_name'] = '/dev/sda1'
        launch_block_device_mappings['volume_size'] = '8'
        launch_block_device_mappings['volume_type'] = 'gp2'
        launch_block_device_mappings['delete_on_termination'] = 'true'
        builder = AutoDict()
        builder['type'] = 'amazon-ebs'
        builder['access_key'] = self.aws_access_key_id
        builder['secret_key'] = self.aws_secret_access_key
        builder['region'] = self.current_config.region
        builder['source_ami'] = parent_ami
        builder['enhanced_networking'] = 'true'
        builder['instance_type'] = 'c3.large'
        builder['ssh_username'] = 'centos'
        builder['ssh_pty'] = 'true'
        builder['ami_name'] = 'dexter_en_{}'.format(self.current_config.region)
        builder['launch_block_device_mappings'] = [
            launch_block_device_mappings]
        ami_config['builders'] = [builder]
        with open('result/{}/ami.json'.format(
                self.grid_name), 'w') as ami_json_file:
            json.dump(ami_config, ami_json_file)
        command = ['packer', 'build', '-machine-readable',
                   'result/{}/ami.json'.format(self.grid_name)]
        packer = subprocess.Popen(command, stdout=subprocess.PIPE)
        packer_output = packer.stdout.read()
        retcode = packer.wait()
        packer_output = packer_output.decode('utf-8')
        print(packer_output)
        pattern = re.compile('ami-.*', re.MULTILINE)
        result = pattern.findall(packer_output)
        os.system('rm -f result/{}/ami.json'.format(self.grid_name))
        return result[0]

    def generate_config(self):
        self.config['provider']['aws']['access_key'] = self.aws_access_key_id
        self.config['provider']['aws'][
            'secret_key'] = self.aws_secret_access_key
        self.config['provider']['aws']['region'] = self.current_config.region
        self.config['variable']['region'][
            'default'] = self.current_config.region
        self.config['variable']['grid_name'][
            'default'] = self.current_config.parentgrid.name
        self.config['variable']['vpc_name']['default'] = '{}_{}_vpc'.format(
            self.current_config.parentgrid.name, self.current_config.region)
        self.config['variable']['key_name'][
            'default'] = self.current_config.sshkey
        self.config['variable']['amis']['default'][
            self.current_config.region] = self.generate_ami(
            self.current_config.region)
        self.config['variable']['en_amis']['default'][
            self.current_config.region] = self.generate_ami_en(
            self.current_config.region,
            self.config['variable']['amis']['default'][
                self.current_config.region])
        with open('result/{}/infrastructure/config.tf'.format(
                self.grid_name), 'w') as config_file:
            json.dump(self.config, config_file)

    def generate_networking(self):
        self.networking['resource']['aws_vpc']['vpc'][
            'cidr_block'] = '172.29.0.0/16'
        self.networking['resource']['aws_vpc']['vpc']['tags'][
            'Name'] = '${var.vpc_name}'
        self.networking['resource']['aws_internet_gateway']['igw'][
            'vpc_id'] = '${aws_vpc.vpc.id}'
        self.networking['resource']['aws_internet_gateway']['igw']['tags'][
            'Name'] = '${var.vpc_name}'
        self.networking['resource']['aws_internet_gateway']['igw'][
            'depends_on'] = ['aws_vpc.vpc']
        self.networking['resource']['aws_internet_gateway']['igw'][
            'depends_on'] = ['aws_vpc.vpc']
        self.networking['resource']['aws_subnet']['grid_subnet'][
            'vpc_id'] = '${aws_vpc.vpc.id}'
        self.networking['resource']['aws_subnet']['grid_subnet'][
            'cidr_block'] = '172.29.0.0/20'
        self.networking['resource']['aws_subnet']['grid_subnet'][
            'map_public_ip_on_launch'] = 'true'
        self.networking['resource']['aws_subnet']['grid_subnet'][
            'tags']['Name'] = '${var.vpc_name}-${var.region}'
        self.networking['resource']['aws_route_table']['routes'][
            'vpc_id'] = '${aws_vpc.vpc.id}'
        self.networking['resource']['aws_route_table']['routes'][
            'route']['cidr_block'] = '0.0.0.0/0'
        self.networking['resource']['aws_route_table']['routes'][
            'route']['gateway_id'] = '${aws_internet_gateway.igw.id}'
        self.networking['resource']['aws_route_table_association'][
            'grid_route_table'][
            'subnet_id'] = '${aws_subnet.grid_subnet.id}'
        self.networking['resource']['aws_route_table_association'][
            'grid_route_table'][
            'route_table_id'] = '${aws_route_table.routes.id}'
        for group in self.current_groups:
            if group.az is not None:
                self.networking['resource']['aws_subnet'][
                    'az_{}_subnet'.format(
                        group.az)]['vpc_id'] = '${aws_vpc.vpc.id}'
                self.networking['resource']['aws_subnet'][
                    'az_{}_subnet'.format(group.az)]['cidr_block'] = az_nets[
                    group.az]
                self.networking['resource']['aws_subnet'][
                    'az_{}_subnet'.format(group.az)][
                    'map_public_ip_on_launch'] = 'true'
                self.networking['resource']['aws_subnet'][
                    'az_{}_subnet'.format(group.az)][
                    'availability_zone'] = '{}{}'.format(
                    self.current_config.region, group.az)
                self.networking['resource']['aws_subnet'][
                    'az_{}_subnet'.format(group.az)]['tags'][
                    'Name'] = '${{var.vpc_name}}-${{var.region}}{}'.format(
                    group.az)
                self.networking['resource']['aws_route_table_association'][
                    'az_{}_route_table'.format(group.az)][
                    'subnet_id'] = '${{aws_subnet.az_{}_subnet.id}}'.format(
                    group.az)
                self.networking['resource']['aws_route_table_association'][
                    'az_{}_route_table'.format(group.az)][
                    'route_table_id'] = '${aws_route_table.routes.id}'
        with open('result/{}/infrastructure/networking.tf'.format(
                self.grid_name), 'w') as networking_file:
            json.dump(self.networking, networking_file)

    def generate_security(self):
        self.security['resource']['aws_security_group']['gridwide']['name'] = '${var.grid_name}'
        self.security['resource']['aws_security_group']['gridwide']['description'] = '${var.grid_name} security group'
        self.security['resource']['aws_security_group']['gridwide']['vpc_id'] = '${aws_vpc.vpc.id}'
        self.security['resource']['aws_security_group']['gridwide']['tags']['Name'] = '${var.grid_name}'
        self.security['resource']['aws_security_group']['gridwide']['depends_on'] = ['aws_vpc.vpc']
        self.security['resource']['aws_security_group_rule']['egress_global_all']['security_group_id'] = '${aws_security_group.gridwide.id}'
        self.security['resource']['aws_security_group_rule']['egress_global_all']['type'] = 'egress'
        self.security['resource']['aws_security_group_rule']['egress_global_all']['from_port'] = '0'
        self.security['resource']['aws_security_group_rule']['egress_global_all']['to_port'] = '0'
        self.security['resource']['aws_security_group_rule']['egress_global_all']['protocol'] = '-1'
        self.security['resource']['aws_security_group_rule']['egress_global_all']['cidr_blocks'] = ['0.0.0.0/0']
        self.security['resource']['aws_security_group_rule']['ingress_ssh_internal']['security_group_id'] = '${aws_security_group.gridwide.id}'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_internal']['type'] = 'ingress'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_internal']['from_port'] = '0'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_internal']['to_port'] = '0'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_internal']['protocol'] = '-1'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_internal']['cidr_blocks'] = ['172.16.0.0/12']
        self.security['resource']['aws_security_group']['terminal']['name'] = '${var.grid_name}_terminal'
        self.security['resource']['aws_security_group']['terminal']['description'] = '${var.grid_name}_terminal security group'
        self.security['resource']['aws_security_group']['terminal']['vpc_id'] = '${aws_vpc.vpc.id}'
        self.security['resource']['aws_security_group']['terminal']['tags']['Name'] = '${var.grid_name}_terminal'
        self.security['resource']['aws_security_group']['terminal']['depends_on'] = ['aws_vpc.vpc']
        self.security['resource']['aws_security_group_rule']['ingress_ssh_terminal']['security_group_id'] = '${aws_security_group.terminal.id}'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_terminal']['type'] = 'ingress'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_terminal']['from_port'] = '22'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_terminal']['to_port'] = '22'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_terminal']['protocol'] = 'tcp'
        self.security['resource']['aws_security_group_rule']['ingress_ssh_terminal']['cidr_blocks'] = ['0.0.0.0/0']
        self.security['resource']['aws_security_group']['publisher']['name'] = '${var.grid_name}_publisher'
        self.security['resource']['aws_security_group']['publisher']['description'] = '${var.grid_name}_publisher security group'
        self.security['resource']['aws_security_group']['publisher']['vpc_id'] = '${aws_vpc.vpc.id}'
        self.security['resource']['aws_security_group']['publisher']['tags']['Name'] = '${var.grid_name}_publisher'
        self.security['resource']['aws_security_group']['publisher']['depends_on'] = ['aws_vpc.vpc']
        self.security['resource']['aws_security_group_rule']['ingress_all_tcp_publisher']['security_group_id'] = '${aws_security_group.publisher.id}'
        self.security['resource']['aws_security_group_rule']['ingress_all_tcp_publisher']['type'] = 'ingress'
        self.security['resource']['aws_security_group_rule']['ingress_all_tcp_publisher']['from_port'] = '1'
        self.security['resource']['aws_security_group_rule']['ingress_all_tcp_publisher']['to_port'] = '65535'
        self.security['resource']['aws_security_group_rule']['ingress_all_tcp_publisher']['protocol'] = 'tcp'
        self.security['resource']['aws_security_group_rule']['ingress_all_tcp_publisher']['cidr_blocks'] = ['0.0.0.0/0']
        self.security['resource']['aws_security_group_rule']['ingress_all_udp_publisher']['security_group_id'] = '${aws_security_group.publisher.id}'
        self.security['resource']['aws_security_group_rule']['ingress_all_udp_publisher']['type'] = 'ingress'
        self.security['resource']['aws_security_group_rule']['ingress_all_udp_publisher']['from_port'] = '1'
        self.security['resource']['aws_security_group_rule']['ingress_all_udp_publisher']['to_port'] = '65535'
        self.security['resource']['aws_security_group_rule']['ingress_all_udp_publisher']['protocol'] = 'udp'
        self.security['resource']['aws_security_group_rule']['ingress_all_udp_publisher']['cidr_blocks'] = ['0.0.0.0/0']
        with open('result/{}/infrastructure/security.tf'.format(
                self.grid_name), 'w') as security_file:
            json.dump(self.security, security_file)

    def generate_terminal(self):
        self.terminal['resource']['aws_instance']['terminal'][
            'ami'] = '${lookup(var.amis,"${var.region}")}'
        self.terminal['resource']['aws_instance']['terminal'][
            'instance_type'] = 'm3.large'
        self.terminal['resource']['aws_instance']['terminal'][
            'key_name'] = '${var.key_name}'
        self.terminal['resource']['aws_instance']['terminal'][
            'subnet_id'] = '${aws_subnet.grid_subnet.id}'
        self.terminal['resource']['aws_instance']['terminal'][
            'security_groups'] = ['${aws_security_group.gridwide.id}',
                                  '${aws_security_group.terminal.id}',
                                  '${aws_security_group.publisher.id}']
        self.terminal['resource']['aws_instance']['terminal'][
            'root_block_device']['volume_size'] = '50'
        self.terminal['resource']['aws_instance']['terminal'][
            'tags']['Name'] = '${var.grid_name}_terminal'
        self.terminal['resource']['aws_instance']['terminal'][
            'depends_on'] = ['aws_internet_gateway.igw']
        self.terminal['resource']['aws_eip']['terminal'][
            'instance'] = '${aws_instance.terminal.id}'
        self.terminal['resource']['aws_eip']['terminal']['vpc'] = 'true'
        with open('result/{}/infrastructure/terminal.tf'.format(
                self.grid_name), 'w') as terminal_file:
            json.dump(self.terminal, terminal_file)

    def generate_masters(self):
        self.masters['resource']['aws_instance']['mesos_master'][
            'count'] = '{}'.format(self.current_config.masters)
        self.masters['resource']['aws_instance']['mesos_master'][
            'ami'] = '${lookup(var.amis,"${var.region}")}'
        self.masters['resource']['aws_instance']['mesos_master'][
            'instance_type'] = 'm3.large'
        self.masters['resource']['aws_instance']['mesos_master'][
            'key_name'] = '${var.key_name}'
        self.masters['resource']['aws_instance']['mesos_master'][
            'subnet_id'] = '${aws_subnet.grid_subnet.id}'
        self.masters['resource']['aws_instance']['mesos_master'][
            'security_groups'] = ['${aws_security_group.gridwide.id}']
        self.masters['resource']['aws_instance']['mesos_master'][
            'root_block_device']['volume_size'] = '50'
        self.masters['resource']['aws_instance']['mesos_master'][
            'tags']['Name'] = '${var.grid_name}_mesos_master'
        self.masters['resource']['aws_instance']['mesos_master'][
            'depends_on'] = ['aws_internet_gateway.igw']
        with open('result/{}/infrastructure/masters.tf'.format(
                self.grid_name), 'w') as masters_file:
            json.dump(self.masters, masters_file)

    def generate_groups(self):
        for group in self.current_groups:
            group_export = AutoDict()
            if group.spot_price is not None:
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['spot_price'] = '{}'.format(group.spot_price)
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['wait_for_fulfillment'] = 'true'
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['count'] = '{}'.format(group._slaves)
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['instance_type'] = '{}'.format(
                    group.instance_type)
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['key_name'] = '${var.key_name}'
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['security_groups'] = [
                    '${aws_security_group.gridwide.id}']
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['root_block_device']['volume_size'] = '{}'.format(
                    group.disk_size)
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['tags'][
                    'Name'] = '${var.grid_name}_mesos_slave'
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['tags']['role'] = '{}_{}'.format(
                    self.grid_name, group.role)
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['tags']['group'] = '{}'.format(group.name)
                if group.az is not None:
                    group_export['resource']['aws_spot_instance_request'][
                        'mesos_group_{}'.format(group.name)][
                        'subnet_id'] = '${{aws_subnet.az_{}_subnet.id}}'.format(
                        group.az)
                else:
                    group_export['resource']['aws_spot_instance_request'][
                        'mesos_group_{}'.format(group.name)][
                        'subnet_id'] = '${aws_subnet.grid_subnet.id}'
                group_export['resource']['aws_spot_instance_request']['mesos_group_{}'.format(
                    group.name)]['depends_on'] = ['aws_internet_gateway.igw']
                if group.customhwconf is not None:
                    group_export['resource']['aws_spot_instance_request'][
                        'mesos_group_{}'.format(group.name)].update(
                        ast.literal_eval(group.customhwconf))
                if group.enhanced_networking:
                    group_export['resource']['aws_spot_instance_request'][
                        'mesos_group_{}'.format(group.name)][
                        'ami'] = '${lookup(var.en_amis,"${var.region}")}'
                else:
                    group_export['resource']['aws_spot_instance_request'][
                        'mesos_group_{}'.format(group.name)][
                        'ami'] = '${lookup(var.amis,"${var.region}")}'
                with open('result/{}/infrastructure/{}.tf'.format(
                        self.grid_name, group.name), 'w') as group_file:
                    json.dump(group_export, group_file)
            else:
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['count'] = '{}'.format(group._slaves)
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['instance_type'] = '{}'.format(
                    group.instance_type)
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['key_name'] = '${var.key_name}'
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['security_groups'] = [
                    '${aws_security_group.gridwide.id}']
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['root_block_device']['volume_size'] = '{}'.format(
                    group.disk_size)
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['tags'][
                    'Name'] = '${var.grid_name}_mesos_slave'
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['tags']['role'] = '{}_{}'.format(
                    self.grid_name, group.role)
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['tags']['group'] = '{}'.format(group.name)
                if group.az is not None:
                    group_export['resource']['aws_instance'][
                        'mesos_group_{}'.format(group.name)][
                        'subnet_id'] = '${{aws_subnet.az_{}_subnet.id}}'.format(
                        group.az)
                else:
                    group_export['resource']['aws_instance'][
                        'mesos_group_{}'.format(group.name)][
                        'subnet_id'] = '${aws_subnet.grid_subnet.id}'
                group_export['resource']['aws_instance']['mesos_group_{}'.format(
                    group.name)]['depends_on'] = ['aws_internet_gateway.igw']
                if group.customhwconf is not None:
                    group_export['resource']['aws_instance'][
                        'mesos_group_{}'.format(group.name)].update(
                        ast.literal_eval(group.customhwconf))
                if group.enhanced_networking:
                    group_export['resource']['aws_instance'][
                        'mesos_group_{}'.format(group.name)][
                        'ami'] = '${lookup(var.en_amis,"${var.region}")}'
                else:
                    group_export['resource']['aws_instance'][
                        'mesos_group_{}'.format(group.name)][
                        'ami'] = '${lookup(var.amis,"${var.region}")}'
                with open('result/{}/infrastructure/{}.tf'.format(
                        self.grid_name, group.name), 'w') as group_file:
                    json.dump(group_export, group_file)

    def generate_ssh_key(self):
        with open('result/{}/grid.pem'.format(
                self.grid_name), 'w+') as ssh_key:
            ssh_key.write(urllib.unquote(self.current_config.sshkeydata))

    def generate_all(self):
        os.environ['AWS_ACCESS_KEY_ID'] = '{}'.format(self.aws_access_key_id)
        os.environ['AWS_SECRET_ACCESS_KEY'] = '{}'.format(
            self.aws_secret_access_key)
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

