# Using LTS ubuntu
FROM ubuntu:14.04
MAINTAINER "Mark Vartanyan <kolypto@gmail.com>"

# Packages: update & install
ENV DEBCONF_FRONTEND noninteractive
RUN apt-get update -qq
RUN apt-get install -qq -y --no-install-recommends python-pip python-dev build-essential
RUN apt-get install -qq -y --no-install-recommends libmysqlclient-dev libpcre3 libpcre3-dev
RUN pip install uwsgi


# Install OverC server
RUN pip install overc[server]

# Configure uwsgi
RUN mkdir /etc/uwsgi
ADD conf/uwsgi-overc.yml /etc/uwsgi/overc.yml

# Configure OverC
ADD conf/overc /etc/overc
RUN mkdir /var/run/overc && chown www-data:www-data /var/run/overc


# Runner
ADD run.sh /root/run.sh



# Declare
VOLUME ["/etc/overc"]
EXPOSE 5000

CMD ["/root/run.sh"]
