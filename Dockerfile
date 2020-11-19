FROM python:3.8
RUN pip install pipenv
RUN mkdir /python
### CACHE PIP DEPENDENCIES
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
###
WORKDIR /python
COPY . .
CMD ["python", "/python/openstack_exporter.py"]