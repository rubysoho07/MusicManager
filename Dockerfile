FROM ubuntu:18.04
LABEL maintainer="hahafree12@gmail.com"

# Upgrade packages
RUN apt-get -qq update
RUN apt-get -qq -y upgrade

# Install Python 3.6 & pip
RUN apt-get install -qq -y python3 python3-pip

WORKDIR /app
ADD . /app/
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/
RUN chmod +x wait-for-it.sh

RUN pip3 install -r requirements.txt