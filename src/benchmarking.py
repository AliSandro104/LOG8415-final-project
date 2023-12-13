import socket
import time

node_selection_algorithms = ['Direct hit', 'Random', 'Customized']

def benchmark_cloud_pattern(num_requests):
     # Open the config file to get the private ip of the trusted host
    filename = '/home/ubuntu/flaskapp/cloud_pattern_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    # Connect to the trusted host
    trusted_host_address = ip_addresses[1].strip()
    trusted_host_port = 8080

    average_times = {} # prepare the dict that will contain the average time for each node selection algorithm

    for i in range(1,4): # 1 = 'Direct hit', 2 = 'Random', 3 = 'Customized'
        algorithm = node_selection_algorithms[i - 1]
        total_response_time = 0

        print(f"\nBenchmarking the '{algorithm}' algorithm")
        for j in range(num_requests):
            operation = "4"  # The value 4 is the encoding of a read transaction that gets all the films of an actor
            first_name = "Adam"
            last_name = "Grant"
            encoded_algorithm = str(i)

            data = f"{operation}|{first_name}|{last_name}|{encoded_algorithm}"

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((trusted_host_address, trusted_host_port)) # connect to the trusted host

            start_time = time.time() # track the start time
            client_socket.sendall(data.encode('utf-8'))
            result = client_socket.recv(1024).decode('utf-8')
            
            end_time = time.time() # track the end time
            elapsed_time = end_time - start_time # compute the response time
            total_response_time += elapsed_time

            query_result, chosen_node = result.split('|')

            # Print the result of each run
            print(f"\nRun number: {j+1}")
            print(f"Query result: {query_result}")
            print(f"Chosen node: {chosen_node}")

        average_response_time = total_response_time / num_requests # compute the average response time in seconds
        average_times[algorithm] = average_response_time  # store the average in a dict that will be printed later

    client_socket.close()
    return average_times

def main():
    num_requests = 1000
    average_times = benchmark_cloud_pattern(num_requests) # perform the benchmarking
    
    # print the average response time for each node selection algorithm
    print(f"\nFinal average response time for each node selection algorithm")
    for node_selection_algorithm in average_times:
        print(f"{node_selection_algorithm}: {float(average_times[node_selection_algorithm]) * 1000} milliseconds")

if __name__ == "__main__":
    main() 