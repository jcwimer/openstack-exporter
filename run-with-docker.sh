#!/bin/bash
OPENSTACK_VARS=""
for var in $(env | grep OS_); do
  OPENSTACK_VARS+="-e $var ";
done
docker run -d -p 8000:8000 $OPENSTACK_VARS jcwimer/openstack_exporter