import os
import time
import openstack
import datetime
import traceback
import prometheus_client as prom

api_metrics = prom.Gauge('openstack_api_response_seconds', 'Time for openstack api to execute.', ['api_name','cloud_name'])
api_status = prom.Gauge('openstack_api_status', 'API current status. 1 = up 0 = down.',['api_name','cloud_name'])

def generate_nova_metrics(connection,cloud_name):
    try:
        start_time = datetime.datetime.now()
        for server in connection.compute.servers():
            name = server
        end_time = datetime.datetime.now()
        time_took = end_time - start_time
        seconds_took = time_took.seconds
        print(f'Nova took {seconds_took} seconds')
        api_metrics.labels('nova',cloud_name).set(seconds_took)
        api_status.labels('nova',cloud_name).set(1)
    except:
        print(traceback.print_exc())
        print("Nova api is down.")
        api_status.labels('nova',cloud_name).set(0)

def generate_neutron_metrics(connection,cloud_name):
    try:
        project = connection.current_project
        start_time = datetime.datetime.now()
        for network in connection.network.networks(project_id=project.id):
            name = network
        end_time = datetime.datetime.now()
        time_took = end_time - start_time
        seconds_took = time_took.seconds
        print(f'Neutron took {seconds_took} seconds')
        api_metrics.labels('neutron',cloud_name).set(seconds_took)
        api_status.labels('neutron',cloud_name).set(1)
    except:
        print(traceback.print_exc())
        print("Neutron api is down.")
        api_status.labels('neutron',cloud_name).set(0)

def generate_cinder_metrics(connection,cloud_name):
    try:
        start_time = datetime.datetime.now()
        for volume in  connection.volume.volumes():
            name = volume
        end_time = datetime.datetime.now()
        time_took = end_time - start_time
        seconds_took = time_took.seconds
        print(f'Cinder took {seconds_took} seconds')
        api_metrics.labels('cinder',cloud_name).set(seconds_took)
        api_status.labels('cinder',cloud_name).set(1)
    except:
        print(traceback.print_exc())
        print("Cinder api is down.")
        api_status.labels('cinder').set(0)