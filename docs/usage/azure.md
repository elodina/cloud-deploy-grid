
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






Common usage scenario for DCOS on Azure
---------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=azure" -d "type=dcos" http://localhost:5555/api/v2.0/grids
```

Update config

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/config -X PUT -d "location=Central US" -d "masters=3" -d "ssh_password=${ssh_password}" -d "ssh_user=${ssh_user}" -d "master_type=Basic_A2"
```

Create group of slaves

```
curl -X POST -d "instance_type=Basic_A2"  -d "name=${group_name}" -d "role=myslaves" -d "attributes={\"type\":\"myslaves\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=12" -d "ram=60" -d "disk_size=200" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure -X PUT -d "credentials=`cat credentials | base64 | tr '+/' '-_'`"
```

Provision grid

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision -X PUT
```

Destroy grid

```
curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure -X DELETE -d "credentials=`cat credentials | base64 | tr '+/' '-_'`"
```

Delete grid configs, etc

```
curl http://localhost:5555/api/v2.0/grids/${grid_name} -X DELETE
```

Common usage scenario for DCOS on Custom Provider
-------------------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=custom" -d "type=dcos" http://localhost:5555/api/v2.0/grids
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