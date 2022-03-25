""" 
Nicholas Harris
40111093 - n_arri
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
HOSTNAME = '127.0.0.1'
CLIENT_FILES_PATH = 'client_files'
SERVER_FILES_PATH = 'server_files'
DEBUG_MODE = False
DEV_MODE = False

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

def decode_request(req):
    res = '0b'
    success, is_get, is_put = False, False, False
    last_bit, file_size, filename = 0, 0, None

    if (req[2:5] == '011'):
        res = response_help(res)
    elif(req[2:5] == '000'):
        is_put = True
        success, res, last_bit, file_size, filename = response_put(res, req)
    elif(req[2:5] == '001'):
        success, res, filename, is_get = response_get(res, req)
    elif(req[2:5] == '010'):
        success, res, filename = response_change(res, req)
    else:
        res = unkwn_req(res)
    return success, res, last_bit, file_size, filename, is_get, is_put

def response_put(res, req):
    filename_length = int(req[5:10], 2)

    last_filename_bit_index = 10 + filename_length*8
    filename = req[10:last_filename_bit_index]
    bin_to_int = int(filename, 2)
    filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')
    
    last_bit_of_req = last_filename_bit_index + 4*8
    file_size = int(req[last_filename_bit_index:last_bit_of_req], 2)
    file_size_bits = file_size*8

    return True, res, last_bit_of_req, file_size_bits, filename

def response_get(res, req):
    is_get = True
    res += req[2:5]
    success = False
    filename_size = req[5:10]
    res += filename_size

    filename_bin = req[10:]
    bin_to_int = int(filename_bin, 2)
    filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')
    res += filename_bin
    print(filename)
    if (exists(f'{SERVER_FILES_PATH}/{filename}')):
        size = os.path.getsize(f'{SERVER_FILES_PATH}/{filename}')
        file_size = f'{size:032b}'
        res += file_size
        success = True

        if (DEV_MODE):
            print(f'debug response_get(): binary_str {res}\n')
    else:
        res = '0b'
        res = error_file(res)
        is_get = False
    return success, res, filename, is_get

def response_change(res, req):
    success = False
    old_filename_length = int(req[5:10], 2)

    last_old_filename_bit_index = 10 + old_filename_length*8
    old_filename = req[10:last_old_filename_bit_index]
    bin_to_int = int(old_filename, 2)
    old_filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')

    new_filename = None
    # Check if old file name actually exists
    if (exists(f'{SERVER_FILES_PATH}/{old_filename}')):
        new_filename_length = int(req[last_old_filename_bit_index:last_old_filename_bit_index + 8], 2)

        start_new_filename_bit = last_old_filename_bit_index + 8

        last_new_filename_bit_index = start_new_filename_bit + new_filename_length*8

        new_filename = req[start_new_filename_bit:last_new_filename_bit_index]
        bin_to_int = int(new_filename, 2)
        new_filename = binascii.unhexlify('%x' % bin_to_int).decode('ascii')

        # Check if new filename already exists
        if (exists(f'{SERVER_FILES_PATH}/{new_filename}')):
            res = unsuccessful_change(res)
        else:
            # Rename file
            os.rename(f'{SERVER_FILES_PATH}/{old_filename}', f'{SERVER_FILES_PATH}/{new_filename}')

            # Check if name updated successfully
            if (exists(f'{SERVER_FILES_PATH}/{new_filename}')):
                success = True
                res += f'{PUT_CHANGE:03b}'
                res += f'{0:05b}'
            else:
                res = unsuccessful_change(res)
    else:
        res = unsuccessful_change(res)
  
    return success, res, new_filename

def error_file(res):
    # Binary rep of file not found req code
    res += f'{FILE_NOT_FOUND:03b}'
    res += f'{0:05b}'

    if (DEV_MODE):
        print(f'debug error_file(): binary_str {res}\n')
    return res

def unkwn_req(res):
    # Binary rep of unknown req code
    res += f'{UNKNOWN_REQ:03b}'
    res += f'{0:05b}'

    if (DEV_MODE):
        print(f'debug unkwn_req(): binary_str {res}\n')
    return res

def unsuccessful_change(res):
    # Binary rep of unsuccessful req code
    res += f'{FAIL_CHANGE:03b}'
    res += f'{0:05b}'

    if (DEV_MODE):
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

    if (DEV_MODE):
        print(f'debug response_help(): binary_str {res}\n')
    return res

# Initialize and run the socket
def run_server():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOSTNAME, PORT))
            s.listen()
            print(f'Server is listening to port {PORT} at host {HOSTNAME}...\n')

            connection, address = s.accept()
            print('Server connected to client...\n')
            while(True):

                data = connection.recv(1024)
                if not data:
                    print('Client disconnected...')
                    connection.close()
                    print('Listening for connection...\n')
                    connection, address = s.accept()
                    continue

                print('Request received...')
                req = data.decode()
                if (DEBUG_MODE):
                    print(f'Debug - Request message received: {req}')
                print('Decoding request...')

                success, res, last_bit_of_req, file_size_bits, filename, is_get, is_put = decode_request(req)
                if (success):

                    # If command is a put, retrieve the file after the request
                    if (is_put):
                        file_data = ''
                        # Means there is some data passed within the request
                        if (len(req) > last_bit_of_req):
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
                    if (DEBUG_MODE):
                        print(f'Debug - Response message being sent: {res}')
                    connection.send(res.encode())

                    # If request is a get, send the file after the response
                    if (is_get):
                        with open(f'{SERVER_FILES_PATH}/{filename}', 'rb') as file:
                            for line in file.readlines():
                                file_lines = line
                                line_size = int(len(line.hex())/2)

                                # Binary rep of line data
                                line_data = f'{int(binascii.hexlify(file_lines), 16):0{line_size*8}b}'
                                connection.send(line_data.encode())
                else:
                    # generate response                    
                    if (DEBUG_MODE):
                        print(f'Debug - Response message being sent: {res}')
                    connection.send(res.encode())
                
                print('Response sent...\n')
        except Exception as e:
            print('Closing socket due to exception:' + e)


# Main program execution
if __name__ == '__main__':
    for i, arg in enumerate(sys.argv):
        if i == 1:
            HOSTNAME = str(arg)
        elif i == 2:
            PORT = int(arg)
        elif i == 3:
            DEBUG_MODE = int(arg)
        elif i == 4:
            DEV_MODE = int(arg)
    
    # Start server
    print('Hostname and port accepted... attempting to run server\n')
    run_server()

    # Terminate program
    print('Exiting program...\n')
