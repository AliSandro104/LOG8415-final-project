# mysql_master.py
import socket
import mysql.connector

def process_sql_query(sql_query):
    # Update the MySQL connection parameters with your actual values
    db_config = {
        'host': 'your_mysql_host',
        'user': 'your_mysql_user',
        'password': 'your_mysql_password',
        'database': 'your_database_name',
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

        # Fetch the result (if any)
        result = cursor.fetchall()  # Adjust based on the nature of your query

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result
    except mysql.connector.Error as err:
        return f"Error: {err}"

def main():
    master_host = '127.0.0.1'  # Update with the actual IP address or hostname
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