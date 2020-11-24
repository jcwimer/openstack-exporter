FROM python:3.8
RUN pip install pipenv
RUN mkdir /python

### CACHE PIP DEPENDENCIES
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
###

### install Chromium
RUN apt-get update
# stretch uses chromium package not chromium-browser
RUN apt-get install chromium=83.0* -y

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# install xvfb
RUN apt-get install -yqq xvfb

RUN apt-get -qq clean \
  && apt-get autoremove -y \
  && rm -rf \
    /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/*

# set display port and dbus env to avoid hanging
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

COPY docker-entrypoint.sh /root/docker-entrypoint.sh

RUN mkdir /app
WORKDIR /app

RUN chmod a+x /root/docker-entrypoint.sh
###

WORKDIR /python
COPY . .

# Python output in stdout
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENTRYPOINT ["bash", "/root/docker-entrypoint.sh","python", "/python/openstack_exporter.py"]