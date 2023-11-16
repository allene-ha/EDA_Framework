# Use a base Docker image with the desired operating system and dependencies
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# Install basic packages
RUN apt-get update
RUN apt update
RUN apt-get install wget git curl make pip vim sudo tmux libpq-dev sysbench lsb-release -y --fix-missing

# Set the working directory inside the container
WORKDIR /home/dbeda

# Copy your framework code and data into the container
COPY . /home/dbeda


# Add apt-get repo for: nodejs, yarn, and postgresql
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install postgresql-14 
EXPOSE 5438
RUN service postgresql restart
# Set the PostgreSQL user 'postgres' password to 'postgres'

USER postgres

RUN /etc/init.d/postgresql start && \
psql -c "alter user postgres with encrypted password 'postgres'" && \
psql -c 'CREATE EXTENSION IF NOT EXISTS pg_stat_statements;' && \
psql -c 'CREATE DATABASE test_cli;' 

# Add the necessary configuration to allow data collection
RUN echo "listen_addresses='*'"  >> /etc/postgresql/14/main/postgresql.conf
RUN echo "shared_preload_libraries = 'pg_stat_statements'" >> /etc/postgresql/14/main/postgresql.conf
RUN echo "pg_stat_statements.track = all" >> /etc/postgresql/14/main/postgresql.conf

# Register the allowed IP address in pg_hba.conf
RUN echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/14/main/pg_hba.conf
RUN sed -i 's/port = 5432/port = 5438/g' /etc/postgresql/14/main/postgresql.conf
RUN export PATH=$PATH:~/.local/bin

USER root
# Specify the command to run when the container starts
CMD ["/bin/bash"]
