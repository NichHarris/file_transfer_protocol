from multiprocessing import connection
import os
from pickle import TRUE
import socket
import json

# Default host and port
PORT = 12000
HOSTNAME = 'localhost'

# Request user input for hostname and port number
def request_input():
    print('Enter a valid hostname (ex: localhost):\n')
    input(HOSTNAME)
    print('\nEnter a valid port (ex: 80, 12000, etc.):\n')
    input(PORT)

# Validate hostname and port
def is_valid():
    print(PORT)
    print(HOSTNAME)
    return True

# Initialize and run the socket
def run_server():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOSTNAME, PORT))
            s.listen()
            print(f'Server is listening to port {PORT} at host {HOSTNAME}...\n')
            print(f'{HOSTNAME}:{PORT}/\n')

            connection, address = s.accept()
            print('Server connected...\n')

            with connection:
                while True:
                    data = connection.recv(1024)

                    if not data:
                        break

                    print('Request received...\n')
                    

        except KeyboardInterrupt:
            print('Closing socket due to keyboard interrupt')


# Main program execution
if __name__ == '__main__':

    # TODO: Add support for CLI arg -d --debug for debug mode

    # Ask for user to input valid hostname and port number
    request_input()

    # Validate input hostname and port number
    while(not is_valid()):
        print('\nInvalid port number and hostname... try again\n')
        request_input()

    print('Hostname and port accepted... attempting to run server\n')
    run_server()
