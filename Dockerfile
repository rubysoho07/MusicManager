FROM ubuntu:18.04
LABEL maintainer="hahafree12@gmail.com"

# Upgrade packages
RUN apt-get -qq update
RUN apt-get -qq -y upgrade

# Install Python 3.6 & pip
RUN apt-get install -qq -y python3 python3-pip

WORKDIR /app

# install requisites
ADD ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

# Copy source files
ADD ./manager_core /app/manager_core
ADD ./mm_user /app/mm_user
ADD ./MusicManager /app/MusicManager
ADD ./templates /app/templates
ADD ./manage.py /app/manage.py

# To wait for database container
ADD ./docker_entrypoint.sh /app/docker_entrypoint.sh
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/
RUN chmod +x wait-for-it.sh