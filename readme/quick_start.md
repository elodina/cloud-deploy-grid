Quick Start
===========

 

Hardware Prerequisites
----------------------

-   RAM \>= 8Gb

-   HDD free space \>= 1Gb

 

Software Prerequisites
----------------------

### GNU/Linux

Latest versions of installed packages:

-   Docker

-   Docker-compose

-   Curl

-   OpenVPN client

### Mac OS

Latest versions of installed packages:

-   Vagrant

-   Curl

-   OpenVPN client

 

IAAS Prerequisites
------------------

### AWS

-   aws\_access\_key\_id

-   aws\_secret\_access\_key

These keys should have full access to EC2 operations

 

Running of CDG API
------------------

### On GNU/Linux

1.  clone this repo

2.  execute `./run.sh`

### On Mac OS

1.  clone this repo

2.  execute `vagrant up`

3.  ssh vagrant\@127.0.0.1 -p 2222; password - vagrant

4.  (In vagrant) execute `cd /vagrant`

5.  (In vagrant) execute `./run`

 

Creating simple Mesos cluster on top of AWS 
--------------------------------------------

Create ssh key pair in AWS and name it “example\_key”

Save private path of this key to `~/.ssh/example_key.pem` and set correct access
rights to it (`chmod 400` `~/.ssh/example_key.pem`)

 

### Define all necessary variables

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
grid_name="example"
aws_access_key_id="<your_aws_access_key>"
aws_secret_access_key="<your_aws_secret_key>"
aws_region="us-west-2"
aws_ssh_key="example_key"
group_name="infra"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Create grid

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=aws" -d "type=mesos" http://localhost:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Set grid’s config parameters

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "master_type=m3.medium" -d "masters=3" -d region="${aws_region}" -d "sshkey=${aws_ssh_key}" --data-urlencode "sshkeydata=`cat ~/.ssh/example_key.pem`" http://localhost:5555/api/v2.0/grids/${grid_name}/config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Create group of slaves

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${group_name}" -d "role=infra" -d "attributes={\"type\":\" infra\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=1" -d "ram=4" -d "disk_size=20" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Deploy grid’s infrastructure(empty virtual machines, networking, etc)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode aws_access_key_id=${aws_access_key_id} --data-urlencode "aws_secret_access_key=${aws_secret_access_key}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wait for infrastructure deployment finish.  
Status of

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://localhost:5555/api/v2.0/grids/${grid_name}/deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Should be `infrastructure_deployed`

 

### Provision grid’s machines with software

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode aws_access_key_id=${aws_access_key_id} --data-urlencode "aws_secret_access_key=${aws_secret_access_key}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wait for provision finish.  
Status of

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://localhost:5555/api/v2.0/grids/${grid_name}/deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Should be `provision_finished`

 

Accessing of newly created cluster
----------------------------------

### Get OpenVPN config

Execute

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo -e `curl -qs http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/vpn | tr -d '"'` > vpn.ovpn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Get IP-address of access server

Execute

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

And save ip-address from `accessip` field.

 

### Getting necessary VPN credentials

Ssh to `accessip`:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ssh -i ~/.ssh/example_key.pem centos@<accessip>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

Create user and passwd it:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sudo adduser exampleuser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sudo passwd exampleuser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

Get ca.crt file at the \<accessip\> server and save it as ca.crt near the
vpn.ovpn file

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sudo cat /etc/openvpn/keys/ca.crt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### VPN Connecting

Import VPN.ovpn file in your OpenVPN client

Set up vpn connection to use this connection for routes that are getting only
from the connection itself(something like `local routes`).

 

Activate newly created VPN connection. Use `exampleuser` and its password for
authentication.

Ensure, that `192.168.164.1` is primary dns server.

 

### Accessing web interfaces

Mesos interface could be accessed by visiting next URL:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://leader.mesos.service.example:5050/
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Marathon interface could be accessed by visiting next URL:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://leader.mesos.service.example:18080/
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
