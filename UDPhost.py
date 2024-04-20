import threading
import os
from connection import *
from logger import init_logger

def main():
    bind_ip, bind_port = input("Bind address: <ip:port>: ").strip().split(":")
    connection = UDPConnection((bind_ip, int(bind_port)))
    init_logger(f"{connection.log_dir}/communication.log")
    recv_thread = threading.Thread(
        target=receive, 
        args=(connection,), 
        daemon = True
    )
    recv_thread.start()

    while True:
        message = input("$ ")
        if message.lower() == "exit":
            break
        elif message.lower() == "info":
            connection.info()
        elif message.lower() == "target":
            addr = input("<ip:port>: ").strip().split(":")
            target_addr = (addr[0], int(addr[1]))
            connection.target_addr = target_addr
        elif message.lower() == "sendfile" or message.lower() == "sf":
            if connection.target_addr is None:
                print("\rTarget address required. Use `target` command. ")
                continue
            file_path = input("<file_path>: ").strip()
            if os.path.exists(file_path):
                threading.Thread(
                    target=send_file_gbn,
                    args=(connection, file_path),
                    daemon=True
                ).start()
            else:
                print("\rFile not found. ")
        else:
            if connection.target_addr is None:
                print("\rTarget address required. Use `target` command. ")
                continue
            threading.Thread(
                target=send_message, 
                args=(connection, message),
                daemon=True
            ).start()

    connection.running = False
    recv_thread.join()
    connection.sock.close()

if __name__ == "__main__":
    main()

# my window addr 
# 192.168.10.1:42477
# my linux addr
# 192.168.10.129:42477