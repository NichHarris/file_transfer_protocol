""" 
Nicholas Harris
40111093
COEN 366 - FTP Project Client File
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

# TODO: Validate it is a command, validate filename is not too long etc (<32 chars)..
def validate_user_cmd(user_cmd: list[str]):
    is_valid = True
    if (len(user_cmd) == 0):
        is_valid = False

    if (len(user_cmd) == 3):
        if len(user_cmd[2]) > 31:
            is_valid = False

    if (len(user_cmd) >= 2):
        if len(user_cmd[1]) > 31:
            is_valid = False
    
    if (len(user_cmd) > 3):
        is_valid = False
    
    return is_valid

def valid_filename(filename):
    if (len(filename) > 0 and len(filename) < 32):
        return True
    return False

def format_request(user_cmd: list[str]):
    # Binary representation of the instruction opcode
    opcode = user_cmd[0].strip().lower()
    if opcode in opcodes:
        opcode = opcodes[opcode]

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
    elif (opcode == 0b011):
        req, status = format_help(opcode)
    else:
        req, status = format_unknown(user_cmd)

    return req, status, is_put

def format_unknown(user_cmd):
    req = '0b'
    req += f'{255:08b}'
    return req, True


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

        if (DEV_MODE):
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

    # Binary rep of filename
    filename = input_filename.encode()
    filename = f'{int(binascii.hexlify(filename), 16):0{filename_length*8}b}'
    req = concantenate_bits(req, filename)

    if (DEV_MODE):
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
    

    if (DEV_MODE):
        print(f'debug format_change(): binary_str {req}\n')
    return req, True

# TODO: Test
def format_help(opcode):
    req = '0b'
    req += concantenate_bits(f'{opcode:03b}', f'{0:05b}')
    
    if (DEV_MODE):
        print(f'debug format_help(): binary_str {req}\n')
    return req, True

# TODO: Test
def concantenate_bits(left, right):
    return left + right

# Take user command request
def user_requests():
    user_cmd = input()
    while(not validate_user_cmd(user_cmd.strip().split())):
        print('Invalid user command, please input a valid one:')
        user_cmd = input()
    return user_cmd.strip().split()

def decode_response(res, cmd):
    last_bit_of_res, file_size_bits, filename, is_get = 0, 0, None, False
    
    if (res[2:5] == '000'):
        successfull_put_change(cmd)
    elif(res[2:5] == '001'):
        is_get = True
        last_bit_of_res, file_size_bits, filename = response_get(res)
    elif(res[2:5] == '010'):
        error_file_not_found(cmd)
    elif(res[2:5] == '011'):
        error_unknown_request(cmd)
    elif(res[2:5] == '101'):
        unsuccessful_change(cmd)
    elif(res[2:5] == '110'):
        help_response(res)

    return last_bit_of_res, file_size_bits, filename, is_get

def successfull_put_change(cmd):
    if (len(cmd) == 2):
        print(f'{cmd[1]} has been uploaded successfully.')
    if (len(cmd) == 3):
        print(f'{cmd[1]} has been change into {cmd[2]}.')

def error_file_not_found(cmd):
    if (len(cmd) == 2):
        print(f'Error get request for {cmd[1]} failed. File is not present on server side...')

def error_unknown_request(cmd: list[str]):
    cmd = ' '.join(cmd)
    print(f'Command: {cmd} is not supported.')

def unsuccessful_change(cmd):
    if (len(cmd) == 3):
        print(f'Error changing {cmd[1]} to {cmd[2]}.')

def help_response(res):
    help_msg = res[10:]
    bin_to_int = int(help_msg, 2)
    help_msg = binascii.unhexlify('%x' % bin_to_int).decode('ascii')
    print(help_msg)

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
                    if (DEBUG_MODE):
                        print(f'Debug - Request message being sent: {req}')

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
                if (DEBUG_MODE):
                    print(f'Debug - Response message received: {res}')
                    
                last_bit_of_res, file_size_bits, filename, is_get = decode_response(res, cmd)

                if (is_get):
                    file_data = ''
                    # Incase some data was passed with response
                    if (len(res) > last_bit_of_res):
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
                    
                    if (exists(f'{CLIENT_FILES_PATH}/{filename}')):
                        print(f'{filename} has been downloaded successfully.')

            print('\nClosing client socket...')
        except KeyboardInterrupt:
            print('\nClosing socket due to keyboard interrupt...')
        except Exception as e:
            print('\nClosing socket due to exception: ' + e)


# Main program execution
if __name__ == '__main__':

    for i, arg in enumerate(sys.argv):
        print(arg)
        if i == 1:
            HOSTNAME = str(arg)
        elif i == 2:
            PORT = int(arg)
        elif i == 3:
            DEBUG_MODE = int(arg)
        elif i == 4:
            DEV_MODE = int(arg)

    # Start client
    print(f'Hostname and port accepted... attempting to connect client to port {PORT}\n')
    run_client()

    # Terminate program
    print('Exiting program...\n')
