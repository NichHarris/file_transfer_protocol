""" 
Nicholas Harris
40111093
COEN 366 - FTP Project Client File
Section: WJ-X

I, Nicholas Harris, am the sole author of the file
"""

import binascii
from fileinput import filename
from genericpath import exists
import os
import sys
import socket

from isort import file

# Default host and port
PORT = 12000
HOSTNAME = 'localhost'
CLIENT_FILES_PATH = 'client_files'
SERVER_FILES_PATH = 'server_files'
DEBUG_MODE = False

opcodes = {
    'put': 0b000,
    'get': 0b001,
    'change': 0b010,
    'help': 0b011
}

# Request user input for hostname and port number
def request_input():
    print('Enter a valid hostname (ex: localhost):')
    input(HOSTNAME)
    print('\nEnter a valid port (ex: 80, 12000, etc.):')
    input(PORT)

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

def valid_filename(filename):
    if (len(filename) > 0 and len(filename) < 32):
        return True
    return False

def format_request(user_cmd: list[str]):
    # Binary representation of the instruction opcode
    opcode = opcodes[user_cmd[0].strip().lower()]
    req = ''
    status, is_put = False, False

    # Call appropriate format function
    if (opcode == 0b000):
        req, status = format_put(opcode, user_cmd)
        is_put = True
    elif (opcode == 0b001):
        req, status = format_get(opcode, user_cmd)
    elif (opcode == 0b010):
        req, status = format_change(opcode, user_cmd)
    else:
        req, status = format_help(opcode)

    return req, status, is_put

# TODO: Test
def format_put(opcode, user_cmd: list[str]):
    # Start encoding binary string to be sent to server
    req = '0b'

    # Ensure a valid filename is present
    if (len(user_cmd) != 2):
        return None, False

    input_filename = user_cmd[1].strip()
    if (not valid_filename(input_filename)):
        return None, False

    if (exists(f'{CLIENT_FILES_PATH}/{input_filename}')):
        # Binary of length of filename
        filename_length = len(input_filename)
        req += concantenate_bits(f'{opcode:03b}', f'{filename_length:05b}')

        # Binary rep of filename
        filename = input_filename.encode()
        filename = f'{int(binascii.hexlify(filename), 16):0{filename_length*8}b}'
        req = concantenate_bits(req, filename)

        # Binary rep of size of file
        size = os.path.getsize(f'{CLIENT_FILES_PATH}/{input_filename}')
        file_size = f'{size:032b}'
        req = concantenate_bits(req, file_size)

        print(f'debug format_put(): binary_str {req}\n')
    else:
        print('Error file does not exist on client side...\n')
        return None, False
    return req, True

# TODO: Test
def format_get(opcode, user_cmd: list[str]):
    # Start encoding binary string to be sent to server
    req = '0b'

    # Ensure a valid filename is present
    if (len(user_cmd) != 2):
        return None, False
    
    input_filename = user_cmd[1].strip()
    if (not valid_filename(input_filename)):
        return None, False

    # Binary of length of filename
    filename_length = len(input_filename)
    req += concantenate_bits(f'{opcode:03b}', f'{filename_length:05b}')
    print(f'{filename_length:05b}')

    # Binary rep of filename
    filename = input_filename.encode()
    filename = f'{int(binascii.hexlify(filename), 16):0{filename_length*8}b}'
    req = concantenate_bits(req, filename)

    print(f'debug format_get(): binary_str {req}\n')
    return req, True

# TODO: Test
def format_change(opcode, user_cmd: list[str]):
    # Start encoding binary string to be sent to server
    req = '0b'

    # Ensure a valid filename is present
    if (len(user_cmd) != 3):
        return None, False

    input_old_filename = user_cmd[1].strip()
    input_new_filename = user_cmd[2].strip()

    if (not valid_filename(input_old_filename)):
        return None, False
    if (not valid_filename(input_new_filename)):
        return None, False

    # Binary rep of length of old_filename
    old_filename_length = len(input_old_filename)
    req += concantenate_bits(f'{opcode:03b}', f'{old_filename_length:05b}')

    # Binary rep of old_filename
    old_filename = input_old_filename.encode()
    old_filename = f'{int(binascii.hexlify(old_filename), 16):0{old_filename_length*8}b}'
    req = concantenate_bits(req, old_filename)

    # Binary rep of length of new_filename
    new_filename_length = len(input_new_filename)
    req = concantenate_bits(req, f'{new_filename_length:08b}')

    # Binary rep of new_filename
    new_filename = input_new_filename.encode()
    new_filename = f'{int(binascii.hexlify(new_filename), 16):0{new_filename_length*8}b}'
    req = concantenate_bits(req, new_filename)
    
    print(f'debug format_change(): binary_str {req}\n')
    return req, True

# TODO: Test
def format_help(opcode):
    req = '0b'
    req += concantenate_bits(f'{opcode:03b}', f'{0:05b}')
    print(f'debug format_help(): binary_str {req}\n')
    return req, True

# TODO: Test
def concantenate_bits(left, right):
    return left + right

# Take user command request
def user_requests():
    user_cmd = input()
    while(not validate_user_cmd(user_cmd)):
        print('Invalid user command, please input a valid one\n')
        user_cmd = input()
    return user_cmd.strip().split()

def decode_response(res):
    last_bit_of_res, file_size_bits, filename, is_get = 0, 0, None, False
    
    if (res[2:5] == '000'):
        successfull_get_change()
    elif(res[2:5] == '001'):
        is_get = True
        last_bit_of_res, file_size_bits, filename = response_get(res)
    elif(res[2:5] == '010'):
        error_file_not_found()
    elif(res[2:5] == '011'):
        error_unknown_request()
    elif(res[2:5] == '101'):
        unsuccessful_change()
    elif(res[2:5] == '110'):
        help_response()

    return last_bit_of_res, file_size_bits, filename, is_get

def successfull_get_change():
    print('Server successfully executed command')

def error_file_not_found():
    print('Server successfully executed command')

def error_unknown_request():
    print('Server successfully executed command')

def unsuccessful_change():
    print('Server successfully executed command')

def help_response():
    print('Server successfully executed command')

def response_get(res):
    filename_length = int(res[5:10], 2)
    last_filename_bit_index = 10 + filename_length*8
    filename = res[10:last_filename_bit_index]
    bin_to_int = int(filename, 2)
    filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')

    last_bit_of_res = last_filename_bit_index + 4*8
    file_size = int(res[last_filename_bit_index:last_bit_of_res], 2)
    file_size_bits = file_size*8

    return last_bit_of_res, file_size_bits, filename

# Start client
def run_client():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOSTNAME, PORT))
            print('Client connected...')
            print('File-Transfer Protocol client active...\n')

            while(True):
                print('Enter FTP commands:')

                cmd = user_requests()
                if (cmd[0].lower() == 'bye'):
                    break

                req, success, is_put = format_request(cmd)
                if (success):
                    s.send(req.encode())
                    if (is_put):
                        with open(f'{CLIENT_FILES_PATH}/{cmd[1]}', 'rb') as file:
                            for line in file.readlines():
                                file_lines = line
                                line_size = int(len(line.hex())/2)

                                # Binary rep of the line data
                                line_data = f'{int(binascii.hexlify(file_lines), 16):0{line_size*8}b}' 
                                s.send(line_data.encode())

                    print('Request sent, awaiting response...')
                
                data = s.recv(1024)
                res = data.decode()
                print(res)

                last_bit_of_res, file_size_bits, filename, is_get = decode_response(res)
                if (is_get):
                    
                    file_data = ''
                    # Incase some data was passed with response
                    if (len(res) > last_bit_of_res):
                        print(res[last_bit_of_res:])
                        file_data = req[0:]

                    # Receive file
                    file_data_remaining = file_size_bits - len(file_data)
                    while (file_data_remaining > 0):
                        data = s.recv(1024)
                        data = data.decode()
                        file_data += data
                        file_data_remaining = file_size_bits - len(file_data)
                    
                    # Write to file
                    bin_to_int = int(file_data, 2)
                    file_data = binascii.unhexlify('%x' % bin_to_int)
                    with open(f'{CLIENT_FILES_PATH}/{filename}', 'wb') as file:
                        file.write(file_data)

            print('\nClosing client socket...')
        except KeyboardInterrupt:
            print('\nClosing socket due to keyboard interrupt')
        except Exception as e:
            print('\nClosing socket due to exception: ' + e)


# Main program execution
if __name__ == '__main__':

    # TODO: Add support for CLI arg -d --debug for debug mode

    # Ask for user to input valid hostname and port number
    request_input()

    # Validate input hostname and port number
    while(not is_valid()):
        print('\nInvalid port number and hostname... try again')
        request_input()

    # Start client
    print(f'Hostname and port accepted... attempting to connect client to port {PORT}\n')
    run_client()

    # Terminate program
    print('Exiting program...\n')
