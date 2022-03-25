# COEN 366 File Transfer Protocol Project

The goal of this project is to design a client-server network application that can be used to simulate the file-transfer protocol operations.
This program should support 5 basic commands: get, put, change, help, and bye

### Command descriptions:

- put: Copy a file from the client side to the server side
- get: Copy a file from the server side to the client side
- change: Change the name of a file on the server side
- help: Print the list of commands
- bye: Terminate the client

### Running the program:
No files that are not included in the default python library are included in this project, so no need to set up a users environment

1. Starting the server
	Open a new terminal
	The terminal command to run the server is formatted as such: `python server.py hostname port debug_mode`
	To run the server type into the terminal: `pythn server.py localhost 80 1`

2. Starting the client
	Open a second terminal
	The terminal command to run the client is formatted as such: `python client.py hostname port debug_mode`
	To run the client type into the terminal: `pythn client.py localhost 80 1`

3. Entering commands
	Commands will be accepted one by one. The client will prompt the user to enter a command ex: `put test.txt`
	The command will be processed and the operation, if the command is accepted, will be executed.
	The user can verify file transfers and name changes have executed by looking in the appropiate folders
	`client_files` for client sided files
	`server_files` for server sided files	

4. Exiting the client
	To exit the client either use a keyboard interrupt (ctrl+c) or type in the command `bye`

5. Exiting the server
	To exit the server, close the terminal