SOURCE /tmp/sakila-db/sakila-schema.sql;
SOURCE /tmp/sakila-db/sakila-data.sql;
USE sakila;

GRANT ALL ON *.* TO 'worker1'@'ec2-54-84-141-25.compute-1.amazonaws.com' IDENTIFIED BY 'worker1';
GRANT ALL ON *.* TO 'worker2'@'ec2-44-198-122-174.compute-1.amazonaws.com' IDENTIFIED BY 'worker2';
GRANT ALL ON *.* TO 'worker3'@'ec2-54-224-84-190.compute-1.amazonaws.com' IDENTIFIED BY 'worker3';
