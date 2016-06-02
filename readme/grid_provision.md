Provision Deployment API Requests
=================================

Consider next parameters:

`${api_host}` - hostname with running API service, for example, `localhost`

`${grid_name}` - name of grid, for example, `examplegrid`, should consist of
only lowercase letters and numbers, should be started with lowercase letter and
be up to 16 characters long

 

AWS HTTP parameters
-------------------

`${aws_access_key_id}` - url-encoded aws\_access\_key\_id, details:
http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html

`${aws_secret_access_key}` - url-encoded aws\_secret\_access\_key, details:
http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html

 

Azure HTTP parameters
---------------------

`${credentials}` - url-encoded **content** of Azure credentials file, example:
`` --data-urlencode "credentials=`cat credentials`" `` For getting this file
look at https://www.terraform.io/docs/providers/azure/index.html

 

GCE HTTP parameters
-------------------

`${credentials}` - url-encoded **content** of GCE credentials file, example: ``
--data-urlencode "credentials=`cat credentials`" `` For getting this file look
at https://www.terraform.io/docs/providers/google/index.html

 

OpenStack HTTP parameters
-------------------------

`${api_url}` - OpenStack API URL, for example,
`http://123.123.123.123:5000/v2.0`

`${api_user}` - OpenStack API username

`${api_pass}` - OpenStack API password

 

Global Provision Deployment API Requests
========================================

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns grid’s provision deployment status

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### PUT

Perform provision(software set up and configuration) of cluster

AWS Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "aws_access_key_id=${aws_access_key_id} --data-urlencode "aws_secret_access_key=${aws_secret_access_key}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Azure Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GCE Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

Masters Provision Deployment API Requests
=========================================

This call is used for separate provisioning of master servers

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}/masters/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns master’s provision status

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}/masters/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### PUT

Perform provision(software set up and configuration) of masters

AWS Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "aws_access_key_id=${aws_access_key_id} --data-urlencode "aws_secret_access_key=${aws_secret_access_key}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/masters/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Azure Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/masters/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GCE Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/masters/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/masters/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

Masters Provision Deployment API Requests
=========================================

Consider next parameters:

`${group_name}` - name of group to provision

This call is used for separate provisioning of particular group

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns groups’s provision status

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### PUT

Perform provision(software set up and configuration) of group

AWS Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "aws_access_key_id=${aws_access_key_id} --data-urlencode "aws_secret_access_key=${aws_secret_access_key}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Azure Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GCE Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "credentials=`cat credentials.json`" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT --data-urlencode "api_user=asdasd" --data-urlencode "api_pass=xwqiocby98137cb" --data-urlencode "api_url=http://123.123.123.123:5000/v2.0" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}/provision
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
