import socket

def validate_request(first_name, last_name):
    # Check if both first name and last name are non-empty and contain only alphabetic characters
    if first_name.isalpha() and last_name.isalpha():
        return True
    return False

def construct_sql_query(operation, first_name, last_name):
    # Construct the sql query based on the operation chosen by the user
    if operation == "1":
        return f"SELECT * FROM actor WHERE actor.first_name = '{first_name}' AND actor.last_name = '{last_name}';"
    elif operation == "2":
        return f"INSERT INTO actor (first_name, last_name) VALUES ('{first_name}', '{last_name}');"
    elif operation == "3":
        return f"DELETE FROM actor WHERE actor.first_name = '{first_name}' AND actor.last_name = '{last_name}';"
    elif operation == "4":
        return f"SELECT film.title, film.release_year FROM film JOIN film_actor ON film.film_id = film_actor.film_id JOIN actor ON film_actor.actor_id = actor.actor_id WHERE actor.first_name = '{first_name}' AND actor.last_name = '{last_name}';"
    else:
        return "Error: Invalid operation"

def main():
    # Open the config file to get the private ip of the trusted host and proxy
    filename = 'cloud_pattern_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    trusted_host_address = ip_addresses[1].strip()
    trusted_host_port = 8080

    proxy_address = ip_addresses[2].strip()
    proxy_port = 8081

    trusted_host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trusted_host_socket.bind((trusted_host_address, trusted_host_port))
    trusted_host_socket.listen(1)
    print(f"Trusted Host listening on {trusted_host_address}:{trusted_host_port}")

    # listen on port 8080 for requests from the gatekeeper
    while True:
        conn, addr = trusted_host_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Split the received data into components
        components = data.split('|')

        # Validate the request
        if len(components) == 4:
            operation, first_name, last_name, proxy_algorithm = components

            # Check if the inputs are valid
            if validate_request(first_name, last_name):
                # Construct the SQL query based on the operation and user input
                sql_query = construct_sql_query(operation, first_name, last_name)

                # add the proxy algorithm to the data to be sent
                data = f"{sql_query}|{proxy_algorithm}"

                # Forward the request to the proxy
                proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                proxy_socket.connect((proxy_address, proxy_port))
                proxy_socket.sendall(data.encode('utf-8'))

                # Receive and forward the result from the proxy
                result = proxy_socket.recv(1024).decode('utf-8')
                conn.sendall(result.encode('utf-8'))

                proxy_socket.close()
            else:
                # Invalid request, send an appropriate response
                conn.sendall("Invalid request".encode('utf-8'))
        else:
            # Invalid request, send an appropriate response
            conn.sendall("Invalid request".encode('utf-8'))

        conn.close()

if __name__ == '__main__':
    main()
