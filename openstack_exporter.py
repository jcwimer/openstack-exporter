import prometheus_client as prom
import traceback
import openstack
import time
import argparse
import sys
import os
from lib import instance_deploy
from lib import api_metrics
from lib import hypervisor_metrics
from lib import horizon

def openstack_connection():
    if os.environ.get('OS_CLOUD_NAME') is not None:
        conn = openstack.connect(cloud=os.environ.get('OS_CLOUD_NAME'))
    else:
        conn = openstack.connect(cloud='envvars')
    return conn

# Set up argparse
def parse_cli_arguments():
    parser = argparse.ArgumentParser(
        description='Openstack Prometheus Exporter',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    required = parser.add_argument_group(title='required arguments')
    required.add_argument(
        '--cloud_name',
        required=True,
        help='Give the cloud a name.',
    )

    # This gets the optional arguments to print below the required ones.
    optional = parser.add_argument_group(title='optional arguments')
    optional.add_argument(
        '--instance_deploy',
        action="store_true",
        dest='instancedeploy',
        default=False,
        help='Enables instance deploy metrics. Requires --flavor --network and --image.'
    )
    optional.add_argument(
        '--flavor',
        dest='flavor',
        type=str,
        help='Flavor name or ID to use for instance deploy metrics.'
    )
    optional.add_argument(
        '--network',
        dest='network',
        type=str,
        help='Pingable (via TCP) network to use for instance deploy metrics.'
    )
    optional.add_argument(
        '--image',
        dest='image',
        type=str,
        help='Image name or ID to use for instance deploy metrics.'
    )
    optional.add_argument(
        '--horizon_url',
        dest='horizon_url',
        type=str,
        help='Url for Horizon.'
    )

    args = parser.parse_args()

    # Validation
    if args.instancedeploy is True and (args.image is None or args.flavor is None or args.network is None):
        parser.error("argument --instance_deploy: requires --image, --flavor, and --network.")
    elif args.image and (args.instancedeploy is False or args.flavor is None or args.network is None):
        parser.error("argument --image: requires --instance_deploy, --flavor, and --network.")
    elif args.network and (args.instancedeploy is False or args.flavor is None or args.image is None):
        parser.error("argument --network: requires --instance_deploy, --flavor, and --image.")
    elif args.flavor and (args.instancedeploy is False or args.image is None or args.network is None):
        parser.error("argument --flavor: requires --instance_deploy, --image, and --network.")
    
    return args

if __name__ == '__main__':
    print("Starting server on port 8000")
    prom.start_http_server(8000)
    args = parse_cli_arguments()
    while True:
        try:
            print("Gathering metrics...")
            connection = openstack_connection()
            api_metrics.generate_nova_metrics(connection,args.cloud_name)
            api_metrics.generate_neutron_metrics(connection,args.cloud_name)
            api_metrics.generate_cinder_metrics(connection,args.cloud_name)
            hypervisor_metrics.generate_hypervisor_metrics(connection,args.cloud_name)
            if args.instancedeploy and args.flavor and args.image and args.network:
                instance_deploy.get_metrics(connection, args.flavor, args.image, args.network,args.cloud_name)
            if args.horizon_url is not None:
                horizon.get_metrics(args.horizon_url, args.cloud_name)
            connection.close()
            print("Waiting 30 seconds to gather more metrics.")
            time.sleep(30)
        except Exception:
            connection.close()
            print(traceback.print_exc())
            print("Waiting 30 seconds to gather more metrics.")
            time.sleep(30)
        finally:
            connection.close()