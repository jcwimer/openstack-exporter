# openstack_exporter
This is a prometheus exporter for Openstack

# Usage
### With Docker
This script will forward all "OS_" variables to the container and start the container on port 8000
```
bash run-with-docker.sh
```

### With Python
Need Python 3.8 and pipenv
```
pipenv sync
pipenv run python openstack_exporter.py
```