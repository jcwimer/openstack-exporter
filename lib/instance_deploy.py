from tcpping2 import Ping
import os
import time
import openstack
import datetime
import traceback
import prometheus_client as prom

instance_deploy_metrics = prom.Gauge('openstack_instance_deploy_seconds_to_ping', 'Time to deploy an instance and ping it.', ['hypervisor_hostname','cloud_name'])

def run_pings(ip_address):
    try:
        ping = Ping(ip_address, 22)
        # Ping 1 time
        run_ping = ping.ping(1)
        ping_success_rate = run_ping['success_rate']
        print(f'Ping success rate: {ping_success_rate}%')
        return ping_success_rate
    # If ping fails
    except socket.gaierror:
        time.sleep(5)

def wait_for_ping(ip_address):
    print('Waiting for instance to respond to ping. This will time out in 10 minutes.')
    timeout = time.time() + 60 * 10  # 10 minutes from now
    ping_success_rate = 0
    while ping_success_rate != 100.0:
        ping_success_rate = run_pings(ip_address)
        time.sleep(5)
        if time.time() > timeout:
            print("Timed out waiting for ping to the instance.")
            return False
    return True

def get_image(connection, image):
    try:
        image_found = connection.image.find_image(image, ignore_missing=True)
        return image_found
    except:
        print(f"Had issues finding image {image}.")
        print(traceback.print_exc())
        return None

def get_flavor(connection, flavor):
    try:
        flavor_found = connection.compute.find_flavor(flavor, ignore_missing=True)
        return flavor_found
    except:
        print(f"Had issues finding flavor {flavor}.")
        print(traceback.print_exc())
        return None

def get_network(connection, network):
    try:
        network_found = connection.network.find_network(network)
        return network_found
    except:
        print(f"Had issues finding network {network}.")
        print(traceback.print_exc())
        return None

def cleanup(connection, instance_name):
    print(f"Cleaning up {instance_name} instance.")
    server = connection.compute.find_server(instance_name)

    if server:
        try:
            connection.compute.delete_server(server.id)
        except:
            print(f"Failed to delete server: {instance_name}")
            print(traceback.print_exc())


def create_instance(connection, flavor, image, network, hypervisor):
    instance_name = f"{hypervisor}-metric"
    availability_zone = str(f"nova:{hypervisor}")
    print(f"Creating an instance called: {instance_name}")
    try:
        server = connection.compute.create_server(
            networks=[{"uuid": network.id}],
            image_id=image.id,
            flavor_id=flavor.id,
            name=f"{instance_name}",
            availability_zone=availability_zone,
        )
        server = connection.compute.wait_for_server(server, status="ACTIVE", wait=600)
        ip_address = server.addresses[network.name][0]['addr']
        if wait_for_ping(ip_address) is True:
            return True
        else:
            return False
    except:
        print(f"Failed to create instance {instance_name}.")
        print(traceback.print_exc())
        cleanup(connection, f"{instance_name}")

def get_metrics(connection, flavor, image, network, cloud_name):
    instance_image = get_image(connection, image)
    instance_flavor = get_flavor(connection, flavor)
    instance_network = get_network(connection, network)

    for hypervisor in connection.list_hypervisors():
        availability_zone = str(f"nova:{hypervisor.name}")
        start_time = datetime.datetime.now()
        if create_instance(connection, instance_flavor, instance_image, instance_network, hypervisor.name) is True:
            end_time = datetime.datetime.now()
            time_took = end_time - start_time
            seconds_took = time_took.seconds
            print(f'Instance creation on {hypervisor.name} took {seconds_took} seconds.')
            instance_deploy_metrics.labels(f'{hypervisor.name}',cloud_name).set(seconds_took)
        cleanup(connection, f"{hypervisor.name}-metric")