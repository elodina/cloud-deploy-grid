Grid Entity API Requests
========================

Grid List API Requests
----------------------

Consider next parameters:

`${api_host}` - hostname with running API service, for example, `localhost`

`${grid_name}` - name of grid, for example, `examplegrid`, should consist of
only lowercase letters and numbers, should be started with lowercase letter and
be up to 16 characters long

`${iaas_provider}` - IAAS provider, for deploying grid to, currently supported:

-   aws

    -   azure

    -   custom

    -   gce

    -   openstack

`${grid_type}` - type of grid, currently supported:

-   mesos

    -   dcos

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns list of grids, present in API

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### POST

adds new grid to API

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "name=${grid_name}" -d "provider=${iaas_provider}" -d "type=${grid_type}" http://${api_host}:5555/api/v2.0/grids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

Grid Entity API Requests
------------------------

Consider next parameters:

`${api_host}` - hostname with running API service, for example, `localhost`

`${grid_name}` - name of grid, for example, `examplegrid`, should consist of
only lowercase letters and numbers, should be started with lowercase letter and
be up to 16 characters long

`${iaas_provider}` - IAAS provider, for deploying grid to, currently supported:

-   aws

    -   azure

    -   custom

    -   gce

    -   openstack

`${grid_type}` - type of grid, currently supported:

-   mesos

    -   dcos

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns grid’s status

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### DELETE

Removes grid config and state only from database, all deployed machines stay
alive

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
