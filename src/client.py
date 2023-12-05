import socket

def read_actor_data():
    # Get actor details from the user and prepare the query
    first_name = input("Enter actor's first name: ")
    last_name = input("Enter actor's last name: ")

    query = "SELECT * FROM actor WHERE actor.first_name = '{}' AND actor.last_name = '{}';".format(first_name, last_name)
    return query

def write_actor_data():
    # Get actor details from the user and prepare the query
    first_name = input("Enter actor's first name: ")
    last_name = input("Enter actor's last name: ")

    query = "INSERT INTO actor (first_name, last_name) VALUES ('{}' , '{}');".format(first_name, last_name)
    return query

def delete_actor_data():
    # Get actor details from the user and prepare the query
    first_name = input("Enter actor's first name: ")
    last_name = input("Enter actor's last name: ")

    query = "DELETE FROM actor WHERE actor.first_name = '{}' AND actor.last_name = '{}';".format(first_name, last_name)
    return query

def read_film_data():
    # Get actor details from the user and prepare the query
    first_name = input("Enter actor's first name: ") # Ex: Adam
    last_name = input("Enter actor's last name: ") # Ex: Grant

    query = "SELECT film.title, film.release_year FROM film JOIN film_actor ON film.film_id = film_actor.film_id JOIN actor ON film_actor.actor_id = actor.actor_id WHERE actor.first_name = '{}' AND actor.last_name = '{}';".format(first_name, last_name)
    return query

def main():
    # Open the config file to get the public ip of the gatekeeper
    filename = 'ip_addresses/cloud_pattern_public_ip.txt'
    with open(filename, 'r') as file:
        gatekeeper_host = file.readline().strip()
    
    gatekeeper_port = 8080

    # connect to the gatekeeper
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((gatekeeper_host, gatekeeper_port))

    print("Choose one of the three db operations below:")
    print("1. Read the info of a specific actor in the sakila db.")
    print("2. Insert a new actor in the sakila db.")
    print("3. Delete an existing actor in the sakila db.")
    print("4. Read all films in which a specific actor has featured in from the sakila db.")

    operation = input("Type the corresponding number (1, 2, 3 or 4): ")

    if operation == "1":
        sql_query = read_actor_data()

    elif operation == "2":
        sql_query = write_actor_data()

    elif operation == "3":
        sql_query = delete_actor_data()

    elif operation == "4":
        sql_query = read_film_data()
    
    else:
        print("Error: You did not insert a valid input. Program will terminate. Bye!")
        return

    # Send the query to the gatekeeper
    client_socket.sendall(sql_query.encode('utf-8'))

    # Receive and print the result from the gatekeeper
    result = client_socket.recv(1024).decode('utf-8')
    print(result)

    client_socket.close()


if __name__ == '__main__':
    main()