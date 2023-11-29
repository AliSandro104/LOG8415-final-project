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

# configurate the manager instance
sudo mkdir -p /opt/mysqlcluster/deploy
sudo mkdir -p /usr/local/mysql/mysql-cluster
cd /opt/mysqlcluster/deploy
sudo mkdir conf
sudo mkdir mysqld_data
sudo mkdir ndb_data
sudo chmod -R 777 ndb_data
cd conf

# create my.cnf file
sudo bash -c 'cat >> my.cnf << EOF
[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306
EOF'

# create config.ini file
sudo bash -c 'cat >> config.ini << EOF
[ndb_mgmd]
hostname=
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=
nodeid=3
serverport=50501

[ndbd]
hostname=
nodeid=4
serverport=50502

[ndbd]
hostname=
nodeid=5
serverport=50503

[mysqld]
nodeid=50
EOF'

sudo scripts/mysql_install_db --datadir=/opt/mysqlcluster/deploy/mysqld_data