#----- A simple TCP client program in Python using send() function -----

import socket

 

# Create a client socket

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

 

# Connect to the server

clientSocket.connect(("127.0.0.1",4242))

 

# Send data to server

data = "get_xy"

#clientSocket.send(data.encode())
#clientSocket.send(b'get_xy')
clientSocket.sendall('get_xy')
 

 
 

# Receive data from server

dataFromServer = clientSocket.recv(1024)

 

# Print to the console

print(dataFromServer.decode())
