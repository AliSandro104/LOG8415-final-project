SOURCE /tmp/sakila-db/sakila-schema.sql;SOURCE /tmp/sakila-db/sakila-data.sql;USE sakila;GRANT ALL ON *.* TO 'worker1'@'ip-172-31-42-18.ec2.internal' IDENTIFIED BY 'worker1';
GRANT ALL ON *.* TO 'worker2'@'ip-172-31-42-18.ec2.internal' IDENTIFIED BY 'worker2';
GRANT ALL ON *.* TO 'worker3'@'ip-172-31-42-18.ec2.internal' IDENTIFIED BY 'worker3';
