from flask_restful import reqparse

grid_parser = reqparse.RequestParser()
grid_parser.add_argument('name', required=True)
grid_parser.add_argument('provider', required=True)
grid_parser.add_argument(
    'type', required=True, help='Grid type - mesos/dcos')

config_parser = reqparse.RequestParser()
config_parser.add_argument('vars', help='Ansible group_vars for all cluster', default='{\"foo\":\"bar\"}')

awsconfig_parser = config_parser.copy()
awsconfig_parser.add_argument(
    'masters', required=True, type=int,
    help='Number of Master nodes in grid')
awsconfig_parser.add_argument(
    'master_type', default='m3.large', help='Master instance type')
awsconfig_parser.add_argument(
    'region', required=True, help='AWS Region, e.g. us-east-1')
awsconfig_parser.add_argument(
    'sshkey', required=True, help='AWS ssh keypair name')
awsconfig_parser.add_argument(
    'sshkeydata', required=True,
    help='AWS ssh key private part, URL encoded')
awsconfig_parser.add_argument(
    'ssh_user', default='centos', help='SSH user for VMs')

azureconfig_parser = config_parser.copy()
azureconfig_parser.add_argument(
    'masters', required=True, type=int,
    help='Number of Master nodes in grid')
azureconfig_parser.add_argument(
    'master_type', default='Basic_A2', help='Master instance type')
azureconfig_parser.add_argument(
    'location', required=True, help='Azure location, e.g. europenorth')
azureconfig_parser.add_argument(
    'ssh_user', required=True, help='SSH user for VMs')
azureconfig_parser.add_argument(
    'ssh_password', required=True, help='SSH password for VMs')

gcsconfig_parser = config_parser.copy()
gcsconfig_parser.add_argument(
    'masters', required=True, type=int,
    help='Number of Master nodes in grid')
gcsconfig_parser.add_argument(
    'master_type', default='n1-standard-1', help='Master instance type')
gcsconfig_parser.add_argument(
    'project', required=True, help='GCE Project')
gcsconfig_parser.add_argument(
    'zone', required=True, help='GCE Zone, for example europe-west1-b')
gcsconfig_parser.add_argument('sshkeydata', required=True,
    help='ssh key public part, URL encoded')
gcsconfig_parser.add_argument(
    'ssh_user', required=True, help='SSH user for VMs')

customconfig_parser = config_parser.copy()
customconfig_parser.add_argument(
    'ssh_user', required=True, help='SSH user for VMs')
customconfig_parser.add_argument(
    'sshkeydata', required=True,
    help='ssh key private part, URL encoded')
customconfig_parser.add_argument(
    'mastersips', required=True,
    help='comma separated list of master ip addresses, 3 or 5')
customconfig_parser.add_argument(
    'terminalips', required=True,
    help='ip addresses of terminal server, format: <external_ip>,<internal_ip>')

deployment_parser = reqparse.RequestParser()

infrastructure_deployment_parser = deployment_parser.copy()

provision_deployment_parser = deployment_parser.copy()
provision_deployment_parser.add_argument(
    'duo_ikey', help='duo.com ikey for api access, URL encoded', default='')
provision_deployment_parser.add_argument(
    'duo_skey', help='duo.com skey for api access, URL encoded', default='')
provision_deployment_parser.add_argument(
    'duo_host', help='duo.com host for api access, URL encoded', default='')
provision_deployment_parser.add_argument(
    'vpn_enabled', help='VPN flag, True by default', default='True')

aws_infrastructure_deployment_parser = infrastructure_deployment_parser.copy()
aws_infrastructure_deployment_parser.add_argument(
    'parallelism', type=int, default=5, help='Terraform deployment threads')
aws_infrastructure_deployment_parser.add_argument(
    'aws_access_key_id', required=True, help='AWS Access key ID, URL encoded')
aws_infrastructure_deployment_parser.add_argument(
    'aws_secret_access_key', required=True, help='AWS Access key secret, URL encoded')

aws_provision_deployment_parser = provision_deployment_parser.copy()
aws_provision_deployment_parser.add_argument(
    'aws_access_key_id', required=True, help='AWS Access key ID, URL encoded')
aws_provision_deployment_parser.add_argument(
    'aws_secret_access_key', required=True, help='AWS Access key secret, URL encoded')

azure_infrastructure_deployment_parser = infrastructure_deployment_parser.copy()
azure_infrastructure_deployment_parser.add_argument(
    'parallelism', type=int, default=5, help='Terraform deployment threads')
azure_infrastructure_deployment_parser.add_argument(
    'credentials', required=True,
    help='Azure credentials file, URL encoded')

azure_provision_deployment_parser = provision_deployment_parser.copy()

gcs_infrastructure_deployment_parser = infrastructure_deployment_parser.copy()
gcs_infrastructure_deployment_parser.add_argument(
    'parallelism', type=int, default=5, help='Terraform deployment threads')
gcs_infrastructure_deployment_parser.add_argument(
    'credentials', required=True, help='GCS credentials file, URL encoded')

gcs_provision_deployment_parser = provision_deployment_parser.copy()

custom_infrastructure_deployment_parser = infrastructure_deployment_parser.copy()

custom_provision_deployment_parser = provision_deployment_parser.copy()

group_parser = reqparse.RequestParser()
group_parser.add_argument('name', required=True)
group_parser.add_argument('role', required=True)
group_parser.add_argument('attributes', required=True)
group_parser.add_argument('vars', help='Ansible group_vars for this group', default='{\"foo\":\"bar\"}')

awsgroup_parser = group_parser.copy()
awsgroup_parser.add_argument('cpus', required=True, type=int,
                          help='Number of CPUs in group')
awsgroup_parser.add_argument('ram', required=True, type=int,
                          help='Amount of RAM in group, in GB')
awsgroup_parser.add_argument('disk_size', required=True, type=int,
                          help='Slave disk size(per slave), in GB')
awsgroup_parser.add_argument(
    'customhwconf',
    help='Add custom hardware configuration to slaves, escaped JSON format')
awsgroup_parser.add_argument('instance_type', default='m3.xlarge',
                             help='AWS Instance type, by default m3.xlarge')
awsgroup_parser.add_argument('enhanced_networking', type=bool, default=False,
                             help='shold enhanced networking AMI be used')
awsgroup_parser.add_argument('az', help='Availability Zone to place group to')
awsgroup_parser.add_argument(
    'spot_price', help='Make instance spot and set price for it')


azuregroup_parser = group_parser.copy()
azuregroup_parser.add_argument('cpus', required=True, type=int,
                          help='Number of CPUs in group')
azuregroup_parser.add_argument('ram', required=True, type=int,
                          help='Amount of RAM in group, in GB')
azuregroup_parser.add_argument('disk_size', required=True, type=int,
                          help='Slave disk size(per slave), in GB')
azuregroup_parser.add_argument(
    'customhwconf',
    help='Add custom hardware configuration to slaves, escaped JSON format')
azuregroup_parser.add_argument(
    'instance_type', default='Standard_DS11',
    help='Azure Instance type, by default Standard_DS11')

gcsgroup_parser = group_parser.copy()
gcsgroup_parser.add_argument('cpus', required=True, type=int,
                          help='Number of CPUs in group')
gcsgroup_parser.add_argument('ram', required=True, type=int,
                          help='Amount of RAM in group, in GB')
gcsgroup_parser.add_argument('disk_size', required=True, type=int,
                          help='Slave disk size(per slave), in GB')
gcsgroup_parser.add_argument(
    'customhwconf',
    help='Add custom hardware configuration to slaves, escaped JSON format')
gcsgroup_parser.add_argument('instance_type', default='n1-standard-2',
                             help='GCE Instance type, by default n1-standard-2')
gcsgroup_parser.add_argument('zone', help='Zone to place group to')
gcsgroup_parser.add_argument('preemptible', type=bool, default=False,
                             help='Make instance preemptible')

customgroup_parser = group_parser.copy()
customgroup_parser.add_argument(
    'groupips', required=True,
    help='comma separated list of group servers ip addresses')

configparsers = {
    'aws': awsconfig_parser,
    'azure': azureconfig_parser,
    'gcs': gcsconfig_parser,
    'custom': customconfig_parser
}

infrastructure_deploymentparsers = {
    'aws': aws_infrastructure_deployment_parser,
    'azure': azure_infrastructure_deployment_parser,
    'gcs': gcs_infrastructure_deployment_parser,
    'custom': custom_infrastructure_deployment_parser
}

provision_deploymentparsers = {
    'aws': aws_provision_deployment_parser,
    'azure': azure_provision_deployment_parser,
    'gcs': gcs_provision_deployment_parser,
    'custom': custom_provision_deployment_parser
}

groupparsers = {
    'aws': awsgroup_parser,
    'azure': azuregroup_parser,
    'gcs': gcsgroup_parser,
    'custom': customgroup_parser
}
