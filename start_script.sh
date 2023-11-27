#!/bin/bash

# Configure AWS Cluster
python aws_setup.py

# open config file
sed -i -e 's/\r$//' config.txt
filename="config.txt"

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

#sed -i "s@chmod 600 /home/ubuntu/.ssh/.*@chmod 600 /home/ubuntu/.ssh/$KEY_NAME@" setup.sh

sleep 1m

sed -i -e 's/\r$//' install_mysql.sh

# copy file to the unique instance 
scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$INSTANCE1:/home/ubuntu
#scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$INSTANCE1:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$INSTANCE1:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME install_mysql.sh ubuntu@$INSTANCE1:/home/ubuntu

# copy file to the master instance 
scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$INSTANCE2:/home/ubuntu
#scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$INSTANCE2:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$INSTANCE2:~/.ssh
scp -o StrictHostKeyChecking=no -i $KEY_NAME install_mysql.sh ubuntu@$INSTANCE2:/home/ubuntu

rm ~/.ssh/$KEY_NAME
