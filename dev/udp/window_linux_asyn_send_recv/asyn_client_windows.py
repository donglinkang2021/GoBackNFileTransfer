# Windows 主机（客户端）
import socket
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("客户端已启动，等待通信...")

server_host = '192.168.10.129'
server_port = 12345           
server_addr = (server_host, server_port)

def receive_messages():
    while True:
        try:
            sock.settimeout(1.0)
            data, addr = sock.recvfrom(1024)
            print(f"\r{addr}: {data.decode()} \n$ ", end="")
        except socket.timeout:
            continue

def main():
    recv_thread = threading.Thread(target=receive_messages)
    recv_thread.daemon = True 
    recv_thread.start()

    while True:
        message = input("$ ")
        
        sock.sendto(message.encode(), server_addr)

        if message.lower() == "exit":
            break

if __name__ == "__main__":
    main()
