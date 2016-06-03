Grid Config API Requests
========================

Consider next parameters:

`${api_host}` - hostname with running API service, for example, `localhost`

`${grid_name}` - name of grid, for example, `examplegrid`, should consist of
only lowercase letters and numbers, should be started with lowercase letter and
be up to 16 characters long

 

Provider Independent HTTP parameters
------------------------------------

`${vars}` - sequence of key-value parameters in escaped json format, example:
`{\”foo\”:\”bar\”}`

### Available vars

| Grid type  | IAAS | key            | value               | description                                          |
|------------|------|----------------|---------------------|------------------------------------------------------|
| mesos only | All  | aurora         | true/false          | enables or disables aurora framework, default false  |
| mesos only | All  | mesos\_version | 0.23-0.XX           | Version of Mesos installed                           |
| mesos/dcos | All  | vpn\_enabled   | true/false          | enables or disables OpenVPN access, default true     |
| mesos/dcos | All  | enable\_duo    | true/false          | enable or disable duo auth(duo.com), default false   |
| mesos/dcos | All  | duo\_ikey      |                     | duo.com ikey, make sense, if enable\_duo is true     |
| mesos/dcos | All  | duo\_skey      |                     | duo.com skey, make sense, if enable\_duo is true     |
| mesos/dcos | All  | duo\_host      |                     | duo.com api host, make sense, if enable\_duo is true |
| dcos       | All  | dcos\_user     |                     | username for DCOS WEB UI, mandatory for DCOS EE      |
| dcos       | All  | dcos\_pass     |                     | password for DCOS WEB UI, mandatory for DCOS EE      |
| dcos       | All  | dcos\_version  | consumer/enterprise | Choose version of DCOS for deployment.               |

 

AWS HTTP parameters
-------------------

`${masters}` - key-value configuration of master-to-az mapping in escaped json
format, example: `{\"a\":\"1\",\"b\":\"1\",\"d\":\"1\"}`

`${master_type}` - AWS machine type for masters, for example, `m3.large`

`${region}` - AWS region for cluster placing, for example, `us-west-2`

`${sshkey}` - existing AWS SSH key `name` server SSH access

`${sshkeydata}` - URL encoded(--data-urlencode in curl) private part of SSH key

`${ssh_user}` - SSH user name, which is used in AWS (for example, `centos` in
CentOS machines, `ubuntu` in Ubuntu machines, default is `centos`)

 

Azure HTTP parameters
---------------------

`${masters}` - integer number of masters to deploy

`${master_type}` - Azure machine type for masters, for example, `Basic_A2`

`${location}` - Azure location for cluster placing, for example, `europenorth`

`${ssh_user}` - SSH user name, for using in virtual machines

`${ssh_password}` - SSH password for using in pair with `${ssh_user}`

 

GCE HTTP parameters
-------------------

`${masters}` - integer number of masters to deploy

`${master_type}` - GCE machine type for masters, for example, `n1-standard-1`

`${zone}` - GCE zone for cluster placing, for example, `europe-west1-b`

`${ssh_user}` - SSH user name, for using in virtual machines

`${sshkeydata}` - URL encoded(--data-urlencode in curl) private part of SSH key

 

OpenStack HTTP parameters
-------------------------

`${masters}` - integer number of masters to deploy

`${master_type}` - OpenStack machine type for masters, for example `m1.small`

`${terminal_type}` - OpenStack machine type for access server, for example
`m1.small`

`${image_name}` - OpenStack image name for instances, for example `centos-7`

`${floating_ip_pool}` - name of OpenStack pool with floating ips

`${tenant}` - OpenStack tenant name for VMs placing

`${region}` - OpenStack region name for VMs placing

`${external_network_uuid}` - UUID of external network foc cluster connection

`${ssh_user}` - SSH user name, for using in virtual machines

`${sshkeydata}` - URL encoded(--data-urlencode in curl) private part of SSH key

 

Bare Metal HTTP parameters
--------------------------

`${mastersips}` - comma separated list if internal ip addresses of master
servers, for example: `“10.10.10.2,10.10.10.3,10.10.104”`

`${terminalips}` - comma separated pair of external and internal ip addresses of
access server, for example: `“123.123.123.123,10.10.10.254”`

`${ssh_user}` - SSH user name, which is pre-created in servers

`${sshkeydata}` - URL encoded(--data-urlencode in curl) private part of SSH key,
public part of which is pre-setup-ed in servers

 

API requests
------------

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns grid’s general config

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### DELETE

Removes grid’s config from database

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### PUT

changes(rewrites, so all options should be specified) grid’s general config

AWS Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=m3.large" -d "masters={\"a\":\"1\",\"b\":\"2\"}" -d region="us-west-2" -d "sshkey=mysshkey" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" -d "ssh_user=centos" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Azure Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=Basic_A2" -d "masters=3" -d location="europenorth" -d "ssh_password=megapassword" -d "ssh_user=centos" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GCE Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=n1-standard-1" -d "masters=3" -d zone="europe-west1-b" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "vars={\"mesos_version\":\"0.26.0\"}" -d "master_type=m1.medium" -d "terminal_type=m1.medium" -d "image_name=centos7" -d "tenant=facebook147846732274467" -d "region=RegionOne" -d "external_network_uuid=0e43db46-8fd9-4ef1-8826-4cf9e809aede" -d "masters=1" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bare Metal example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=123.123.123.123,172.29.13.62" -d "ssh_user=centos" --data-urlencode "sshkeydata=`cat ~/.ssh/id_rsa`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
