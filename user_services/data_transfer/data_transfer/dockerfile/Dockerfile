FROM python:3.9-slim-buster
RUN apt-get update && \
    apt-get -y install sudo nano vim git && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN git clone --branch data-export-import-docker https://github.com/fabric-testbed/MeasurementFramework.git
RUN curl https://rclone.org/install.sh | sudo bash
RUN mkdir /root/services
RUN mkdir /root/services/data_transfer
RUN mkdir /root/services/data_transfer/config_file
RUN mv /MeasurementFramework/user_services/data_transfer/data_transfer/config_file/data_transfer.conf /root/services/data_transfer/config_file/data_transfer.conf
RUN mkdir /root/services/data_transfer/service_files
RUN mkdir /root/services/data_transfer/prometheus
RUN mkdir /root/services/data_transfer/elk
RUN mkdir /root/services/data_transfer/prometheus_data/download
RUN mkdir /root/services/data_transfer/elk_data/download
RUN mv /MeasurementFramework/user_services/data_transfer/data_transfer/service_files/* /root/services/data_transfer/service_files
WORKDIR /root/services/data_transfer/service_files
ENTRYPOINT [ "python3" ]