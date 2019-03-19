import boto3


def s3_delete():
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('assignment2instance1')
    my_bucket.objects.filter(Prefix='face_detected_picture').delete()
    my_bucket.objects.filter(Prefix='raw_picture').delete()
    my_bucket.objects.filter(Prefix='CPU-Utilization').delete()
    my_bucket.objects.filter(Prefix='HTTP-Request').delete()
