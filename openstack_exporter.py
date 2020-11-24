import prometheus_client as prom
import traceback
import openstack
import time
import argparse
import sys
from lib import api_metrics
from lib import hypervisor_metrics

def openstack_connection():
    conn = openstack.connect(cloud='envvars')
    return conn

if __name__ == '__main__':
    print("Starting server on port 8000")
    prom.start_http_server(8000)
    while True:
        try:
            print("Gathering metrics...")
            connection = openstack_connection()
            api_metrics.generate_nova_metrics(connection)
            api_metrics.generate_neutron_metrics(connection)
            api_metrics.generate_cinder_metrics(connection)
            hypervisor_metrics.generate_hypervisor_metrics(connection)
            connection.close()
            print("Waiting 30 seconds to gather more metrics.")
            time.sleep(30)
        except Exception:
            print(traceback.print_exc())
            print("Waiting 30 seconds to gather more metrics.")
            time.sleep(30)