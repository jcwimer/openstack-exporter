import os
import time
import openstack
import datetime
import prometheus_client as prom

hypervisor_running_vms = prom.Gauge('openstack_hypervisor_running_vms', 'Number of VMs running on this hypervisor.',['hypervisor_hostname'])
hypervisor_used_ram_mb = prom.Gauge('openstack_hypervisor_used_ram_mb', 'Total MB of used RAM on the hypervisor.',['hypervisor_hostname'])
hypervisor_total_ram_mb = prom.Gauge('openstack_hypervisor_total_ram_mb', 'Total MB of RAM on the hypervisor.',['hypervisor_hostname'])
hypervisor_used_cpus = prom.Gauge('openstack_hypervisor_used_cpus', 'Total VCPUs used on the hypervisor.',['hypervisor_hostname'])
hypervisor_total_cpus = prom.Gauge('openstack_hypervisor_total_cpus', 'Total VCPUs on the hypervisor.',['hypervisor_hostname'])
hypervisor_enabled = prom.Gauge('openstack_hypervisor_enabled', 'nova-compute service status on hypervisor. 1 is enabled 0 is disabled.',['hypervisor_hostname'])
hypervisor_up = prom.Gauge('openstack_hypervisor_up', 'nova-compute service state on hypervisor. 1 is up 0 is down.',['hypervisor_hostname'])
hypervisor_local_gb_total = prom.Gauge('openstack_hypervisor_local_gb_total', 'Total local disk in GB.',['hypervisor_hostname'])
hypervisor_local_gb_used = prom.Gauge('openstack_hypervisor_local_gb_used', 'Used local disk in GB.',['hypervisor_hostname'])

def generate_hypervisor_metrics(connection):
    for hypervisor in connection.list_hypervisors():
        print(f'Getting hypervisor {hypervisor.name} metrics.')
        # See: https://opendev.org/openstack/openstacksdk/src/branch/master/openstack/compute/v2/hypervisor.py
        hypervisor_running_vms.labels(hypervisor.name).set(hypervisor.running_vms)
        hypervisor_used_ram_mb.labels(hypervisor.name).set(hypervisor.memory_used)
        hypervisor_total_ram_mb.labels(hypervisor.name).set(hypervisor.memory_size)
        hypervisor_used_cpus.labels(hypervisor.name).set(hypervisor.vcpus_used)
        hypervisor_total_cpus.labels(hypervisor.name).set(hypervisor.vcpus)
        hypervisor_local_gb_total.labels(hypervisor.name).set(hypervisor.local_disk_size)
        hypervisor_local_gb_used.labels(hypervisor.name).set(hypervisor.local_disk_used)

        if hypervisor.status == "enabled":
            hypervisor_enabled.labels(hypervisor.name).set(1)
        else:
            hypervisor_enabled.labels(hypervisor.name).set(0)
        if hypervisor.state == "up":
            hypervisor_up.labels(hypervisor.name).set(1)
        else:
            hypervisor_up.labels(hypervisor.name).set(0)