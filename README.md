Grid 2.0 API
===========

Table of Contents
=================

  * [Grid API](#grid-api)
    * [Prerequisites](#prerequisites)
    * [Current Limitations](#current-limitations)
    * [Preparation](#preparation)
    * [Grid List API Requests](#grid-list-api-requests)
    * [Grid Entity API Requests](#grid-entity-api-requests)
    * [Grid Config API Requests](#grid-config-api-requests)
    * [Grid Slave group list API Requests](#grid-slave-group-list-api-requests)
    * [Grid Slave group API Requests](#grid-slave-group-api-requests)
    * [Grid Deployment API Requests](#grid-deployment-api-requests)
    * [Common usage scenario for Mesos on AWS](#common-usage-scenario-for-mesos-on-aws)
    * [Common usage scenario for Mesos on GCS](#common-usage-scenario-for-mesos-on-gcs)
    * [Common usage scenario for Mesos on Azure](#common-usage-scenario-for-mesos-on-azure)
    * [Common usage scenario for DCOS on AWS](#common-usage-scenario-for-dcos-on-aws)
    * [Common usage scenario for DCOS on Azure](#common-usage-scenario-for-dcos-on-azure)
    * [Mesos Cli Grid Access](#mesos-cli-grid-access)
    * [Mesos Grid VPN Access](#mesos-grid-vpn-access)
    * [DCOS Grid VPN Access](#dcos-grid-vpn-access)

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
All names(grid, groups, etc) should consist of only lowercase letters and numbers, should be started with
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


Grid List API Requests
-------------------------

```
http://localhost:5555/api/v2.0/grids
```

Supported requests:

GET - get grid list, example:

```
curl http://localhost:5555/api/v2.0/grids
```

POST - add new grid, example:

```
curl -X POST -d "name=${grid_name}" -d "provider=aws" -d "type=mesos" http://localhost:5555/api/v2.0/grids
```

required parameters - name(variable), provider(aws/azure/gcs/custom), type(mesos/dcos)


Grid Entity API Requests
---------------------------

```
http://localhost:5555/api/v2.0/grids/${grid_name}
```

Supported requests:

GET - get grid status, example:

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}
```

DELETE - delete grid and its stuff, example:

```
curl -X DELETE http://localhost:5555/api/v2.0/grids/${grid_name}
```

Grid Config API Requests
---------------------------

```
http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

Supported requests:

GET - get grids config, example:

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

DELETE - delete grids config:

```
curl -X DELETE http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

PUT - change grids config:

```
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-west-2" -d "sshkey=reference" --data-urlencode "sshkeydata=`cat ~/.ssh/reference.pem`" http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

required parameters:

common:
masters(number of masters hosts)

aws:
master_type(AWS instance type for master, default m3.large), region(AWS region for grid), sshkey(AWS ssh key name), sshkeydata(Private path of ssh key, URL-encoded, e.g. curl --data-urlencode "${key}=${value}")

azure:
master_type(Azure instance type for master, default is Basic_A2), location(Azure location for grid in format like "Central US"), ssh_user(user for ssh login), ssh_password(password for ssh user and sudo)

gcs:
master_type(GCS instance type for master, default is n1-standard-1), zone(GCS Zone in format like "us-east1-a"), project(GCS project ID), ssh_user(user for ssh login), sshkeydata(Private path of ssh key, URL-encoded, e.g. curl --data-urlencode "${key}=${value}")

custom:
mastersips(Comma separated list of masters ips), terminalips(<terminal_external_ip>,<terminal_internal_ip>), ssh_user(ssh user for connection), sshkeydata(Private part of ssh key, URL-encoded, e.g. curl --data-urlencode "${key}=${value}")


Grid Slave group list API Requests
-------------------------------------

```
http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Supported requests:

GET - get grids slave groups, example:

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

POST - add new group, example:

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"foo\":\"bar\"}" -d "vars={\"foo\":\"bar\"}" -d "instance_type=r3.xlarge" -d "cpus=10" -d "ram=64" -d "disk_size=50" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```
required parameters - name(variable), role(variable), attributes(escaped json format), vars(escaped json format), instance_type(for AWS, for example - m3.large, for Azure, for example - Basic_A3), cpus(number of cpus per group), ram(amount of GB of ram per group), disk_size(hdd size, per HOST)

zone(GCS zone to place group to, GCS only), example:

```
-d "zone=us-east1-c"
```

optional parameters:

az(availability zone to place group to, AWS only), example:

```
-d "az=c"
```

customhwconf(escaped json format, look at https://www.terraform.io/docs/configuration/syntax.html), example:

```
{\"ebs_block_device\":[{\"device_name\":\"/dev/sdx\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"}]}
```
All of the new created disks will be mounted to /hdd/xvd{last letter of disk name, eg, x, y, whatever}


groupips(in custom provider, comma separated list of group ips)


preemptible(True/False in GCS, enables machine's preemptibility(https://cloud.google.com/preemptible-vms/), example:

```
-d "preemptible=True"
```


spot_price(only in AWS - group of slaves will be make of spot instances), example:

```
-d "spot_price=0.9"
```

Grid Slave group API Requests
--------------------------------

```
http://localhost:5555/api/v2.0/grids/${grid_name}/groups/${group_name}
```

Supported requests:

GET - get grids slave group parameters, example:

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/groups/${group_name}
```

DELETE - delete group, example:

```
curl -X DELETE http://localhost:5555/api/v2.0/grids/${grid_name}/groups/${group_name}
```

PUT - change group parameters, example:

```
curl -X PUT -d "name=group2" -d "role=role1" -d "attributes={\"foo\":\"bar\"}" -d "vars={\"var1\":\"varvalue1\"}" -d "instance_type=r3.xlarge" -d "cpus=10" -d "ram=64" -d "disk_size=50" http://localhost:5555/api/v2.0/grids/${grid_name}/groups/${group_name}
```

required parameters - name(variable), role(variable), attributes(escaped json format), vars(escaped json format), instance_type(for AWS, for example - m3.large, for Azure, for example - Basic_A3), cpus(number of cpus per group), ram(amount of GB of ram per group), disk_size(hdd size, per HOST)

zone(GCS zone to place group to, GCS only), example:

```
-d "zone=us-east1-c"
```


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


preemptible(True/False in GCS, enables machine's preemptibility(https://cloud.google.com/preemptible-vms/), example:

```
-d "preemptible=True"
```

Grid Deployment API Requests
-------------------------------

```
http://localhost:5555/api/v2.0/grids/${grid_name}/deployment
```

Supported requests:

GET - get grids deployment status, example:

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment
```

Grid Infrastructure Deployment API Requests
----------------------------------------------

```
http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Supported requests:

GET - get grids infrastructure deployment status, example:

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

DELETE - destroy grid's infrastructure(virtual machines, networks, etc), example:

```
curl -X DELETE http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

PUT - deploy grid's infrastructure(virtual machines, networks, etc), example:

AWS:
```
curl -X PUT --data-urlencode "aws_access_key_id=${key_id}" --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

AZURE:
```
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

GCS:
```
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

CUSTOM:
```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

required parameters:

common:
parallelism(number of deploy threads, higher number increase deployment speed, but may cause instability, default is 5)

aws:
aws_access_key_id(self descriptive,URL-encoded, e.g. curl --data-urlencode "${key}=${value}"), aws_secret_access_key(self descriptive,URL-encoded, e.g. curl --data-urlencode "${key}=${value}")

azure:
credentials(credentials file, can be aquired here: https://manage.windowsazure.com/publishsettings, URL-encoded, e.g. curl --data-urlencode "${key}=${value}")

gcs:
credentials(credentials file, should be aquired, as described here: https://www.terraform.io/docs/providers/google/index.html, URL-encoded, e.g. curl --data-urlencode "${key}=${value}")


Grid Provision API Requests
------------------------------

```
http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

Supported requests:

GET - get grids provision status, example:

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

PUT - run grid's provision(install software, configure settings, etc), example:

AWS:
```
curl -X PUT --data-urlencode "aws_access_key_id=${key_id}" --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

AZURE:
```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

GCS:
```
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

CUSTOM:
```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

required parameters:

aws:

aws_access_key_id(self descriptive,URL-encoded, e.g. curl --data-urlencode "${key}=${value}"), aws_secret_access_key(self descriptive,URL-encoded, e.g. curl --data-urlencode "${key}=${value}")


gcs:
credentials(credentials file, should be aquired, as described here: https://www.terraform.io/docs/providers/google/index.html, URL-encoded, e.g. curl --data-urlencode "${key}=${value}")


optional parameters:

common:

vpn_enabled - by default == 'True', if True - enable VPN server provisioinig, otherwise - disable

duo_ikey, duo_skey, duo_host - duo security api parameters(duo.com) for vpn auth, URL-encoded, e.g. curl --data-urlencode "${key}=${value}"

PREREQUISITS FOR MFA:
1) Created application at duo.com(Auth API)

2) Created user at duo.com with added Mobile Device

3) Installed duo.com mobile app on mobile device(the only supported way for now)

How to use MFA:

1) Create login(same as at duo.com) on Terminal server and passwd it

2) Create new VPN connection

3) password for vpn will be: "," example: "str0ng_pass,123123"



It is possible to provision separate group, calling
```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
```

required parameters are the same as for grid provision calls



Common usage scenario for Mesos on AWS
--------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=aws" -d "type=mesos" http://localhost:5555/api/v2.0/grids
```

Update config

```
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-west-2" -d "sshkey=reference" --data-urlencode "sshkeydata=`cat ~/.ssh/reference.pem`" http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

Create group of slaves

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"foo\":\" bar\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=10" -d "ram=64" -d "disk_size=50" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Provision grid

```
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

Change slaves group size:

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"purpose\":\"log_storing\"}" -d "vars={\"x_factor\":\"42\"}" -d "cpus=20" -d "ram=128" -d "disk_size=50" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Apply changes to infrastructure

```
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Provision fresh nodes

```
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
```

Destroy grid

```
curl -X DELETE --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Delete grids config, etc:

```
curl -X DELETE http://localhost:5555/api/v2.0/grids/${grid_name}
```


Common usage scenario for Mesos on Azure
----------------------------------------

Create grid

```
curl http://localhost:5555/api/v2.0/grids -X POST -d "name=${grid_name}" -d "provider=azure" -d "type=mesos"
```

Update config

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/config -X PUT -d "location=Central US" -d "masters=3" -d "ssh_password=${ssh_password}" -d "ssh_user=${ssh_user}" -d "master_type=Basic_A2"
```

Create group of slaves

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/groups -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"purpose\":\"analytics\"}" -d "vars={\"y_factor\":\"43\"}" -d "cpus=12" -d "ram=16" -d "disk_size=50" -d "instance_type=Standard_D11"
```

Deploy grid's infrastructure

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure -X PUT --data-urlencode "credentials=`cat credentials`"
```

Provision grid

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision -X PUT
```

Destroy grid

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure -X DELETE --data-urlencode "credentials=`cat credentials`"
```

Delete grid configs, etc

```
curl http://localhost:5555/api/v2.0/grids/${grid_name} -X DELETE
```

Common usage scenario for Mesos on GCS
--------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=gcs" -d "type=mesos" http://localhost:5555/api/v2.0/grids
```

Update config

```
curl -X PUT -d "project=super-project-123456" -d "vars={\"mesos_version\":\"0.26.0\"}" -d "master_type=n1-standard-1" -d "masters=3" -d zone="europe-west1-b" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

Create group of slaves

```
curl -X POST -d "zone=europe-west1-b" -d "instance_type=n1-standard-1" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "cpus=1" -d "ram=10" -d "disk_size=50" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Provision grid

```
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

Destroy grid

```
curl -X DELETE --data-urlencode "credentials=`cat credentials.json`" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Delete grid configs, etc

```
curl -X DELETE http://localhost:5555/api/v2.0/grids/${grid_name}
```


Common usage scenario for Mesos on Custom Provider
--------------------------------------------------

Create grid

```
curl http://localhost:5555/api/v2.0/grids -X POST -d "name=${grid_name}" -d "provider=custom" -d "type=mesos"
```

Update config

```
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=52.71.23.21,172.29.13.62" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/reference.pem`" http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

Create group of slaves

```
curl -X POST -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure -X PUT
```

Provision grid

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision -X PUT
```

Delete grid configs, etc

```
curl http://localhost:5555/api/v2.0/grids/${grid_name} -X DELETE
```

Common usage scenario for DCOS on AWS
-------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=aws" -d "type=dcos" http://localhost:5555/api/v1.0/grids
```

Update config

```
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-east-1" -d "sshkey=reference" --data-urlencode "sshkeydata=`cat ~/.ssh/reference.pem`" http://localhost:5555/api/v1.0/grids/${grid_name}/config
```

Create group of slaves

```
curl -X POST -d "instance_type=r3.xlarge" -d "name=${group_name}" -d "role=myslaves" -d "attributes={\"type\":\"myslaves\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=12" -d "ram=60" -d "disk_size=200" http://localhost:5555/api/v1.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/infrastructure
```

Provision grid

```
curl -X PUT http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/provision
```

Destroy grid

```
curl -X DELETE --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/infrastructure
```

Delete grids config, etc:

```
curl -X DELETE http://localhost:5555/api/v1.0/grids/${grid_name}
```


Common usage scenario for DCOS on Azure
---------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=azure" -d "type=dcos" http://localhost:5555/api/v1.0/grids
```

Update config

```
curl http://localhost:5555/api/v1.0/grids/${grid_name}/config -X PUT -d "location=Central US" -d "masters=3" -d "ssh_password=${ssh_password}" -d "ssh_user=${ssh_user}" -d "master_type=Basic_A2"
```

Create group of slaves

```
curl -X POST -d "instance_type=Basic_A2"  -d "name=${group_name}" -d "role=myslaves" -d "attributes={\"type\":\"myslaves\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=12" -d "ram=60" -d "disk_size=200" http://localhost:5555/api/v1.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/infrastructure -X PUT --data-urlencode "credentials=`cat credentials`"
```

Provision grid

```
curl http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/provision -X PUT
```

Destroy grid

```
curl http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/infrastructure -X DELETE --data-urlencode "credentials=`cat credentials`"
```

Delete grid configs, etc

```
curl http://localhost:5555/api/v1.0/grids/${grid_name} -X DELETE
```

Common usage scenario for DCOS on Custom Provider
-------------------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=custom" -d "type=dcos" http://localhost:5555/api/v1.0/grids
```

Update config

```
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=52.71.23.21,172.29.13.62" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/reference.pem`" http://localhost:5555/api/v1.0/grids/${grid_name}/config
```

Create group of slaves

```
curl -X POST -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://localhost:5555/api/v1.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/infrastructure -X PUT
```

Provision grid

```
curl http://localhost:5555/api/v1.0/grids/${grid_name}/deployment/provision -X PUT
```

Delete grid configs, etc

```
curl http://localhost:5555/api/v1.0/grids/${grid_name} -X DELETE
```

Mesos Cli Grid Access
------------------------

There are mesos-cli available on terminal
For transparent usage it is recommended to switch to user "manager" first:
```
su -l manager
```
Mesos cli documentation:

https://github.com/mesosphere/mesos-cli


Mesos Grid VPN Access
------------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl -X http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure and get _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${grid_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${grid_name}.ovpn file
6. Import this config into Tunnelblick by double clicking on ovpn file
7. Connect to VPN using credentials from step 3)
8. Following services are available

Mesos:
```
http://leader.mesos.service.${grid_name}:5050/
```
Marathon:
```
http://leader.mesos.service.${grid_name}:18080/
```
Consul:
```
http://leader.mesos.service.${grid_name}:8500/
```

DCOS Grid VPN Access
-----------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure and save _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${grid_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${grid_name}.ovpn file
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

Mesos Grid VPN Access
------------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl -X http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure and get _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${grid_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${grid_name}.ovpn file
6. Import this config into Tunnelblick by double clicking on ovpn file
7. Connect to VPN using credentials from step 3)
8. Following services are available

Mesos:
```
http://leader.mesos.service.${grid_name}:5050/
```
Marathon:
```
http://leader.mesos.service.${grid_name}:18080/
```
Consul:
```
http://leader.mesos.service.${grid_name}:8500/
```

DCOS Grid VPN Access
-----------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure and save _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${grid_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${grid_name}.ovpn file
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

