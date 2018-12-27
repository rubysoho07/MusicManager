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

ENV SECRET_KEY testsecretkey
ENV AWS_STORAGE_BUCKET_NAME static_bucket
ENV AWS_ACCESS_KEY_ID accesskeyid
ENV AWS_SECRET_ACCESS_KEY secretaccesskey
ENV AWS_S3_REGION_NAME aws_region
ENV EMAIL_HOST smtp_server
ENV EMAIL_PORT 465
ENV EMAIL_HOST_USER smtp_user
ENV EMAIL_HOST_PASSWORD smtp_password
ENV DEFAULT_FROM_EMAIL "MusicManager <gonigoni@gonigoni.kr>"