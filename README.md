Cluster API
===========

Table of Contents
=================

  * [Cluster API](#cluster-api)
    * [Prerequisites](#prerequisites)
    * [Current Limitations](#current-limitations)
    * [Preparation](#preparation)
    * [Cluster List API Requests](#cluster-list-api-requests)
    * [Cluster Entity API Requests](#cluster-entity-api-requests)
    * [Cluster Config API Requests](#cluster-config-api-requests)
    * [Cluster Slave group list API Requests](#cluster-slave-group-list-api-requests)
    * [Cluster Slave group API Requests](#cluster-slave-group-api-requests)
    * [Cluster Deployment API Requests](#cluster-deployment-api-requests)
    * [Common usage scenario for Mesos on AWS](#common-usage-scenario-for-mesos-on-aws)
    * [Common usage scenario for Mesos on Azure](#common-usage-scenario-for-mesos-on-azure)
    * [Common usage scenario for DCOS on AWS](#common-usage-scenario-for-dcos-on-aws)
    * [Common usage scenario for DCOS on Azure](#common-usage-scenario-for-dcos-on-azure)
    * [Mesos Cli Cluster Access](#mesos-cli-cluster-access)
    * [Mesos Cluster VPN Access](#mesos-cluster-vpn-access)
    * [DCOS Cluster VPN Access](#dcos-cluster-vpn-access)

Prerequisites
-------------
First, you should install required software:

GNU/Linux:

1. Docker - latest

OS X:

1. Vagrant - latest


Current Limitations
-------------------
Azure instances supported:
Standard_DS1, Standard_DS2, Standard_DS3, Standard_DS4, Standard_DS11, Standard_DS12, Standard_DS13, Standard_DS14

WARNING!
All names(cluster, groups, etc) should consist of only lowercase letters and numbers, should be started with
lowercase letter and be up to 16 characters long.


Preparation
-----------

GNU/Linux:

1. clone this repo

2. run ./run

OS X:

1. clone this repo

2. cd dexter

3. run vagrant up

3. ssh vagrant@127.0.0.1 -p 2222; password - vagrant

4. (In vagrant) run cd /vagrant

5. (In vagrant) run ./run


Cluster List API Requests
-------------------------

```
http://localhost:5555/api/v1.0/clusters
```

Supported requests:

GET - get cluster list, example:

```
curl http://localhost:5555/api/v1.0/clusters
```

POST - add new cluster, example:

```
curl -X POST -d "name=${cluster_name}" -d "provider=aws" -d "type=mesos" http://localhost:5555/api/v1.0/clusters
```

required parameters - name(variable), provider(aws/azure/custom), type(mesos/dcos)


Cluster Entity API Requests
---------------------------

```
http://localhost:5555/api/v1.0/clusters/${cluster_name}
```

Supported requests:

GET - get cluster status, example:

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}
```

DELETE - delete cluster and its stuff, example:

```
curl -X DELETE http://localhost:5555/api/v1.0/clusters/${cluster_name}
```

Cluster Config API Requests
---------------------------

```
http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

Supported requests:

GET - get clusters config, example:

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

DELETE - delete clusters config:

```
curl -X DELETE http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

PUT - change clusters config:

```
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-west-2" -d "sshkey=reference" -d "sshkeydata=`cat ~/.ssh/reference.pem | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

required parameters:

common:
masters(number of masters hosts)

aws:
master_type(AWS instance type for master, default m3.large), region(AWS region for cluster), sshkey(AWS ssh key name), sshkeydata(Private path of ssh key, encoded with BASE64)

azure:
master_type(Azure instance type for master, default is Basic_A2), location(Azure location for cluster in format like "Central US"), ssh_user(user for ssh login), ssh_password(password for ssh user and sudo)

custom:
mastersips(Comma separated list of masters ips), terminalips(<terminal_external_ip>,<terminal_internal_ip>), ssh_user(ssh user for connection), sshkeydata(Private part of ssh key, encoded with BASE64)


Cluster Slave group list API Requests
-------------------------------------

```
http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

Supported requests:

GET - get clusters slave groups, example:

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

POST - add new group, example:

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"foo\":\"bar\"}" -d "vars={\"foo\":\"bar\"}" -d "instance_type=r3.xlarge" -d "cpus=10" -d "ram=64" -d "disk_size=50" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```
required parameters - name(variable), role(variable), attributes(escaped json format), vars(escaped json format), instance_type(for AWS, for example - m3.large, for Azure, for example - Basic_A3), cpus(number of cpus per group), ram(amount of GB of ram per group), disk_size(hdd size, per HOST)

optional parameters:

az(availability zone to place group to, AWS only), example:

```
-d "az=c"
```

customhwconf(escaped json format, look at https://www.terraform.io/docs/configuration/syntax.html)

example of customhwconf:

```
{\"ebs_block_device\":[{\"device_name\":\"/dev/sdx\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"}]}
```

groupips(in custom provider, comma separated list of group ips)


All of the new created disks will be mounted to /hdd/xvd{last letter of disk name, eg, x, y, whatever}

Cluster Slave group API Requests
--------------------------------

```
http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups/${group_name}
```

Supported requests:

GET - get clusters slave group parameters, example:

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups/${group_name}
```

DELETE - delete group, example:

```
curl -X DELETE http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups/${group_name}
```

PUT - change group parameters, example:

```
curl -X PUT -d "name=group2" -d "role=role1" -d "attributes={\"foo\":\"bar\"}" -d "vars={\"var1\":\"varvalue1\"}" -d "instance_type=r3.xlarge" -d "cpus=10" -d "ram=64" -d "disk_size=50" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups/${group_name}
```

required parameters - name(variable), role(variable), attributes(escaped json format), vars(escaped json format), instance_type(for AWS, for example - m3.large, for Azure, for example - Basic_A3), cpus(number of cpus per group), ram(amount of GB of ram per group), disk_size(hdd size, per HOST)

optional parameters:

az(availability zone to place group to, AWS only), example:

```
-d "az=c"
```

customhwconf(escaped json format, look at https://www.terraform.io/docs/configuration/syntax.html)

example of customhwconf:

```
{\"ebs_block_device\":[{\"device_name\":\"/dev/sdx\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"}]}
```

All of the new created disks will be mounted to /hdd/xvd{last letter of disk name, eg, x, y, whatever}

spot_price(group of slaves will be make of spot instances), example:

```
-d "spot_price=0.9"
```

groupips(in custom provider, comma separated list of group ips)

Cluster Deployment API Requests
-------------------------------

```
http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment
```

Supported requests:

GET - get clusters deployment status, example:

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment
```

Cluster Infrastructure Deployment API Requests
----------------------------------------------

```
http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

Supported requests:

GET - get clusters infrastructure deployment status, example:

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

DELETE - destroy cluster's infrastructure(virtual machines, networks, etc), example:

```
curl -X DELETE http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

PUT - deploy cluster's infrastructure(virtual machines, networks, etc), example:

AWS:
```
curl -X PUT -d "aws_access_key_id=${key_id}" -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

AZURE:
```
curl -X PUT -d "credentials=`cat credentials | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

CUSTOM:
```
curl -X PUT http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

required parameters:

common:
parallelism(number of deploy threads, higher number increase deployment speed, but may cause instability, default is 5)

aws:
aws_access_key_id(self descriptive), aws_secret_access_key(self descriptive)

azure:
credentials(credentials file, can be aquired here: https://manage.windowsazure.com/publishsettings )


Cluster Provision API Requests
------------------------------

```
http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

Supported requests:

GET - get clusters provision status, example:

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

PUT - run cluster's provision(install software, configure settings, etc), example:

AWS:
```
curl -X PUT -d "aws_access_key_id=${key_id}" -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

AZURE:
```
curl -X PUT http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

CUSTOM:
```
curl -X PUT http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

required parameters:

aws:

aws_access_key_id(self descriptive), aws_secret_access_key(self descriptive)


optional parameters:

common:

vpn_enabled - by default == 'True', if True - enable VPN server provisioinig, otherwise - disable

duo_ikey, duo_skey, duo_host - duo security api parameters(duo.com) for vpn auth
PREREQUISITS FOR MFA:
1) Created application at duo.com(Auth API)

2) Created user at duo.com with added Mobile Device

3) Installed duo.com mobile app on mobile device(the only supported way for now)


How to use MFA:

1) Create login(same as at duo.com) on Terminal server and passwd it

2) Create new VPN connection

3) password for vpn will be: "<local_password>,<duo_passcode_from_mobile_app>"
example: "str0ng_pass,123123"


It is possible to provision separate group, calling
```
curl -X PUT http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups/${group_name}/provision
```

required parameters are the same as for cluster provision calls


Common usage scenario for Mesos on AWS
--------------------------------------

Create cluster

```
curl -X POST -d "name=${cluster_name}" -d "provider=aws" -d "type=mesos" http://localhost:5555/api/v1.0/clusters
```

Update config

```
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-west-2" -d "sshkey=reference" -d "sshkeydata=`cat ~/.ssh/reference.pem | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

Create group of slaves

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"foo\":\" bar\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=10" -d "ram=64" -d "disk_size=50" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

Deploy cluster's infrastructure

```
curl -X PUT -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

Provision cluster

```
curl -X PUT http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

Change slaves group size:

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"purpose\":\"log_storing\"}" -d "vars={\"x_factor\":\"42\"}" -d "cpus=20" -d "ram=128" -d "disk_size=50" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

Apply changes to infrastructure

```
curl -X PUT -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

Provision fresh nodes

```
curl -X PUT http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

Destroy cluster

```
curl -X DELETE -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

Delete clusters config, etc:

```
curl -X DELETE http://localhost:5555/api/v1.0/clusters/${cluster_name}
```


Common usage scenario for Mesos on Azure
----------------------------------------

Create cluster

```
curl http://localhost:5555/api/v1.0/clusters -X POST -d "name=${cluster_name}" -d "provider=azure" -d "type=mesos"
```

Update config

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/config -X PUT -d "location=Central US" -d "masters=3" -d "ssh_password=${ssh_password}" -d "ssh_user=${ssh_user}" -d "master_type=Basic_A2"
```

Create group of slaves

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"purpose\":\"analytics\"}" -d "vars={\"y_factor\":\"43\"}" -d "cpus=12" -d "ram=16" -d "disk_size=50" -d "instance_type=Standard_D11"
```

Deploy cluster's infrastructure

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure -X PUT -d "credentials=`cat credentials | base64 | tr '+/' '-_'`"
```

Provision cluster

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision -X PUT
```

Destroy cluster

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure -X DELETE -d "credentials=`cat credentials | base64 | tr '+/' '-_'`"
```

Delete cluster configs, etc

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name} -X DELETE
```


Common usage scenario for Mesos on Custom Provider
--------------------------------------------------

Create cluster

```
curl http://localhost:5555/api/v1.0/clusters -X POST -d "name=${cluster_name}" -d "provider=custom" -d "type=mesos"
```

Update config

```
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=52.71.23.21,172.29.13.62" -d "ssh_user=centos" -d "sshkeydata=`cat ~/.ssh/reference.pem | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

Create group of slaves

```
curl -X POST -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

Deploy cluster's infrastructure

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure -X PUT
```

Provision cluster

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision -X PUT
```

Delete cluster configs, etc

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name} -X DELETE
```


Common usage scenario for DCOS on AWS
-------------------------------------

Create cluster

```
curl -X POST -d "name=${cluster_name}" -d "provider=aws" -d "type=dcos" http://localhost:5555/api/v1.0/clusters
```

Update config

```
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-east-1" -d "sshkey=reference" -d "sshkeydata=`cat ~/.ssh/reference.pem | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

Create group of slaves

```
curl -X POST -d "instance_type=r3.xlarge" -d "name=${group_name}" -d "role=myslaves" -d "attributes={\"type\":\"myslaves\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=12" -d "ram=60" -d "disk_size=200" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

Deploy cluster's infrastructure

```
curl -X PUT -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

Provision cluster

```
curl -X PUT http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision
```

Destroy cluster

```
curl -X DELETE -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure
```

Delete clusters config, etc:

```
curl -X DELETE http://localhost:5555/api/v1.0/clusters/${cluster_name}
```


Common usage scenario for DCOS on Azure
---------------------------------------

Create cluster

```
curl -X POST -d "name=${cluster_name}" -d "provider=azure" -d "type=dcos" http://localhost:5555/api/v1.0/clusters
```

Update config

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/config -X PUT -d "location=Central US" -d "masters=3" -d "ssh_password=${ssh_password}" -d "ssh_user=${ssh_user}" -d "master_type=Basic_A2"
```

Create group of slaves

```
curl -X POST -d "instance_type=Basic_A2"  -d "name=${group_name}" -d "role=myslaves" -d "attributes={\"type\":\"myslaves\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=12" -d "ram=60" -d "disk_size=200" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

Deploy cluster's infrastructure

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure -X PUT -d "credentials=`cat credentials | base64 | tr '+/' '-_'`"
```

Provision cluster

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision -X PUT
```

Destroy cluster

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure -X DELETE -d "credentials=`cat credentials | base64 | tr '+/' '-_'`"
```

Delete cluster configs, etc

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name} -X DELETE
```

Common usage scenario for DCOS on Custom Provider
-------------------------------------------------

Create cluster

```
curl -X POST -d "name=${cluster_name}" -d "provider=custom" -d "type=dcos" http://localhost:5555/api/v1.0/clusters
```

Update config

```
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=52.71.23.21,172.29.13.62" -d "ssh_user=centos" -d "sshkeydata=`cat ~/.ssh/reference.pem | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v1.0/clusters/${cluster_name}/config
```

Create group of slaves

```
curl -X POST -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```

Deploy cluster's infrastructure

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure -X PUT -d "credentials=`cat credentials | base64 | tr '+/' '-_'`"
```

Provision cluster

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/provision -X PUT
```

Delete cluster configs, etc

```
curl http://localhost:5555/api/v1.0/clusters/${cluster_name} -X DELETE
```


Mesos Cli Cluster Access
------------------------

There are mesos-cli available on terminal
For transparent usage it is recommended to switch to user "manager" first:
```
su -l manager
```
Mesos cli documentation:

https://github.com/mesosphere/mesos-cli


Mesos Cluster VPN Access
------------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl -X http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure and get _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${cluster_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${cluster_name}.ovpn file
6. Import this config into Tunnelblick by double clicking on ovpn file
7. Connect to VPN using credentials from step 3)
8. Following services are available

Mesos:
```
http://leader.mesos.service.${cluster_name}:5050/
```
Marathon:
```
http://leader.mesos.service.${cluster_name}:18080/
```
Consul:
```
http://leader.mesos.service.${cluster_name}:8500/
```

DCOS Cluster VPN Access
-----------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/infrastructure and save _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v1.0/clusters/${cluster_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${cluster_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${cluster_name}.ovpn file
6. Import this config into Tunnelblick by double clicking on ovpn file
7. Connect to VPN using credentials from step 3)
8. Following services are available

DCOS GUI:
```
http://192.168.164.1/
```
Mesos:
```
http://192.168.164.1/mesos/
```
Marathon:
```
http://192.168.164.1/marathon/
```

Raid and single disk handling
-----------------------------

In order to have raids and disks handling, we need to pass raid/disk structure inside group's vars in escaped JSON format

Structure format:

For RAID handling:
```
raids:
  ${raid_number}:
    mountpoint: "${mount_directory}"
    fstype: "${filesystem}"
    level: "${raid_level}"
    devices:
      - /dev/${one_disk}
      - /dev/${another_disk}
```
Where

${raid_number} is unsigned integer value, e.g. 0, 1, 2

${mount_directory} - is arbitrary directory in the system, for example, /data

${filesystem} - is file system type, for example, xfs, ext4

${raid_level} - is RAID's level, e.g. 0, 1, 5, 6, etc

${one_disk} - disk device name, for example, xvdx

${another_disk} - another disk device name, for example, xvdy


For Disk handling:

```
disks:
  ${disk_name}:
    mountpoint: "${mount_directory}"
    fstype: "${filesystem}"
```

Where

${disk_name} - disk device name, for example, xvdz

${mount_directory} - is arbitrary directory in the system, for example, /commitlog

${filesystem} - is file system type, for example, xfs, ext4

Example of creation of group with raid and disks handling

```
curl -X POST -d "instance_type=r3.xlarge" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"raids\":{\"0\":{\"mountpoint\":\"/data\",\"fstype\":\"xfs\",\"level\":\"0\",\"devices\":[\"/dev/xvdx\",\"/dev/xvdy\"]}},\"disks\":{\"xvdz\":{\"mountpoint\":\"/commitlog\",\"fstype\":\"xfs\"}}}" -d "cpus=10" -d "ram=64" -d "disk_size=50" -d "customhwconf={\"ebs_block_device\":[{\"device_name\":\"/dev/sdx\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdy\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdz\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"}]}" http://localhost:5555/api/v1.0/clusters/${cluster_name}/groups
```
