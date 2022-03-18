import os
import socket
from urllib import request

from numpy import binary_repr, size

# Default host and port
PORT = 12000
HOSTNAME = 'localhost'

opcodes = {
    'put': 0b000,
    'get': 0b001,
    'change': 0b010,
    'help': 0b011
}

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

# TODO: Validate it is a command, validate filename is not too long etc (<32 chars)..
def validate_user_cmd(user_cmd: str):
    if (user_cmd.strip() == ''):
        return False
    return True

def format_request(user_cmd: str):
    user_cmd_split = user_cmd.split()
    # Binary representation of the instruction opcode
    opcode = opcodes[user_cmd_split[0].strip().lower()]

    # Call appropriate format function
    if (opcode == 0b000):
        format_put(opcode, user_cmd_split)
    elif (opcode == 0b001):
        format_get(opcode, user_cmd_split)
    elif (opcode == 0b010):
        format_change(opcode, user_cmd_split)
    else:
        format_help(opcode)

    return True

# TODO:
def format_put(opcode, user_cmd_split: list[str]):
    # Start encoding binary string to be sent to server
    binary_str = opcode
    # Binary of length of filename
    filename_length = bin(len(user_cmd_split[1].strip()))
    # Binary rep of filename
    filename = user_cmd_split[1].strip().encode()
    # Binary rep of size of file
    file_size = '{:032b}'.format(os.path.getsize(user_cmd_split[1].strip()))
    # Binary rep of the file itself
    file_binary = 0b0
    with open(user_cmd_split[1].strip(), 'rb') as file:
        file_binary = file.read()

# TODO:
def format_get(opcode, user_cmd_split: list[str]):
    return False

# TODO:
def format_change(opcode, user_cmd_split: list[str]):
    return False

# TODO:
def format_help(opcode):
    return False

def user_requests():
    user_cmd = ''
    input(user_cmd)
    while(validate_user_cmd(user_cmd)):
        print('Invalid user command, please input a valid one\n')
        input(user_cmd)

    format_request(user_cmd)
    return 'string'

def run_client():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOSTNAME, PORT))
            print('Client connected...\n')
            print('File-Transfer Protocol client active... please enter valid commands\n')

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
