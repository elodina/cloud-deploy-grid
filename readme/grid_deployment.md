Deployment Entity API Requests
==============================

Consider next parameters:

`${api_host}` - hostname with running API service, for example, `localhost`

`${grid_name}` - name of grid, for example, `examplegrid`, should consist of
only lowercase letters and numbers, should be started with lowercase letter and
be up to 16 characters long

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns grid’s deployment status.

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}/deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Table of statuses:

| Status                         | Description                                                                       |
|--------------------------------|-----------------------------------------------------------------------------------|
| init                           | No deployment was performed yet, initial state                                    |
| infrastructure\_deploying      | Deployment of infrastructure is in progress                                       |
| infrastructure\_deploy\_failed | Deployment of infrastructure failed. See docker logs for details                  |
| infrastructure\_deployed       | Deployment of infrastructure was successful. It is possible to run provision now. |
| infrastructure\_destroying     | Infrastructure destruction in progress                                            |
| destroyed                      | Infrastructure was destroyed                                                      |
| destroy\_failed                | Infrastructure destruction failed. See docker logs for details                    |
| provision\_deploying           | Provision of servers is in progress                                               |
| provision\_deploy\_failed      | Provision of servers failed. See docker logs for details                          |
| provision\_finished            | Provision of servers finished. You may access cluster and use it.                 |
