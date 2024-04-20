import threading
import socket
import os
from connection import UDPConnection, receive, send_message, send_file_gbn
from logger import init_logger
from typing import Tuple
from utils import addr_to_str

class UDPhost:
    def __init__(self, bind_addr:Tuple[str, int]):
        assert bind_addr is not None, "Bind address is required."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind_addr)
        # for logging
        self.log_dir = addr_to_str(bind_addr)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        init_logger(f"{self.log_dir}/communication.log")
        self.connection = None
        self.addr_map = {}
        self.is_broadcasting = False

    def broadcast(self):
        self.is_broadcasting = True

    def add_target(self, target_addr:Tuple[str, int]):
        self.connection = UDPConnection(self.sock, target_addr, self.log_dir)
        self.recv_thread = threading.Thread(
            target=receive, 
            args=(self.connection,), 
            daemon = True
        )
        self.recv_thread.start()
        self.addr_map[target_addr] = {
            "connection": self.connection, 
            "recv_thread": self.recv_thread
        }

    def send(self, message):
        if self.is_broadcasting:
            for addr, info in self.addr_map.items():
                connection = info["connection"]
                threading.Thread(
                    target=send_message,
                    args=(connection, message),
                    daemon=True
                ).start()
        else:
            threading.Thread(
                target=send_message, 
                args=(self.connection, message),
                daemon=True
            ).start()

    def send_file(self, file_path):
        if os.path.exists(file_path):
            if self.is_broadcasting:
                for addr, info in self.addr_map.items():
                    connection = info["connection"]
                    threading.Thread(
                        target=send_file_gbn,
                        args=(connection, file_path),
                        daemon=True
                    ).start()
            else:
                threading.Thread(
                    target=send_file_gbn,
                    args=(self.connection, file_path),
                    daemon=True
                ).start()
        else:
            print("\rFile not found. ")


    def info(self):
        print(f"\rHost address: {self.sock.getsockname()}")
        print(f"\rTarget address: {self.connection}")
        print("\rBroadcasting: ", self.is_broadcasting)
        print("\rTarget list: ")
        for addr, info in self.addr_map.items():
            info["connection"].info()

    def exit(self):
        for addr, info in self.addr_map.items():
            info["connection"].running = False
            info["recv_thread"].join()
        self.sock.close()

def main():
    bind_ip, bind_port = input("Bind address: <ip:port>: ").strip().split(":")
    udp_host = UDPhost((bind_ip, int(bind_port)))
    while True:
        message = input("$ ")
        if message.lower() == "exit":
            break
        elif message.lower() == "info":
            udp_host.info()
        elif message.lower() == "broadcast":
            udp_host.broadcast()
        elif message.lower() == "target":
            addr = input("<ip:port>: ").strip().split(":")
            udp_host.add_target((addr[0], int(addr[1])))
        elif message.lower() == "sendfile" or message.lower() == "sf":
            if udp_host.connection is None:
                print("\rTarget address required. Use `target` command. ")
                continue
            file_path = input("<file_path>: ").strip()
            udp_host.send_file(file_path)
        else:
            if udp_host.connection is None:
                print("\rTarget address required. Use `target` command. ")
                continue
            udp_host.send(message)
    udp_host.exit()

if __name__ == "__main__":
    main()

# my window addr 
# 192.168.10.1:42477
# my linux addr
# 192.168.10.129:42477