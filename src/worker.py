import socket
import mysql.connector

def get_worker_info():
    filename = 'cluster_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()
    
    ip_addresses = [ip.strip() for ip in ip_addresses]

    # identify worker number
    hostname = socket.getfqdn()
    worker_num = ip_addresses.index(hostname) - 1
    
    # return the worker number and its private ip address
    return worker_num, ip_addresses[worker_num + 1]

def process_sql_query(sql_query, worker_num):
    # Open the config file to get the private ip of the master node
    filename = 'cluster_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    ip_addresses = [ip.strip() for ip in ip_addresses]
    
    # sql config 
    db_config = {
        'host': ip_addresses[1],
        'user': 'worker{}'.format(worker_num),
        'password': 'worker{}'.format(worker_num),
        'database': 'sakila',
    }

    try:
        # Connect to the MySQL server
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(sql_query)

        # Fetch the result
        result = cursor.fetchall() 

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result
    
    except mysql.connector.Error as err:
        return f"Error: {err}"

def main():
    # Open the config file to get the private ip of the master node
    filename = 'cluster_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    ip_addresses = [ip.strip() for ip in ip_addresses]
    
    # identify worker number and worker hostname
    worker_num, worker_host = get_worker_info()

    worker_port = 8082

    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_socket.bind((worker_host, worker_port))
    master_socket.listen(1)
    print(f"Worker {worker_num} listening on {worker_host}:{worker_port}")

    # listen on port 8082 for requests from the proxy
    while True:
        conn, addr = master_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Process the SQL query
        result = process_sql_query(data, worker_num)

        # Send the result back to the proxy
        conn.sendall(str(result).encode('utf-8'))

        conn.close()

if __name__ == '__main__':
    main()