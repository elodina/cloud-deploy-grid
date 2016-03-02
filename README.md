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

required parameters - name(variable), provider(aws/azure/custom), type(mesos/dcos)


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

CUSTOM:
```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

required parameters:

aws:

aws_access_key_id(self descriptive,URL-encoded, e.g. curl --data-urlencode "${key}=${value}"), aws_secret_access_key(self descriptive,URL-encoded, e.g. curl --data-urlencode "${key}=${value}")


optional parameters:

common:

vpn_enabled - by default == 'True', if True - enable VPN server provisioinig, otherwise - disable

duo_ikey, duo_skey, duo_host - duo security api parameters(duo.com) for vpn auth, URL-encoded, e.g. curl --data-urlencode "${key}=${value}"
PREREQUISITS FOR MFA:
1) Created application at duo.com(Auth API)

2) Created user at duo.com with added Mobile Device

3) Installed duo.com mobile app on mobile device(the only supported way for now)


It is possible to provision separate group, calling
```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
```

required parameters are the same as for grid provision calls





