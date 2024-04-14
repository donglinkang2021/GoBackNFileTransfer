# Linux 虚拟机（服务器端）

import socket
import threading

host = '0.0.0.0'
port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
print("服务器已启动，等待通信...")

addr_set = set()

def receive_messages():
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"\r{addr}: {data.decode()} \n$ ", end="")
        addr_set.add(addr)

def main():
    recv_thread = threading.Thread(target=receive_messages)
    recv_thread.daemon = True
    recv_thread.start()

    while True:
        message = input("$ ")
        for addr in addr_set:
            sock.sendto(message.encode(), addr)

if __name__ == "__main__":
    main()
