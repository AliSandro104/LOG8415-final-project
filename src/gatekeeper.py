# gatekeeper.py
import socket

def main():
    # Open the config file to get the private ip of the gatekeeper
    filename = 'cloud_pattern_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()
    
    gatekeeper_host = ip_addresses[0].strip()
    print(gatekeeper_host)
    gatekeeper_port = 8080

    gatekeeper_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gatekeeper_socket.bind((gatekeeper_host, gatekeeper_port))
    gatekeeper_socket.listen(1)
    print(f"Gatekeeper listening on {gatekeeper_host}:{gatekeeper_port}")

    while True:
        conn, addr = gatekeeper_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Data is forwarded to the trusted host without validation
        trusted_host_address = ip_addresses[1].strip()
        trusted_host_port = 8081
        trusted_host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        trusted_host_socket.connect((trusted_host_address, trusted_host_port))
        trusted_host_socket.sendall(data.encode('utf-8'))

        # Receive and forward the result from the trusted host
        result = trusted_host_socket.recv(1024).decode('utf-8')
        conn.sendall(result.encode('utf-8'))

        conn.close()
        trusted_host_socket.close()

if __name__ == '__main__':
    main()