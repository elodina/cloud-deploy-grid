import requests

ec2instances_url = 'http://www.ec2instances.info/instances.json'
ec2instances = {}


def ec2instances_load():
    instances_json = requests.get(ec2instances_url).json()
    for instance in instances_json:
        ec2instances[instance['instance_type']] = {
            'cpu': instance['vCPU'],
            'ram': instance['memory']}
