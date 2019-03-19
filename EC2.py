import boto3


def create_instance(expand_ratio=1):
    client = boto3.client('ec2')
    states = client.run_instances(
        LaunchTemplate={'LaunchTemplateId': 'lt-04c9e24d688e4416f',
                        'Version': '1'}, MinCount=1, MaxCount=expand_ratio)
    return states


def delete_instance(instance_id):
    client = boto3.client('ec2')
    client.terminate_instances(InstanceIds=instance_id)


def obtain_instance():
    client = boto3.client('ec2')
    states = client.describe_instance_status()
    return states


def describe_instance(instance_id):
    client = boto3.client('ec2')
    instance_type = client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['InstanceType']
    instance_dns_name = client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['PublicDnsName']
    return instance_type, instance_dns_name






