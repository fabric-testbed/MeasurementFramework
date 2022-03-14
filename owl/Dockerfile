# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster
EXPOSE 5005

RUN apt-get update && apt-get install -y \
	tcpdump \
	&& rm -rf /var/lib/apt/lists/*


RUN mkdir -p /owl_app/data
RUN mkdir -p /owl_app/config

WORKDIR /owl_app
#COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt


COPY ./NodeSockManager.py .
COPY ./sock_ops/.  ./sock_ops/ 
RUN ls -l 

ENTRYPOINT [ "python3", "NodeSockManager.py" ] 
