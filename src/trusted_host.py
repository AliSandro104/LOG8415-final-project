import socket
import re

def validate_request(query):
    # extract the user inputs from the query
    match_first_name = re.search(r"first_name\s*=\s*'([^']+)'", query)
    match_last_name = re.search(r"last_name\s*=\s*'([^']+)'", query)

    # Check if matches are found
    if match_first_name and match_last_name:
        user_first_name = match_first_name.group(1)
        user_last_name = match_last_name.group(1)

        if user_first_name.isalpha() and user_last_name.isalpha(): 
            # return true if first name and last name are valid characters
            return True

    return False

def main():
    # Open the config file to get the private ip of the trusted host
    filename = 'cloud_pattern_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    trusted_host_address = ip_addresses[1].strip()
    trusted_host_port = 8081

    proxy_address = ip_addresses[2].strip()
    proxy_port = 8082

    trusted_host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trusted_host_socket.bind((trusted_host_address, trusted_host_port))
    trusted_host_socket.listen(1)
    print(f"Trusted Host listening on {trusted_host_address}:{trusted_host_port}")
    
    # listen on port 8081 for requests
    while True:
        conn, addr = trusted_host_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Validate the request
        if validate_request(data):
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

        conn.close()

if __name__ == '__main__':
    main()