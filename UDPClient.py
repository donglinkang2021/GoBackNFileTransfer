import socket
import threading
from pdu import PDU
from config import BUF_SIZE, SK_TIMEOUT, INIT_SEQ_NO, MAX_SEQ_LEN
from typing import Tuple

def step1():
    print("UDP Client")
    print("Commands:")
    print("  addr: Add a new address")
    print("  clear: Clear address list")
    print("  exit: Exit the program")
    print("  list/ls: List all addresses")
    print("  host: Display host IP address")
    print("  bind: Bind to a new address")
    print("  unicast/uni: Set unicast mode")
    print("  broadcast/bro: Set broadcast mode")
    print("  sendfile/sf: Send a file")
    print("  <message>: Send a message to all addresses")
    print("  <message> <ip:port>: Send a message to a specific address")
    print("")

step1()


class UDPClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr_set = set()
        self.running = True
        self.target_addr = " "

        self.send_no = INIT_SEQ_NO # send frame number
        self.recv_no = INIT_SEQ_NO # receive frame number
        self.ack_no = INIT_SEQ_NO # ack frame number

    def send_pdu(self, data:bytes, addr:Tuple[str, int]):
        pdu = PDU(self.send_no, self.ack_no, data)
        self.sock.sendto(pdu.pack(), addr)
        self.send_no = self._step_no(self.send_no + 1)

    def _step_no(self, step:int):
        return (step - INIT_SEQ_NO) % MAX_SEQ_LEN + INIT_SEQ_NO

    def send_ack(self, ack_no:int, addr:Tuple[str, int]):
        pdu = PDU(self.send_no, ack_no, b'')
        self.sock.sendto(pdu.pack(), addr)
    
    def receive_pdu(self):
        data, addr = self.sock.recvfrom(BUF_SIZE)
        self.addr_set.add(addr)
        pdu = PDU.unpack(data)
        return pdu, addr
    
client = UDPClient()

def receive_messages():
    while client.running:
        try:
            client.sock.settimeout(SK_TIMEOUT)
            pdu, addr = client.receive_pdu()

            # check if the pdu is corrupted
            if pdu.is_corrupted():
                print(f"\r Corrupted PDU from {addr} received. \n${client.target_addr} ", end="")
                continue
            
            # receive an ack packet and update ack number
            if pdu.data == b'':
                print(f"\r{addr}: ACK {pdu.ack_no} received. \n${client.target_addr} ", end="")
                if pdu.ack_no == client.send_no:
                    client.ack_no = client._step_no(client.ack_no + 1)
                continue

            # receive data packet and send ack
            if pdu.frame_no == client.recv_no:
                client.recv_no = client._step_no(client.recv_no + 1)
                client.send_ack(pdu.frame_no, addr)
            elif pdu.frame_no < client.recv_no:
                client.send_ack(client.recv_no, addr)

            print(f"\r{addr}: {pdu.data.decode()} \n${client.target_addr} ", end="")
            client.addr_set.add(addr)
        except socket.timeout:
            continue

recv_thread = threading.Thread(target=receive_messages)
recv_thread.daemon = True
recv_thread.start()

while True:
    message = input(f"${client.target_addr} ")
    if message.lower() == "addr":
        addr = input("<ip:port>: ").strip().split(":")
        client.addr_set.add((addr[0], int(addr[1])))
    elif message.lower() == "clear":
        client.addr_set.clear()
    elif message.lower() == "exit":
        break
    elif message.lower() == "list" or message.lower() == "ls":
        print(client.addr_set)
    elif message.lower() == "host":
        print(socket.gethostbyname(socket.gethostname()))
    elif message.lower() == "bind":
        host, port = input("<ip:port>: ").strip().split(":")
        client.sock.bind((host, int(port)))
    elif message.lower() == "unicast" or message.lower() == "uni":
        client.target_addr = input("<ip:port>: ").strip()
    elif message.lower() == "broadcast" or message.lower() == "bro":
        client.target_addr = " "
    elif message.lower() == "sendfile" or message.lower() == "sf":
        pass
    elif message == "":
        continue
    else:
        if client.target_addr != " ":
            host, port = client.target_addr.split(":")
            client.send_pdu(message.encode(),  (host, int(port)))
        else:
            for addr in client.addr_set:
                client.send_pdu(message.encode(), addr)

client.running = False
recv_thread.join()
client.sock.close()
print("Host is stopped")

"""
192.168.10.1:42477
"""