import boto3
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plts
from pylab import *
from numpy.ma import arange
import os
import EC2


# derive source metrics from AWS server
def get_cpu_util(instanceID, startTime, endTime):
    client = boto3.client('cloudwatch')
    response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceID
            },
        ],

        StartTime=startTime,
        EndTime=endTime,
        Period=300,
        Statistics=[
            'Average',
        ],
        Unit='Percent'
    )
    return response


# extract data from cloud watch metrics
def data_extraction(data_input):
    time_metrics = []
    data_metrics = []
    file_summary = data_input
    for i in range(len(file_summary['Datapoints'])):
        data_metrics.append(file_summary['Datapoints'][i]['Average'])
        time_metrics.append(file_summary['Datapoints'][i]['Timestamp'])
    for j in range(len(time_metrics)):
        now = time_metrics[j]
        now.strftime('%m/%d/%Y')
        time_metrics[j] = now
    return time_metrics, data_metrics


# draw cup utilization graphs
def draw_graph(x, y, graphs_path, instance_id):
    for i in range(len(x)):
        x[i] = x[i].strftime('%m/%d/%Y\n%H:%M:%S')
    # Create a new graph
    plts.title(instance_id + '  CPU Utilization  ')
    plts.xlabel('Timestamp')
    plts.ylabel('Percentage')
    plts.ylim(0, 100)
    plts.yticks(range(0, 100, 10), fontsize=8)
    plts.xticks(range(0, 1000, 20), rotation=70, fontsize=4)
    plts.subplots_adjust(bottom=0.2)
    # Store x-label and y-label separately
    plts.xticks(arange(len(x)), x)
    y_list = y

    # Draw new graph and save
    plts.plot(y_list, color='r', linewidth=1, alpha=0.6)
    plts.savefig(graphs_path, dpi=600)
    plts.cla()


# Define photo_Upload Function
def upload_to_s3(bucket_name, file_path, file_name):
    session = boto3.session.Session()
    s3 = session.resource('s3')
    # Upload a new file
    data = open(file_path, 'rb')
    s3.Bucket(bucket_name).put_object(Key=file_name, Body=data)


def plot_graph():
    base_path = os.path.dirname(__file__)
    bucket_name = 'assignment2instance1'
    instances = EC2.obtain_instance()['InstanceStatuses']
    for i in range((len(instances))):
        instanceID = instances[i]['InstanceId']
        # Set other parameters
        startTime = datetime.datetime.utcnow() - timedelta(seconds=3600)
        endTime = datetime.datetime.utcnow()
        graph_path = os.path.join(base_path, 'static/CPU-Utilization',  'instance-'
                                  + str(i+1) + '.png')
        graph_name = os.path.join('CPU-Utilization', 'instance-' + str(i+1) + '.png')
        # Run the graphic functions
        inter_sec1 = get_cpu_util(instanceID, startTime, endTime)
        inter_sec21 = data_extraction(inter_sec1)[0]
        inter_sec22 = data_extraction(inter_sec1)[1]
        draw_graph(inter_sec21, inter_sec22, graph_path, instanceID)
        # Upload graph into S3 bucket
        upload_to_s3(bucket_name, graph_path, graph_name)


def obtain_average():
    data_sum = 0
    instances = EC2.obtain_instance()['InstanceStatuses']
    for i in range(len(instances)):
        instanceID = instances[i]['InstanceId']
        # Set other parameters
        startTime = datetime.datetime.utcnow() - timedelta(seconds=120)
        endTime = datetime.datetime.utcnow()
        inter_sec1 = get_cpu_util(instanceID, startTime, endTime)
        time_datapoint = data_extraction(inter_sec1)[1]
        # Calculate the sum of all running instances
        if len(time_datapoint) == 0:
            data_sum = data_sum
        else:
            data_sum = data_sum + time_datapoint[0]
    data_ave = data_sum/len(instances)
    return data_ave



