import socket
import threading
from config import BUF_SIZE, SK_TIMEOUT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Host is running")

addr_set = set()
target_addr = " "

running = True

def receive_messages():
    global running
    while running:
        try:
            sock.settimeout(SK_TIMEOUT)
            data, addr = sock.recvfrom(BUF_SIZE)
            print(f"\r{addr}: {data.decode()} \n${target_addr} ", end="")
            addr_set.add(addr)
        except socket.timeout:
            continue


recv_thread = threading.Thread(target=receive_messages)
recv_thread.daemon = True
recv_thread.start()

while True:
    message = input(f"${target_addr} ")
    if message.lower() == "addr":
        addr = input("<ip:port>: ").strip().split(":")
        addr_set.add((addr[0], int(addr[1])))
    elif message.lower() == "clear":
        addr_set.clear()
    elif message.lower() == "exit":
        break
    elif message.lower() == "list" or message.lower() == "ls":
        print(addr_set)
    elif message.lower() == "host":
        print(socket.gethostbyname(socket.gethostname()))
    elif message.lower() == "bind":
        host, port = input("<ip:port>: ").strip().split(":")
        sock.bind((host, int(port)))
    elif message.lower() == "unicast" or message.lower() == "uni":
        target_addr = input("<ip:port>: ").strip()
    elif message.lower() == "broadcast" or message.lower() == "bro":
        target_addr = " "
    elif message.lower() == "sendfile" or message.lower() == "sf":
        pass
    else:
        if target_addr != " ":
            host, port = target_addr.split(":")
            sock.sendto(message.encode(),  (host, int(port)))
        else:
            for addr in addr_set:
                sock.sendto(message.encode(), addr) 

running = False
recv_thread.join()
sock.close()
print("Host is stopped")

"""
if you want to connect 2 host
1. host 1
    bind
    192.168.10.1:42477
2. host 2
    addr
    192.168.10.1:42477
    hello
at this time, host 1 will receive the message "hello" and record the address of host 2
"""