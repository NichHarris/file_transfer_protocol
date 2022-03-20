""" 
Nicholas Harris
40111093
COEN 366 - FTP Project Server File
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
    print(req)
    if (req[2:5] == '011'):
        res = response_help(res)

        print(f'debug response_help(): binary_str {res}\n')
        return res, 0, 0, None
    elif(req[2:5] == '000'):
        return response_put(res, req)
    elif(req[2:5] == '001'):
        return response_get(res, req), 0, 0, None
    elif(req[2:5] == '010'):
        return response_change(res, req), 0, 0, None
    else:
        return unkwn_req(res), 0, 0, None

# TODO: Test 
def response_put(res, req):
    filename_length = int(req[5:10], 2)

    last_filename_bit_index = 10 + (filename_length)*8
    filename = req[10:last_filename_bit_index]
    bin_to_int = int(filename, 2)
    filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')
    
    last_bit_of_req = last_filename_bit_index + 4*8
    file_size = int(req[last_filename_bit_index:last_bit_of_req], 2)
    file_size_bits = file_size*8
    
    # Means there is some data passed within the request
    if (len(req) > last_bit_of_req):
        print(req[last_bit_of_req:])

    return res, last_bit_of_req, file_size_bits, filename

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
            res += f'{PUT_CHANGE:03b}'
            res += f'{0:05b}'
        else:
            res = unsuccessful_change(res)
    else:
        res = error_file(res)
  
    return res  

# TODO: Test
def error_file(res):
    # Binary rep of file not found req code
    res += f'{FILE_NOT_FOUND:03b}'
    res += f'{0:05b}'

    print(f'debug error_file(): binary_str {res}\n')
    return res

# TODO: Test
def unkwn_req(res):
    # Binary rep of unknown req code
    res += f'{UNKNOWN_REQ:03b}'
    res += f'{0:05b}'

    print(f'debug unkwn_req(): binary_str {res}\n')
    return res

# TODO: Test
def unsuccessful_change(res):
    # Binary rep of unsuccessful req code
    res += f'{FAIL_CHANGE:03b}'
    res += f'{0:05b}'

    print(f'debug unsuccessful_change(): binary_str {res}\n')
    return res

def response_help(res):
    # String rep of help str
    help_str = 'Help: get put change help bye'
    # Binary rep of rescode
    res += f'{HELP:03b}'

    # Binary rep of help str length
    res += f'{len(help_str):05b}'
    
    # Binary rep of help str TODO: Change this?
    res += str(bin(int(binascii.hexlify(help_str.encode()), 16)))

    return res

# Initialize and run the socket
def run_server():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOSTNAME, PORT))
            s.listen()
            print(f'Server is listening to port {PORT} at host {HOSTNAME}...\n')
            print(f'https://{HOSTNAME}:{PORT}/\n')

            connection, address = s.accept()
            while(True):
                print('Server connected to client...\n')

                data = connection.recv(1024)
                if not data:
                    print('Client disconnected...\n')
                    connection.close()
                    print('Listening for connection...')
                    connection, address = s.accept()
                    continue

                req = data.decode()
                print('Request received...\n')
                print('Decoding request...\n')

                res, last_bit_of_req, file_size_bits, filename = decode_request(req)

                file_data = ''
                # Means there is some data passed within the request
                if (len(req) > last_bit_of_req):
                    print(req[last_bit_of_req:])
                    file_data = req[last_bit_of_req:]

                file_data_remaining = file_size_bits - len(file_data)
                while (file_data_remaining > 0):
                    data = connection.recv(1024)
                    data = data.decode()
                    file_data += data
                    file_data_remaining = file_size_bits - len(file_data)

                bin_to_int = int(file_data, 2)
                file_data = binascii.unhexlify('%x' % bin_to_int)
                with open(f'{SERVER_FILES_PATH}/{filename}', 'wb') as file:
                    file.write(file_data)
                
                if (exists(f'{SERVER_FILES_PATH}/{filename}')):
                    # Binary rep of sucessful put
                    res += f'{PUT_CHANGE:03b}'
                    res += f'{0:05b}'
                else:
                    res = error_file(res)

                # generate response
                connection.sendall(res.encode())
        except Exception as e:
            print('Closing socket due to exception:' + e)


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
