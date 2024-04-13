import socket
import os
from tqdm import tqdm

SEPERATOR = "<SEP>"

SERVER_HOST = "192.168.56.1"
SERVER_PORT = 42477

BUFFER_SIZE = 4096 

# create the server socket
server_socket = socket.socket()
server_socket.bind((SERVER_HOST, SERVER_PORT))

# make the server listen to new connections
server_socket.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# accept connection if there is any
client_socket, address = server_socket.accept()
# if below code is executed, that means the sender is connected
print(f"[+] {address} is connected.")

# receive the file infos
# receive using client socket, not server socket
received = client_socket.recv(BUFFER_SIZE).decode()
filename, filesize = received.split(SEPERATOR)

# remove absolute path if there is
filename = os.path.basename(filename)
filesize = int(filesize)

# start receiving the file from the socket
# and writing to the file stream
progress = tqdm(range(filesize), f"Receiving {filename}", unit="B", 
                unit_scale=True, unit_divisor=1024)

with open(filename, "wb") as file:
    while True:
        # read 1024 bytes from the socket (receive)
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            # nothing is received
            # file transmitting is done
            break
        # write to the file the bytes we just received
        file.write(bytes_read)
        # update the progress bar
        progress.update(len(bytes_read))
progress.close()

# close the client socket
client_socket.close()
# close the server socket
server_socket.close()

