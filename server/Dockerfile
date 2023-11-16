# Use the base Docker image with the desired operating system and dependencies
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# Install basic packages
RUN apt-get update
RUN apt update
RUN apt-get install wget git curl make pip vim sudo tmux lsb-release -y --fix-missing

# Set the working directory inside the container
WORKDIR /home/dbeda

# Copy your framework code and data into the container
COPY . /home/dbeda


# Add apt-get repo for: nodejs, yarn, and postgresql
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install postgresql-14 
EXPOSE 5437
RUN service postgresql restart
# Set the PostgreSQL user 'postgres' password to 'postgres'

USER postgres

RUN /etc/init.d/postgresql start && \
psql -c "alter user postgres with encrypted password 'postgres'" && \
psql -c "CREATE DATABASE dbeda;" && \
psql -d dbeda -c "CREATE TABLE db_config (id VARCHAR(50) PRIMARY KEY, db_type VARCHAR(50) NOT NULL, db_host VARCHAR(50) NOT NULL, db_port VARCHAR(50) NOT NULL, db_name VARCHAR(50) NOT NULL, db_user VARCHAR(50) NOT NULL, db_password VARCHAR(50) NOT NULL);"


RUN sed -i 's/port = 5432/port = 5437/g' /etc/postgresql/14/main/postgresql.conf
RUN echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/14/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/14/main/postgresql.conf

USER root

# Specify the command to run when the container starts
CMD ["/bin/bash"]

#!/bin/bash
