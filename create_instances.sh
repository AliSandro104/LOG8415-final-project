#!/bin/bash

# Configure AWS Cluster
python aws_setup.py

# open config file
sed -i -e 's/\r$//' instances.txt
filename="instances.txt"

# Check if the file exists and read it line by line
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

# Copy pem key to .ssh
cp $KEY_NAME ~/.ssh

sed -i "s@chmod 600 /home/ubuntu/.ssh/.*@chmod 600 /home/ubuntu/.ssh/$KEY_NAME@" setup_manager.sh
sed -i "s@chmod 600 /home/ubuntu/.ssh/.*@chmod 600 /home/ubuntu/.ssh/$KEY_NAME@" setup_worker.sh

sleep 1m

# adjust the script files to be able to run them
sed -i -e 's/\r$//' install_mysql.sh
sed -i -e 's/\r$//' setup_manager.sh
sed -i -e 's/\r$//' setup_worker.sh
chmod 777 install_mysql.sh
chmod 777 setup_manager.sh
chmod 777 setup_worker.sh

# copy file to the unique instance 
scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$INSTANCE1:/home/ubuntu
#scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$INSTANCE1:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$INSTANCE1:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME install_mysql.sh ubuntu@$INSTANCE1:/home/ubuntu

# copy file to the manager instance 
scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$INSTANCE2:/home/ubuntu
#scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$INSTANCE2:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$INSTANCE2:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME setup_manager.sh ubuntu@$INSTANCE2:/home/ubuntu
scp -o StrictHostKeyChecking=no -i $KEY_NAME instances_private.txt ubuntu@$INSTANCE2:/home/ubuntu

# copy file to the worker1 instance
scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$INSTANCE3:/home/ubuntu
#scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$INSTANCE3:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$INSTANCE3:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME setup_worker.sh ubuntu@$INSTANCE3:/home/ubuntu

# copy file to the worker2 instance
scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$INSTANCE4:/home/ubuntu
#scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$INSTANCE4:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$INSTANCE4:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME setup_worker.sh ubuntu@$INSTANCE4:/home/ubuntu

# copy file to the worker3 instance
scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$INSTANCE5:/home/ubuntu
#scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$INSTANCE5:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$INSTANCE5:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME setup_worker.sh ubuntu@$INSTANCE5:/home/ubuntu

rm ~/.ssh/$KEY_NAME
