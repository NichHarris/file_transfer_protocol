import socket

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

def user_requests():
    return 'string'

def run_client():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOSTNAME, PORT))
            print('Client connected...\n')
            print(f'{HOSTNAME}:{PORT}/\n')

            while(user_requests() != 'bye'):
                HOSTNAME

            print('Closing client socket...\n')
            s.shutdown()

        except KeyboardInterrupt:
            print('Closing socket due to keyboard interrupt')

if __name__ == '__main__':

    # Ask for user to input valid hostname and port number
    request_input()

    # Validate input hostname and port number
    while(not is_valid()):
        print('\nInvalid port number and hostname... try again\n')
        request_input()

    # Start client
    print(f'Hostname and port accepted... attempting to connect client to port {PORT}\n')
    run_client()

    # Terminate program
    print('Exiting program...\n')
