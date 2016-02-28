Common usage scenario for Mesos on Custom Provider
--------------------------------------------------

Create grid

```
curl http://localhost:5555/api/v1.0/grids -X POST -d "name=${grid_name}" -d "provider=custom" -d "type=mesos"
```

Update config

```
curl -X PUT -d "mastersips=172.29.15.83,172.29.15.225,172.29.14.184" -d "terminalips=52.71.23.21,172.29.13.62" -d "ssh_user=centos" -d "sshkeydata=`cat ~/.ssh/reference.pem | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v1.0/grids/${grid_name}/config
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