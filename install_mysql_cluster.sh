sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home/
sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

chmod 700 /etc/profile.d/mysqlc.sh
sudo bash -c 'cat >> /etc/profile.d/mysqlc.sh << EOF
export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc
export PATH=$MYSQLC_HOME/bin:$PATH
EOF'

source /etc/profile.d/mysqlc.sh