import boto3


def elb_to_instance(instance_id):
    client = boto3.client('elbv2')
    client.register_targets(TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:531099828430:targetgroup/workpool-instance1/4d79100047c6a538',
                            Targets=[{'Id': instance_id}])


elb_to_instance('i-0b130594b2bc6eaa1')
