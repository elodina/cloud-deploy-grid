How to
======

Consider next parameters:

`${api_host}` - hostname with running API service, for example, `localhost`

`${grid_name}` - name of grid, for example, `examplegrid`, should consist of
only lowercase letters and numbers, should be started with lowercase letter and
be up to 16 characters long

Running Cloud Deploy Grid
-------------------------

-   [Run Cloud Deploy Grid in development
    mode](#Run-Cloud-Deploy-Grid-in-development-mode)

-   Run Cloud Deploy Grid using Stack Deploy in Development Mode

-   Run Cloud Deploy Grid using Stack Deploy with existing Cassandra cluster

Basic operations
----------------

-   [Run mesos on AWS](#Run mesos on AWS)

-   [Run mesos on Azure](#Run mesos on Azure)

-   [Run mesos on GCE](#Run mesos on GCE)

-   [Run mesos on OpenStack](#Run mesos on OpenStack)

-   [Run mesos on Bare Metal](#Run mesos on Bare Metal)

-   [Run dcos on AWS](#Run dcos on AWS)

-   [Run dcos on Azure](#Run dcos on Azure)

-   [Run dcos on GCE](#Run dcos on GCE)

-   [Run dcos on OpenStack](#Run dcos on OpenStack)

-   [Run dcos on Bare Metal](#Run dcos on Bare Metal)

-   Access cluster via VPN

Advanced operations
-------------------

-   Expand/shrink group size

-   Heal group with destroyed group instances

-   Create VMs with additional disks and configure RAID with them

-   Use Duo Auth Security

-   Unlock database in case of API crash

-   Run particular version of Mesos

-   Use AWS spot instances

-   Use GCE preemptible instances

 

### Run Cloud Deploy Grid in development mode

Just clone the repo and execute `./run.sh`

API will bi available at:

`http://localhost:5555/api/v2.0/`

 

### Run mesos on AWS

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=aws" -d "type=mesos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-east-1" -d "sshkey=my_ssh_key" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=m3.large" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "cpus=1" -d "ram=20" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run mesos on Azure

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=azure" -d "type=mesos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=Basic_A2" -d "masters=3" -d location="europenorth" -d "ssh_password=megapassword" -d "ssh_user=centos" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=Standard_DS11"  -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=6" -d "ram=30" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run mesos on GCE

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=gce" -d "type=mesos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=n1-standard-1" -d "masters=3" -d zone="europe-west1-b" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "zone=europe-west1-b" -d "instance_type=n1-standard-2" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "cpus=1" -d "ram=10" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run mesos on OpenStack

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=openstack" -d "type=mesos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=m1.medium" -d "terminal_type=m1.medium" -d "image_name=centos7" -d "tenant=${tenant}" -d "region=${region}" -d "external_network_uuid=${network_uuid}" -d "masters=1" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=m1.medium" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "slaves=1" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run mesos on Bare Metal

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=custom" -d "type=mesos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=123.123.123.123,172.29.13.62" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run dcos on AWS

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=aws" -d "type=dcos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-east-1" -d "sshkey=my_ssh_key" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=m3.large" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "cpus=1" -d "ram=20" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode aws_access_key_id=${key_id} --data-urlencode "aws_secret_access_key=${secret}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run dcos on Azure

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=azure" -d "type=dcos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=Basic_A2" -d "masters=3" -d location="europenorth" -d "ssh_password=megapassword" -d "ssh_user=centos" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=Standard_DS11"  -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=6" -d "ram=30" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run dcos on GCE

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=gce" -d "type=dcos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=n1-standard-1" -d "masters=3" -d zone="europe-west1-b" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "zone=europe-west1-b" -d "instance_type=n1-standard-2" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "cpus=1" -d "ram=10" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run dcos on OpenStack

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=openstack" -d "type=dcos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=m1.medium" -d "terminal_type=m1.medium" -d "image_name=centos7" -d "tenant=${tenant}" -d "region=${region}" -d "external_network_uuid=${network_uuid}" -d "masters=1" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=m1.medium" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "slaves=1" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destroy grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Run dcos on Bare Metal

Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=custom" -d "type=dcos" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update config

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=123.123.123.123,172.29.13.62" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy grid's infrastructure

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provision grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete grids config, etc:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
