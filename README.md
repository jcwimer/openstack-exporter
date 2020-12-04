# openstack_exporter
This is a prometheus exporter for Openstack

# Usage
### With Docker
This script will forward all "OS_" variables to the container and start the container on port 8000
```
bash run-with-docker.sh --cloud_name openstack
```
The docker image includes Chromium for getting Horizon metrics.

### With Python
Need Python 3.8 and pipenv
```
pipenv sync
pipenv run python openstack_exporter.py --cloud_name openstack
```

### Optional Params
To deploy an instance and test the time to ping on all hypervisors, use the following flags: 
```
--image IMAGE_NAME_OR_ID --flavor FLAVOR_NAME_OR_ID --network NETWORK_NAME_OR_ID --instance_deploy
```
The network used needs to have TCP port 22 (uses TCP instead of ICMP to ping) open in the default security group.

To capture horizon login response time, use the following flag:
```
--horizon_url "http://url_here"
```
This will use selenium to log into horizon. You will need Chrome or Chromium installed to use this feature. You will see these metrics: 
```
openstack_api_response_seconds{api_name="horizon",cloud_name="CLOUD_NAME"}
openstack_api_status{api_name="horizon",cloud_name="CLOUD_NAME"}
```

# Information
### Standard Metrics Provided
| Metric | Metric Labels | Description|
| :--- | :--- | :--- |
| `openstack_api_response_seconds` | `{api_name="API_NAME",cloud_name="CLOUD_NAME"}` | Seconds for the api to respond via openstack sdk. nova, neutron, and cinder are currently recorded. |
| `openstack_api_status` | `{api_name="API_NAME",cloud_name="CLOUD_NAME"}` | Status of the openstack api. 1 = up 0 = down. nova, neutron, and cinder are currently recorded. |
| `openstack_hypervisor_running_vms` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | Number of running VMs on every hypervisor in the region. |
| `openstack_hypervisor_used_ram_mb` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | Amount of RAM in MB used (as reported by nova-compute) for every hypervisor in the region. |
| `openstack_hypervisor_total_ram_mb` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | Amount of RAM in MB in total (as reported by nova-compute) for every hypervisor in the region. |
| `openstack_hypervisor_used_cpus` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | Number of vcpus used (as reported by nova-compute) for every hypervisor in the region. |
| `openstack_hypervisor_total_cpus` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | Number of vcpus in total (as reported by nova-compute) for every hypervisor in the region. |
| `openstack_hypervisor_enabled` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | nova-compute status for every hypervisor in the region. 1 = enabled 0 = disabled|
| `openstack_hypervisor_up` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | nova-compute state for every hypervisor in the region. 1 = up 0 = down |
| `openstack_hypervisor_local_gb_total` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}`| Total local disk in GB (as reported by nova-compute) for every hypervisor in the region. |
| `openstack_hypervisor_local_gb_used` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME",aggregate="AGGREGATE_NAME"}` | Total local disk used in GB (as reported by nova-compute) for every hypervisor in the region. |

### Optional Metrics (use flags when running)
| Metric | Metrics Labels | Description |
| :--- | :--- | :--- |
|`openstack_instance_deploy_seconds_to_ping` | `{hypervisor_hostname="HYPERVISOR_NAME",cloud_name="CLOUD_NAME"}` | Seconds from deploy command to ping when creating an instance for every hypervisor in the region. Requires --flavor, --image, --network, and --instance_deploy flags. The network used needs to have TCP port 22 (uses TCP instead of ICMP to ping) open in the default security group. |
|`openstack_horizon_response_seconds` | `{cloud_name="CLOUD_NAME"}` | Seconds it takes for Chromium to log into Horizon. Requires --horizon_url flag. |
|`openstack_horizon_status` | `{cloud_name="CLOUD_NAME"}` | Horizon status. 1 = up 0 = down. Requires --horizon_url flag. |