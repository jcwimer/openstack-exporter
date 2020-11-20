import prometheus_client as prom
import os
import time
import traceback
import openstack
import datetime

def openstack_connection():
    conn = openstack.connect(cloud='envvars')
    return conn

def generate_hypervisor_metrics(connection, hypervisor_running_vms, hypervisor_used_ram_mb, hypervisor_total_ram_mb, hypervisor_free_cpus, hypervisor_total_cpus, hypervisor_enabled, hypervisor_up):
    for hypervisor in connection.list_hypervisors():
        print(f'Getting hypervisor {hypervisor.name} metrics.')
        hypervisor_running_vms.labels(hypervisor.name).set(hypervisor.running_vms)
        hypervisor_used_ram_mb.labels(hypervisor.name).set(hypervisor.memory_used)
        hypervisor_total_ram_mb.labels(hypervisor.name).set(hypervisor.memory_size)
        hypervisor_free_cpus.labels(hypervisor.name).set(hypervisor.vcpus_used)
        hypervisor_total_cpus.labels(hypervisor.name).set(hypervisor.vcpus)
        if hypervisor.status == "enabled":
            hypervisor_enabled.labels(hypervisor.name).set(1)
        else:
            hypervisor_enabled.labels(hypervisor.name).set(0)
        if hypervisor.state == "up":
            hypervisor_up.labels(hypervisor.name).set(1)
        else:
            hypervisor_up.labels(hypervisor.name).set(0)

def generate_nova_metrics(connection,api_gauge):
    start_time = datetime.datetime.now()
    for server in connection.compute.servers():
        name = server
    end_time = datetime.datetime.now()
    time_took = end_time - start_time
    seconds_took = time_took.seconds
    print(f'Nova took {seconds_took} seconds')
    api_gauge.labels('nova').set(seconds_took)

def generate_neutron_metrics(connection,api_gauge):
    project = connection.current_project
    start_time = datetime.datetime.now()
    for network in connection.network.networks(project_id=project.id):
        name = network
    end_time = datetime.datetime.now()
    time_took = end_time - start_time
    seconds_took = time_took.seconds
    print(f'Neutron took {seconds_took} seconds')
    api_gauge.labels('neutron').set(seconds_took)

def generate_cinder_metrics(connection,api_gauge):
    start_time = datetime.datetime.now()
    for volume in  connection.volume.volumes():
        name = volume
    end_time = datetime.datetime.now()
    time_took = end_time - start_time
    seconds_took = time_took.seconds
    print(f'Cinder took {seconds_took} seconds')
    api_gauge.labels('cinder').set(seconds_took)

if __name__ == '__main__':
    print("Starting server on port 8000")
    api_metrics = prom.Gauge('openstack_api_response_seconds', 'Time for openstack api to execute.', ['api_name'])
    hypervisor_running_vms = prom.Gauge('openstack_hypervisor_running_vms', 'Number of VMs running on this hypervisor.',['hypervisor_hostname'])
    hypervisor_used_ram_mb = prom.Gauge('openstack_hypervisor_used_ram_mb', 'Total MB of used RAM on the hypervisor.',['hypervisor_hostname'])
    hypervisor_total_ram_mb = prom.Gauge('openstack_hypervisor_total_ram_mb', 'Total MB of RAM on the hypervisor.',['hypervisor_hostname'])
    hypervisor_used_cpus = prom.Gauge('openstack_hypervisor_used_cpus', 'Total VCPUs used on the hypervisor.',['hypervisor_hostname'])
    hypervisor_total_cpus = prom.Gauge('openstack_hypervisor_total_cpus', 'Total VCPUs on the hypervisor.',['hypervisor_hostname'])
    hypervisor_enabled = prom.Gauge('openstack_hypervisor_enabled', 'nova-compute service status on hypervisor. 1 is enabled 0 is disabled.',['hypervisor_hostname'])
    hypervisor_up = prom.Gauge('openstack_hypervisor_up', 'nova-compute service state on hypervisor. 1 is up 0 is down.',['hypervisor_hostname'])

    prom.start_http_server(8000)
    while True:
        try:
            print("Gathering metrics...")
            connection = openstack_connection()
            generate_nova_metrics(connection,api_metrics)
            generate_neutron_metrics(connection,api_metrics)
            generate_cinder_metrics(connection,api_metrics)
            generate_hypervisor_metrics(connection, hypervisor_running_vms, hypervisor_used_ram_mb, hypervisor_total_ram_mb, hypervisor_used_cpus, hypervisor_total_cpus, hypervisor_enabled, hypervisor_up)
            connection.close()
            print("Waiting 30 seconds to gather more metrics.")
            time.sleep(30)
        except Exception:
            print(traceback.print_exc())