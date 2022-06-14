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

### May be needed later
#COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt


# For debugging
RUN pwd
RUN ls -lh *

ENTRYPOINT [ "python3" ]  
