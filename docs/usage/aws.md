Common usage scenario for AWS
--------------------------------------

Create grid

```
curl -X POST -d "name=${grid_name}" -d "provider=aws" -d "type=mesos" http://localhost:5555/api/v2.0/grids
```

Update config

```
curl -X PUT -d "master_type=m3.large" -d "masters=3" -d region="us-west-2" -d "sshkey=reference" -d "sshkeydata=`cat ~/.ssh/reference.pem | base64 -w 0 | tr '+/' '-_'`" http://localhost:5555/api/v2.0/grids/${grid_name}/config
```

Create group of slaves

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"foo\":\" bar\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=10" -d "ram=64" -d "disk_size=50" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Deploy grid's infrastructure

```
curl -X PUT -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Provision grid

```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

Change slaves group size:

```
curl -X POST -d "name=${group_name}" -d "role=role1" -d "attributes={\"purpose\":\"log_storing\"}" -d "vars={\"x_factor\":\"42\"}" -d "cpus=20" -d "ram=128" -d "disk_size=50" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```

Apply changes to infrastructure

```
curl -X PUT -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Provision fresh nodes

```
curl -X PUT http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/provision
```

Destroy grid

```
curl -X DELETE -d aws_access_key_id=${key_id} -d "aws_secret_access_key=${secret}" http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure
```

Delete grids config, etc:

```
curl -X DELETE http://localhost:5555/api/v2.0/grids/${grid_name}
```
