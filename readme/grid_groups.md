Grid Group Entity API Requests
==============================

Consider next parameters:

`${api_host}` - hostname with running API service, for example, `localhost`

`${grid_name}` - name of grid, for example, `examplegrid`, should consist of
only lowercase letters and numbers, should be started with lowercase letter and
be up to 16 characters long

`${group_name}` - name of group

`${vars}` - sequence of key-value parameters in escaped json format, example:
`{\”foo\”:\”bar\”}`

### Available vars:

| key   | value                                                                                                                                       | description                                                                                                                                                                                                                                  | example                                                                                                                                        |
|-------|---------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| raids | {\${raid\_number}: mountpoint: \${path}, raid\_level: \${raid\_level}, fstype: \${file\_system\_type}, devices:[ \${disk\_devices\_list} ]} | Creates Raid and mounts it.                                                                                                                                                                                                                  | {\\"raids\\":{\\"0\\":\\"mountpoint\\":\\"/data\\",\\"fstype\\":\\"xfs\\",\\"level\\":\\"0\\",\\"devices\\":[\\"/dev/xvdx\\",\\"/dev/xvdy\\"]} |
|       |                                                                                                                                             | Parameters:                                                                                                                                                                                                                                  |                                                                                                                                                |
|       |                                                                                                                                             | \${raid\_number} - integer number of raid                                                                                                                                                                                                    |                                                                                                                                                |
|       |                                                                                                                                             | \${path} - destination mountpoint                                                                                                                                                                                                            |                                                                                                                                                |
|       |                                                                                                                                             | \${file\_system\_type} - type of filesystem(xfs/ext4/etc)                                                                                                                                                                                    |                                                                                                                                                |
|       |                                                                                                                                             | \${disk\_devices\_list} - list of disk device names, e,g, /dev/xvda                                                                                                                                                                          |                                                                                                                                                |
| disks | {\${disk\_name}: mountpoint: \${path}, fstype: \${file\_system\_type}}                                                                      | Format and mounts single disk                                                                                                                                                                                                                | {\\"disks\\":{\\"xvdz\\":{\\"mountpoint\\":\\"/commitlog\\",\\"fstype\\":\\"xfs\\"}}}                                                          |
|       |                                                                                                                                             | Parameters:                                                                                                                                                                                                                                  |                                                                                                                                                |
|       |                                                                                                                                             | \${disk\_name} - disk name, present in /dev/ catalog, example - xvdx                                                                                                                                                                         |                                                                                                                                                |
|       |                                                                                                                                             | \${path} - destination mountpoint                                                                                                                                                                                                            |                                                                                                                                                |
|       |                                                                                                                                             | \${file\_system\_type} - type of file system(xfs/ext4/etc                                                                                                                                                                                    |                                                                                                                                                |

Provider Independent Group HTTP parameters
------------------------------------------

`${name}` - name of slave group to manage, for example, `infra`, should consist
of only lowercase letters and numbers, should be started with lowercase letter
and be up to 16 characters long

`${role}` - role of group, for example, `infra`, should consist of only
lowercase letters and numbers, should be started with lowercase letter and be up
to 16 characters long

`${attributes}` - key-value sequence of mesos attributes in escaped json format,
example: `{\"attr1\":\"foo\",\"attr2\":\"bar\"}`

`${attributes}` - key-value sequence of additional ansible variables for
particular group in escaped json format, example: `{\"foo\":\"bar\"}`

 

AWS Group HTTP parameters
-------------------------

`${cpus}` - integer minimum amount of CPU cores per group

`${ram}` - integer minimum amount of GB of RAM per group

`${disk_size}` - root disk size

`${customhwconf}` - custom hardware configuration to slaves in escaped json
format. Configuration structure and values should consist of
terraform(https://www.terraform.io/docs/configuration/syntax.html)
configuration.

More detailed description both with examples is described in separate topic:
[customhwconf](customhwconf.md)

`${instance_type}` - AWS machine type for slaves, for example, `m3.large`

`${enhanced_networking}` - true/false - if true,
enhanced\_networking(http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking.html)
will be turned on for instances.

`${az}` - Availability zone for VMs placing, for example `a`

`${ssh_user}` - SSH user name, which is used in AWS (for example, `centos` in
CentOS machines, `ubuntu` in Ubuntu machines, default is `centos`)

`${spot_price}` - spot price(https://aws.amazon.com/ru/ec2/spot/) for instances.
WARNING! If this parameter is defined, all instances in group become spot.
WARNING! If you spot instances will be destroyed due to low price, they become
unmanaged ny api. Correct workaround of this is:

1.  set resources of group to 0(both CPU, RAM)

2.  make infrastructure deployment `PUT` call(machines in group will be
    destroyed)

3.  set desirable resources of group

4.  make infrastructure deployment `PUT` call(machines will be recreated)

5.  make group provision deployment `PUT` call

 

Azure Group HTTP parameters
---------------------------

`${cpus}` - integer minimum amount of CPU cores per group

`${ram}` - integer minimum amount of GB of RAM per group

`${disk_size}` - root disk size

`${customhwconf}` - custom hardware configuration to slaves in escaped json
format. Configuration structure and values should consist of
terraform(https://www.terraform.io/docs/configuration/syntax.html)
configuration.

More detailed description both with examples is described in separate topic:
[customhwcon]

`${instance_type}` - Azure machine type for slaves, for example, `Standard_DS11`

 

GCE Group HTTP parameters
-------------------------

`${cpus}` - integer minimum amount of CPU cores per group

`${ram}` - integer minimum amount of GB of RAM per group

`${disk_size}` - root disk size

`${customhwconf}` - custom hardware configuration to slaves in escaped json
format. Configuration structure and values should consist of
terraform(https://www.terraform.io/docs/configuration/syntax.html)
configuration.

More detailed description both with examples is described in separate topic:
[customhwcon]

`${instance_type}` - GCE machine type for slaves, for example, `n1-standard-2`

`${zone}` - GCE zone to place group to

`${preemptible}` - makes instance
preemptible(https://cloud.google.com/compute/docs/instances/preemptible)

 

OpenStack Group HTTP parameters
-------------------------------

`${slaves}` - integer number of slaves to deploy

`${instance_type}` - OpenStack machine type for slaves, for example `m1.small`

`${customhwconf}` - custom hardware configuration to slaves in escaped json
format. Configuration structure and values should consist of
terraform(https://www.terraform.io/docs/configuration/syntax.html)
configuration.

More detailed description both with examples is described in separate topic:
[customhwcon]`​`

 

Bare Metal Group HTTP parameters
--------------------------------

`${groupips}` - comma separated list if internal ip addresses of group servers,
for example: `“10.10.10.20,10.10.10.30,10.10.10.40”`

 

Grid Groups List API Requests
-----------------------------

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns list of groups

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### POST

adds new slave group to grid

AWS Group Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "az=a" -d "enhanced_networking=True" -d "instance_type=r3.xlarge" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"raids\":{\"0\":{\"mountpoint\":\"/data\",\"fstype\":\"xfs\",\"level\":\"0\",\"devices\":[\"/dev/xvdx\",\"/dev/xvdy\"]},\"1\":{\"mountpoint\":\"/data2\",\"fstype\":\"xfs\",\"level\":\"1\",\"devices\":[\"/dev/xvdv\",\"/dev/xvdw\"]}},\"disks\":{\"xvdz\":{\"mountpoint\":\"/commitlog\",\"fstype\":\"xfs\"}}}" -d "cpus=10" -d "ram=64" -d "disk_size=50" -d "customhwconf={\"ebs_block_device\":[{\"device_name\":\"/dev/sdv\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdw\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdx\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdy\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdz\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"}]}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Azure Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=Standard_DS11"  -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=6" -d "ram=30" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GCE Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "zone=europe-west1-b" -d "instance_type=n1-standard-2" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "cpus=1" -d "ram=10" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "instance_type=m1.medium" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "slaves=1" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bare Metal Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X POST -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

Grid Group Entity API requests
------------------------------

### BASE URL

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### GET

returns group’s config

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X GET http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### DELETE

Removes group only from database

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X DELETE http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/${group_name}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### PUT

changes(rewrites, so all options should be specified) group’s config.

AWS Group Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "az=a" -d "enhanced_networking=True" -d "instance_type=r3.xlarge" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"raids\":{\"0\":{\"mountpoint\":\"/data\",\"fstype\":\"xfs\",\"level\":\"0\",\"devices\":[\"/dev/xvdx\",\"/dev/xvdy\"]},\"1\":{\"mountpoint\":\"/data2\",\"fstype\":\"xfs\",\"level\":\"1\",\"devices\":[\"/dev/xvdv\",\"/dev/xvdw\"]}},\"disks\":{\"xvdz\":{\"mountpoint\":\"/commitlog\",\"fstype\":\"xfs\"}}}" -d "cpus=10" -d "ram=64" -d "disk_size=50" -d "customhwconf={\"ebs_block_device\":[{\"device_name\":\"/dev/sdv\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdw\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdx\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdy\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdz\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"}]}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/infra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Azure Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "instance_type=Standard_DS11"  -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"foo\":\"bar\"}" -d "cpus=6" -d "ram=30" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/infra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GCE Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "zone=europe-west1-b" -d "instance_type=n1-standard-2" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "cpus=1" -d "ram=10" -d "disk_size=50" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/infra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "instance_type=m1.medium" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "slaves=1" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/infra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bare Metal Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
curl -X PUT -d "groupips=172.29.5.134,172.29.12.227,172.29.9.93" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" http://${api_host}:5555/api/v2.0/grids/${grid_name}/groups/infra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
