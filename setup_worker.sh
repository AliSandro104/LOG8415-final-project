#!/bin/bash

# install mysql cluster
sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home/
sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

# add env variables to the mysqlc.sh file
sudo bash -c 'cat >> /etc/profile.d/mysqlc.sh << EOF
export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc
export PATH=$MYSQLC_HOME/bin:$PATH
EOF'

# update the env variables
sudo chmod 777 /etc/profile.d/mysqlc.sh
source /etc/profile.d/mysqlc.sh

# initialize cluster with libncurses5
sudo apt-get update
sudo apt-get -y install libncurses5

# create the nbd_data folder
sudo mkdir -p /opt/mysqlcluster/deploy/ndb_data