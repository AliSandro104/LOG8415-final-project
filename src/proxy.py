import socket
import random
from re import findall
from subprocess import Popen, PIPE

# create a list that contains the three algorithms that need to be implemented
worker_choice_algorithms = ['Direct hit', 'Random', 'Customized']
algorithm = worker_choice_algorithms[2] # Customized

# measure the response time when pinging a server with an ip address
# code inspired by https://medium.com/@networksuatomation/python-ping-an-ip-adress-663ed902e051
def measure_response_time(ip_address):
    data = ""
    output = Popen(f"ping {ip_address} -c 1", stdout=PIPE, encoding="utf-8", shell=True)
    print(output)

    for line in output.stdout:
        data = data + line
        time_match = findall(r"time=(\d+\.\d+)", data) # search for the round-trip time in the data string

    if time_match:
        return float(time_match[-1]) # if a time was found in the output, we return it
    else:
        return float('inf')  # else, return infinity
    
def customized_algorithm(ip_addresses_workers):
    response_times = {}
    
    for ip_address in ip_addresses_workers:
        response_times[ip_address] = measure_response_time(ip_address) # measure the response time of each worker

    print(response_times)
    return min(response_times, key=response_times.get) # get the key which is the ip address corresponding to the minimum response time

def choose_node(data):
    # Open the config file to get the private ip of the cluster nodes
    filename = 'cluster_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    ip_addresses = [ip.strip() for ip in ip_addresses]
    sql_query_type = data.split()[0].lower() # get the first word of the sql query to know if it's a read or write transaction

    if algorithm == 'Direct hit' or sql_query_type != "select" : # if the algorithm is 'Direct hit' or if the sql query requires a write transaction
        return ip_addresses[1] # return the master node
    
    elif algorithm == 'Random': # if the algorithm is 'Random'
        random_list = ip_addresses[-3] # take the last three elements of the list (representing the ip addresses of the worker nodes)
        return random.choice(random_list) # return the ip address of a random worker
    
    elif algorithm == 'Customized': # if the algorithm is 'Customized'
        return customized_algorithm(ip_addresses[-3]) # call method that will compute the response time of each worker and choose the smallest one

def main():
    # Open the config file to get the public ip of the trusted host
    filename = 'cloud_pattern_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    ip_addresses = [ip.strip() for ip in ip_addresses]
    proxy_host = ip_addresses[2]
    proxy_port = 8082

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((proxy_host, proxy_port))
    proxy_socket.listen(1)
    print(f"Proxy listening on {proxy_host}:{proxy_port}")

    while True:
        conn, addr = proxy_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        node_ip_address = choose_node(data)
        node_port = 8083

        print(node_ip_address)

        node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node_socket.connect((node_ip_address, node_port))
        node_socket.sendall(data.encode('utf-8'))

        # Receive and forward the result from the node
        result = node_socket.recv(1024).decode('utf-8')
        conn.sendall(result.encode('utf-8'))

        node_socket.close()
        conn.close()

if __name__ == '__main__':
    main()