#!/bin/bash

# install mysql
sudo apt update
sudo apt-get install mysql-server

# install sakila
sudo wget http://downloads.mysql.com/docs/sakila-db.tar.gz
sudo tar xvf sakila-db.tar.gz -C /tmp/

# install sysbench
sudo apt-get install sysbench
