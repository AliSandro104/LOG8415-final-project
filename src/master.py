import socket
import mysql.connector

def process_sql_query(sql_query):
    # sql config 
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '',
        'database': 'sakila',
    }

    try:
        # Connect to the MySQL server
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(sql_query)

        # If the query modifies the database, commit the changes
        if sql_query.strip().lower().startswith(('insert', 'update', 'delete')):
            connection.commit()

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

    master_host = ip_addresses[1]
    master_port = 8083

    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_socket.bind((master_host, master_port))
    master_socket.listen(1)
    print(f"Master listening on {master_host}:{master_port}")

    while True:
        conn, addr = master_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Process the SQL query
        result = process_sql_query(data)

        # Send the result back to the proxy
        conn.sendall(str(result).encode('utf-8'))

        conn.close()

if __name__ == '__main__':
    main()