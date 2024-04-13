import socket
import os
from tqdm import tqdm

SEPERATOR = "<SEP>"

# get server host 
host = "192.168.10.129"
port = 42477

# buffer for file transfer
BUFFER_SIZE = 4096

# file path
file_path = "file_examples/miziha_running.png"
# get file size
file_size = os.path.getsize(file_path)
print(f"file size: {file_size / 1024 / 1024:.2f} MB")

# creare a socket object
client_socket = socket.socket()
print(f"connecting to {host}:{port}")
client_socket.connect((host, port))
print("connected")

# send the filename and filesize
client_socket.send(f"{file_path}{SEPERATOR}{file_size}".encode())

# start sending the file
progress = tqdm(range(file_size), f"sending {file_path}", unit="B", unit_scale=True, unit_divisor=1024)
with open(file_path, "rb") as file:
    while True:
        # read the bytes from the file
        bytes_read = file.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in busy networks
        client_socket.sendall(bytes_read)

        # update the progress bar
        progress.update(len(bytes_read))
progress.close()
# close the socket
client_socket.close()
print("file has been sent successfully")

