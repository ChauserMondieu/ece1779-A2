from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import EC2
import ELB
import S3
import CPU_MONITOR


# Initialize the program
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://ece1779:ece1779pass@instance1.c9klgmg6bydj.us-east-1.rds.amazonaws.com/faced?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Happy Wind Man'
db = SQLAlchemy(app)


# Define a mysql table for instances
class Manager(db.Model):
    __tablename__ = 'manager'
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(100), unique=False)
    availability_zone = db.Column(db.String(100), unique=False)
    status = db.Column(db.String(100), unique=False)
    DNS_address = db.Column(db.String(100), unique=False)


# Initialize the database from aws
def sql_start():
    db.drop_all()
    db.create_all()
    instances = EC2.obtain_instance()['InstanceStatuses']
    for i in range(len(instances)):
        instance_id = instances[i]['InstanceId']
        instance_availability_zone = instances[i]['AvailabilityZone']
        instance_state = instances[i]['InstanceState']['Name']
        instance_type, instance_dns_name = EC2.describe_instance(instance_id)
        manager = Manager(instance_id=instance_id, availability_zone=instance_availability_zone,
                          DNS_address=instance_dns_name, status=instance_state, type=instance_type)
        db.session.add(manager)
        db.session.commit()


@app.route('/')
def manager_main():
    return render_template("MAIN.html")


@app.route('/manager/ec2', methods=['GET', 'POST'])
def ec2():
    filenames = Manager.query.all()
    return render_template("EC2.html", filenames=filenames)


@app.route('/manager/s3', methods=['GET', 'POST'])
def s3():
    return render_template("S3.html")


@app.route('/manager/auto_scaling', methods=['GET', 'POST'])
def auto_scaling(e_ratio=1, s_ratio=1, e_threshold=80, s_threshold=20):
    return render_template("auto_scaling.html", e_ratio=e_ratio, s_ratio=s_ratio, e_threshold=e_threshold,
                           s_threshold=s_threshold)


@app.route('/manager/ec2/cpu_graph/<instance_id>')
def cpu_graph(instance_id):
    CPU_MONITOR.plot_graph()
    graph_address = "/static/CPU-Utilization/instance-" + instance_id + ".png"
    return render_template("CPU_GRAPH.html", graph_address=graph_address)


@app.route('/manager/ec2/delete_instance/<instance_id>')
def delete_instance(instance_id):
    EC2.delete_instance([instance_id])
    sql_start()
    return redirect(url_for('ec2'))


@app.route('/manager/ec2/create_instance')
def create_instance():
    # state = \
    EC2.create_instance()
    # ELB.elb_to_instance(state['Instances'][0]['InstanceId'])
    sql_start()
    flash('successfully!')
    return render_template("MAIN.html")


@app.route('/manager/s3/delete')
def delete_s3():
    S3.s3_delete()
    db.drop_all()
    db.create_all()
    flash('successfully!')
    return redirect(url_for('manager_main'))


@app.route('/manager/auto_scaling/process/er_<e_ratio>/sr_<s_ratio>/et_<e_threshold>/st_<s_threshold>')
def auto_scaling_process(e_ratio=1, s_ratio=1, e_threshold=80, s_threshold=20):
    expand_ratio = int(e_ratio)
    shrink_ratio = int(s_ratio)
    average = CPU_MONITOR.obtain_average()
    if average > float(e_threshold):
        EC2.create_instance(expand_ratio)
    elif average < float(s_threshold):
        instances = EC2.obtain_instance()['InstanceStatuses']
        instances_number = len(instances)
        shrink_number = instances_number - int(instances_number / shrink_ratio)
        for i in range(shrink_number):
            drop_target = Manager.query.filter_by(id=(instances_number - i)).first()
            EC2.delete_instance(drop_target.instance_id)
    flash('successfully!')
    return redirect(url_for('auto_scaling', e_ratio=e_ratio, s_ratio=s_ratio, e_threshold=e_threshold,
                            s_threshold=s_threshold))


if __name__ == '__main__':
    sql_start()
    app.run(host = '0.0.0.0', debug = 'True')

