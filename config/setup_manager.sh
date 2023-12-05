#!/bin/bash

# install mysql cluster
sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home/
sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

# add env variables to the mysqlc.sh file
MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc
sudo bash -c 'cat >> /etc/profile.d/mysqlc.sh << EOF
export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc
export PATH=/opt/mysqlcluster/home/mysqlc/bin:$PATH
EOF'

# update the env variables
sudo chmod 777 /etc/profile.d/mysqlc.sh
#source /etc/profile.d/mysqlc.sh

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

# get private dns of instances
# open config file
sed -i -e 's/\r$//' instances_private.txt
filename="instances_private.txt"

# Check if the file exists and read it line by line
cd ~
if [ -e "$filename" ]; then
    line_counter=0
    while read -r line; do
        ((line_counter++))
        if [ "$line_counter" -eq 1 ]; then
            INSTANCE1="$line"
        elif [ "$line_counter" -eq 2 ]; then
            INSTANCE2="$line"
        elif [ "$line_counter" -eq 3 ]; then
            INSTANCE3="$line"
        elif [ "$line_counter" -eq 4 ]; then
            INSTANCE4="$line"
        elif [ "$line_counter" -eq 5 ]; then
            INSTANCE5="$line"
        fi
    done < "$filename"
fi

# create config.ini file
cd /opt/mysqlcluster/deploy/conf
sudo bash -c "cat >> config.ini << EOF
[ndb_mgmd]
hostname=$INSTANCE2
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=$INSTANCE3
nodeid=3

[ndbd]
hostname=$INSTANCE4
nodeid=4

[ndbd]
hostname=$INSTANCE5
nodeid=5

[mysqld]
nodeid=50
EOF"

# execute mysql cluster script
cd /opt/mysqlcluster/home/mysqlc
sudo chmod 777 /opt/mysqlcluster/deploy/ndb_data
sudo scripts/mysql_install_db --datadir=/opt/mysqlcluster/deploy/mysqld_data

# install sakila
sudo wget http://downloads.mysql.com/docs/sakila-db.tar.gz
sudo tar xvf sakila-db.tar.gz -C /tmp/

# install sysbench
sudo apt-get install sysbench

# install required python module
sudo apt install python3-pip
pip3 install mysql-connector-python