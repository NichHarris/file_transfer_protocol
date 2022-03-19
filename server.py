""" 
Nicholas Harris
40111093
COEN 366 - FTP Project
Section: WJ-X

I, Nicholas Harris, am the sole author of the file
"""

import binascii
from genericpath import exists
import os
import sys
import socket

# Default host and port
PORT = 12000
HOSTNAME = 'localhost'
CLIENT_FILES_PATH = 'client_files'
SERVER_FILES_PATH = 'server_files'

PUT_CHANGE = 0b000
GET = 0b001
FILE_NOT_FOUND = 0b010
UNKNOWN_REQ = 0b011
FAIL_CHANGE = 0b101
HELP = 0b110


# Request user input for hostname and port number
def request_input():
    print('Enter a valid hostname (ex: localhost):\n')
    input(HOSTNAME)
    print('\nEnter a valid port (ex: 80, 12000, etc.):\n')
    input(PORT)

# TODO: Validate hostname and port
def is_valid():
    print(HOSTNAME)
    print(PORT)
    return True

def decode_request(req):
    res = '0b'
    if (req[2:5] == '011'):
        res = response_help(res)

        print(f'debug response_help(): binary_str {res}\n')
        return res
    elif(req[2:5] == '000'):
        return response_put(res, req)
    elif(req[2:5] == '001'):
        return response_get(res, req)
    elif(req[2:5] == '010'):
        return response_change(res, req)
    else:
        return unkwn_req(res)

# TODO: Test 
def response_put(res, req):
    filename_length = int(req[5:10], 2)

    last_filename_bit_index = 2 + 8 + (filename_length)*8
    filename = req[10:last_filename_bit_index]
    bin_to_int = int(filename, 2)
    filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')

    file_data = req[last_filename_bit_index + 4*8:]
    bin_to_int = int(file_data, 2)
    file_data = binascii.unhexlify('%x' % bin_to_int).decode()[::-1]

    with open(f'{SERVER_FILES_PATH}/{filename}', 'w') as file:
        file.write(file_data)

    if (exists(f'{SERVER_FILES_PATH}/{filename}')):
        # Binary rep of sucessful put
        res += '{:03b}'.format(PUT_CHANGE)
        res += '{:05b}'.format(0)
    else:
        res = error_file(res)
    return res   

# TODO: 
def response_get(res, req):
    return True  

# TODO: 
def response_change(res, req):
    old_filename_length = int(req[5:10], 2)

    last_old_filename_bit_index = 2 + 8 + (old_filename_length)*8
    old_filename = req[10:last_old_filename_bit_index]
    bin_to_int = int(old_filename, 2)
    old_filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')

    # Check if old file name actually exists
    if (exists(f'{SERVER_FILES_PATH}/{old_filename}')):
        new_filename_length = int(req[last_old_filename_bit_index:last_old_filename_bit_index + 8], 2)

        start_new_filename_bit = last_old_filename_bit_index + 8

        last_new_filename_bit_index = start_new_filename_bit + (new_filename_length)*8

        new_filename = req[start_new_filename_bit:last_new_filename_bit_index]
        bin_to_int = int(new_filename, 2)
        new_filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')

        # Rename file
        os.rename(f'{SERVER_FILES_PATH}/{old_filename}', f'{SERVER_FILES_PATH}/{new_filename}')

        # Final check for updated name
        if (exists(f'{SERVER_FILES_PATH}/{new_filename}')):
            # Binary rep of sucessful put
            res += '{:03b}'.format(PUT_CHANGE)
            res += '{:05b}'.format(0)
        else:
            res = unsuccessful_change(res)
    else:
        res = error_file(res)
  
    return res  

# TODO: Test
def error_file(res):
    # Binary rep of file not found req code
    res += '{:03b}'.format(FILE_NOT_FOUND)
    res += '{:05b}'.format(0)

    print(f'debug error_file(): binary_str {res}\n')
    return res

# TODO: Test
def unkwn_req(res):
    # Binary rep of unknown req code
    res += '{:03b}'.format(UNKNOWN_REQ)
    res += '{:05b}'.format(0)

    print(f'debug unkwn_req(): binary_str {res}\n')
    return res

# TODO: Test
def unsuccessful_change(res):
    # Binary rep of unsuccessful req code
    res += '{:03b}'.format(FAIL_CHANGE)
    res += '{:05b}'.format(0)

    print(f'debug unsuccessful_change(): binary_str {res}\n')
    return res

def response_help(res):
    # String rep of help str
    help_str = 'Help: get put change help bye'
    # Binary rep of rescode
    res += '{:03b}'.format(HELP)

    # Binary rep of help str length
    res += '{:05b}'.format(len(help_str))
    
    # Binary rep of help str
    res += str(bin(int(binascii.hexlify(help_str.encode()), 16)))

    return res

# Initialize and run the socket
def run_server():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOSTNAME, PORT))
            s.listen()
            print(f'Server is listening to port {PORT} at host {HOSTNAME}...\n')
            print(f'{HOSTNAME}:{PORT}/\n')

            while(True):
                connection, address = s.accept()
                print('Server connected...\n')

                data = connection.recv(1024)

                if not data:
                    print('Listening for connection...')
                    connection.close()
                    continue

                req = data.decode()
                print('Request received...\n')
                print('Decoding request...\n')

                res = decode_request(req)
                connection.sendall(res.encode())
        except Exception:
            print('Closing socket due to exception')


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

    # Terminate program
    print('Exiting program...\n')
