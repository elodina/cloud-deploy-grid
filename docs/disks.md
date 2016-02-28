Raid and single disk handling
-----------------------------

In order to have raids and disks handling, we need to pass raid/disk structure inside group's vars in escaped JSON format

Structure format:

For RAID handling:
```
raids:
  ${raid_number}:
    mountpoint: "${mount_directory}"
    fstype: "${filesystem}"
    level: "${raid_level}"
    devices:
      - /dev/${one_disk}
      - /dev/${another_disk}
```
Where

${raid_number} is unsigned integer value, e.g. 0, 1, 2

${mount_directory} - is arbitrary directory in the system, for example, /data

${filesystem} - is file system type, for example, xfs, ext4

${raid_level} - is RAID's level, e.g. 0, 1, 5, 6, etc

${one_disk} - disk device name, for example, xvdx

${another_disk} - another disk device name, for example, xvdy


For Disk handling:

```
disks:
  ${disk_name}:
    mountpoint: "${mount_directory}"
    fstype: "${filesystem}"
```

Where

${disk_name} - disk device name, for example, xvdz

${mount_directory} - is arbitrary directory in the system, for example, /commitlog

${filesystem} - is file system type, for example, xfs, ext4

Example of creation of group with raid and disks handling

```
curl -X POST -d "instance_type=r3.xlarge" -d "name=infra" -d "role=infra" -d "attributes={\"type\":\"infra\"}" -d "vars={\"raids\":{\"0\":{\"mountpoint\":\"/data\",\"fstype\":\"xfs\",\"level\":\"0\",\"devices\":[\"/dev/xvdx\",\"/dev/xvdy\"]}},\"disks\":{\"xvdz\":{\"mountpoint\":\"/commitlog\",\"fstype\":\"xfs\"}}}" -d "cpus=10" -d "ram=64" -d "disk_size=50" -d "customhwconf={\"ebs_block_device\":[{\"device_name\":\"/dev/sdx\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdy\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"},{\"device_name\":\"/dev/sdz\",\"volume_size\":\"200\",\"volume_type\":\"gp2\"}]}" http://localhost:5555/api/v2.0/grids/${grid_name}/groups
```
