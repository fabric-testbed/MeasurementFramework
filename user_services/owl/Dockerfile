# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster
EXPOSE 5005

RUN apt-get update && apt-get install -y \
	tcpdump \
        git \
	&& rm -rf /var/lib/apt/lists/*

RUN git clone --branch owl  https://github.com/fabric-testbed/MeasurementFramework.git
RUN mkdir /owl_data
RUN mkdir /owl_config
RUN ls -l /

WORKDIR /MeasurementFramework/user_services/owl
#COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt

# For debugging
RUN pwd
RUN ls -lh *
#RUN cat NodeSockManager.py
#RUN cat sock_ops/udp_capturer.py

# This should probably be changed to simply python3
ENTRYPOINT [ "python3", "NodeSockManager.py" ] 
