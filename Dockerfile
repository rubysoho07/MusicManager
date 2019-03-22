FROM python:3.6-slim
LABEL maintainer="hahafree12@gmail.com"

WORKDIR /app

# install requisites
ADD ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

# Copy source files
ADD . .

# To wait for database container
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /app/
RUN chmod +x wait-for-it.sh