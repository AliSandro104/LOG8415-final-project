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
sudo chmod 700 /etc/profile.d/mysqlc.sh
#source /etc/profile.d/mysqlc.sh

# Check if the file exists and read it line by line to get all the instances DNS
cd ~
filename="instances.txt"
if [ -e "$filename" ]; then
    line_counter=0
    while read -r line; do
        ((line_counter++))
        if [ "$line_counter" -eq 1 ]; then
            KEY_NAME="$line"
        elif [ "$line_counter" -eq 2 ]; then
            INSTANCE1="$line"
        elif [ "$line_counter" -eq 3 ]; then
            INSTANCE2="$line"
        elif [ "$line_counter" -eq 4 ]; then
            INSTANCE3="$line"
        elif [ "$line_counter" -eq 5 ]; then
            INSTANCE4="$line"
        elif [ "$line_counter" -eq 6 ]; then
            INSTANCE5="$line"
        fi
    done < "$filename"
fi

# configurate the manager instance
sudo mkdir -p /opt/mysqlcluster/deploy
cd /opt/mysqlcluster/deploy
sudo mkdir conf
sudo mkdir mysqld_data
sudo mkdir ndb_data
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
hostname=$INSTANCE2
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=$INSTANCE3
nodeid=3
serverport=50501

[ndbd]
hostname=$INSTANCE4
nodeid=4
serverport=50502

[ndbd]
hostname=$INSTANCE5
nodeid=5
serverport=50503

[mysqld]
nodeid=50
EOF'