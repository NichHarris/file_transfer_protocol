import binascii
from msilib.schema import Binary
import os
import socket

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
    print('Enter a valid hostname (ex: localhost):')
    HOSTNAME = input(HOSTNAME)
    print('\nEnter a valid port (ex: 80, 12000, etc.):')
    PORT = input(PORT)

# TODO: Validate hostname and port
def is_valid():
    print(HOSTNAME)
    print(PORT)
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
    req = 0b0
    # Call appropriate format function
    if (opcode == 0b000):
        req = format_put(opcode, user_cmd_split)
    elif (opcode == 0b001):
        req = format_get(opcode, user_cmd_split)
    elif (opcode == 0b010):
        req = format_change(opcode, user_cmd_split)
    else:
        req = format_help(opcode)

    return req

# TODO: Test
def format_put(opcode, user_cmd_split: list[str]):
    # Start encoding binary string to be sent to server
    req = '0b'

    # Binary of length of filename
    filename_length = len(user_cmd_split[1].strip())
    req += concantenate_bits('{:03b}'.format(opcode), '{:05b}'.format(filename_length))

    # Binary rep of filename
    filename = user_cmd_split[1].strip().encode()
    filename = str(bin(int(binascii.hexlify(filename), 16)))
    req = concantenate_bits(req, filename[2:])

    # Binary rep of size of file
    file_size = '{:032b}'.format(os.path.getsize(user_cmd_split[1].strip()))
    req = concantenate_bits(req, file_size[2:])

    # Binary rep of the file itself
    file_binary = ''
    with open(user_cmd_split[1].strip(), 'rb') as file: ##
        file_binary = str(bin(int(binascii.hexlify(file.read()), 16)))
    req = concantenate_bits(req, file_binary[2:])

    print(f'debug format_put(): binary_str {req}\n')
    return req

# TODO: Test
def format_get(opcode, user_cmd_split: list[str]):
    # Start encoding binary string to be sent to server
    req = '0b'

    # Binary of length of filename
    filename_length = len(user_cmd_split[1].strip())
    req += concantenate_bits('{:03b}'.format(opcode), '{:05b}'.format(filename_length))

    # Binary rep of filename
    filename = user_cmd_split[1].strip().encode()
    filename = str(bin(int(binascii.hexlify(filename), 16)))
    req = concantenate_bits(req, filename[2:])

    print(f'debug format_get(): binary_str {req}\n')
    return req

# TODO: Test
def format_change(opcode, user_cmd_split: list[str]):
    if (len(user_cmd_split) == 3):
        # Start encoding binary string to be sent to server
        req = '0b'

        # Binary of length of old_filename
        old_filename_length = len(user_cmd_split[1].strip())
        req += concantenate_bits('{:03b}'.format(opcode), '{:05b}'.format(old_filename_length))

        # Binary rep of old_filename
        old_filename = user_cmd_split[1].strip().encode()
        old_filename = str(bin(int(binascii.hexlify(old_filename), 16)))
        req = concantenate_bits(req, old_filename[2:])

        # Binary of length of new_filename
        new_filename_length = len(user_cmd_split[1].strip())
        req = concantenate_bits('{:03b}'.format(opcode), '{:05b}'.format(new_filename_length))

        # Binary rep of new_filename
        new_filename = str(bin(int(binascii.hexlify(new_filename), 16)))
        req = concantenate_bits(req, new_filename[2:])

        print(f'debug format_change(): binary_str {req}\n')
        return req
    return None

# TODO: Test
def format_help(opcode):
    req = '0b'
    req += concantenate_bits('{:03b}'.format(opcode), '{:05b}'.format(0))
    print(f'debug format_help(): binary_str {req}\n')
    return req

# TODO: Test
def concantenate_bits(left, right):
    return left + right

# Take user command request
def user_requests():
    user_cmd = input()
    while(not validate_user_cmd(user_cmd)):
        print('Invalid user command, please input a valid one\n')
        user_cmd = input()
    return user_cmd.strip()

# Start client
def run_client():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOSTNAME, PORT))
            print('Client connected...\n')
            print('File-Transfer Protocol client active... please enter valid commands')

            while(True):
                cmd = user_requests()
                if (cmd.lower() == 'bye'):
                    break
                req = format_request(cmd)

                s.sendall(req.encode('utf-8'))
                print('Request sent, awaiting response...\n')
                
                res = s.recv(1024)
                print(res.decode())

            print('Closing client socket...\n')
            s.shutdown()

        except KeyboardInterrupt:
            print('Closing socket due to keyboard interrupt')


# Main program execution
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
