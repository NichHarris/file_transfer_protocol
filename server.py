import os
import socket

# Default host and port
PORT = 12000
HOSTNAME = 'localhost'

# Request user input for hostname and port number
def request_input():
    print('Enter a valid hostname (ex: localhost):\n')
    HOSTNAME = input(HOSTNAME)
    print('\nEnter a valid port (ex: 80, 12000, etc.):\n')
    PORT = input(PORT)

# TODO: Validate hostname and port
def is_valid():
    print(HOSTNAME)
    print(PORT)
    return True

def print_help():
    print('List of available commands:\n')
    print('put `{`filename`}`: Transfers file from client machine to server machine\n')
    print('get `{`filename`}`: Retrieves file from server machine to client machine\n')
    print('change `{`OldFileName`}` `{`NewFileName`}`: Update the name of a file on server machine\n')
    print('help: Print out list of available commands\n')
    print('bye: Exit program and close client connection\n')

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
                    req = data.decode('utf-8')
                    print(req)
                    print('Request received...\n')
                    print('Decoding request...\n')
                    

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
