import socket
import threading
import os
from typing import Tuple
from pdu import PDU, PacketType
from config import *
from logger import *
from tqdm import tqdm
import time

class UDPReceiver:
    def __init__(self, addr:Tuple[str, int], recv_dir:str="received"):
        self.addr = addr

        # as sender
        self.send_no = INIT_SEQ_NO      # pdu_to_send: sender's send no
        self.recv_ack_no = INIT_SEQ_NO  # acked_no: sender's expected no

        # as receiver
        self.recv_no = INIT_SEQ_NO      # pdu_exp: receiver's expected no
        self.send_ack_no = INIT_SEQ_NO  # pdu_recv: receiver's send ack no
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)
        self.running = True

        self.target_addr = None
        self.target_addrs = set()

        self.recv_dir = recv_dir
        self.file_transfer = False
        self.pbar = None
        self.file_path = None
        self.file_size = 0

    def info(self):
        print(f"send_no: {self.send_no}")
        print(f"recv_ack_no: {self.recv_ack_no}")
        print(f"recv_no: {self.recv_no}")
        print(f"send_ack_no: {self.send_ack_no}")

    def init_file_transfer(self, file_name:str, file_size:int):
        print(f"\rReceiving file: {file_name} ({file_size} bytes) ...")
        self.pbar = tqdm(total=file_size, unit="B", unit_scale=True)
        if not os.path.exists(self.recv_dir):
            os.makedirs(self.recv_dir)
        self.file_path = os.path.join("received", file_name)
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self.file_size = file_size
        self.file_transfer = True

    def finish_file_transfer(self):
        self.pbar.set_description(f"File received")
        self.pbar.close()
        print(f"\r<file_path>: {self.file_path} \n$ ", end="")
        self.pbar = None
        self.file_path = None
        self.file_transfer = False

    def loop_no(self, step:int):
        return (step - INIT_SEQ_NO) % MAX_SEQ_LEN + INIT_SEQ_NO

    def send_pdu(self, pdu_type:PacketType, data:bytes):
        pdu = PDU(self.send_no, self.recv_ack_no, data, pdu_type)
        self.sock.sendto(pdu.pack(), self.target_addr)

    def send_ack(self):
        pdu = PDU(self.send_ack_no, self.recv_no, b"", PacketType.ACK)
        self.sock.sendto(pdu.pack(), self.target_addr) 

    def recv_pdu(self):
        data, addr = self.sock.recvfrom(BUF_SIZE)
        pdu = PDU.unpack(data)
        return pdu, addr

def receive_file(receiver:UDPReceiver, pdu:PDU):
    if not receiver.file_transfer:
        file_header = pdu.data.decode().split(SEP)
        receiver.init_file_transfer(file_header[0], int(file_header[1]))
    else:
        with open(receiver.file_path, "ab") as file:
            file.write(pdu.data)
        receiver.pbar.update(pdu.data_size)
        receiver.file_size -= pdu.data_size
        if receiver.file_size == 0:
            receiver.finish_file_transfer()

def receive_msg(receiver:UDPReceiver, pdu:PDU):
    print(f"\r{receiver.target_addr}: {pdu.data.decode()} \n$ ", end="")

def receive_packet(receiver:UDPReceiver, pdu:PDU):
    if pdu.frame_no == receiver.recv_no:
        if pdu.is_corrupted():
            log_recv(receiver.send_ack_no, receiver.recv_no, 
                    pdu.pdu_type, pdu.data_size, LogStatus.DAE)
        else:
            if pdu.pdu_type == PacketType.MESSAGE:
                receive_msg(receiver, pdu)
            elif pdu.pdu_type == PacketType.FILE:
                receive_file(receiver, pdu)
            else:
                log_recv(receiver.send_ack_no, receiver.recv_no, 
                        pdu.pdu_type, pdu.data_size, LogStatus.DAE)
            log_recv(receiver.send_ack_no, receiver.recv_no, 
                    pdu.pdu_type, pdu.data_size, LogStatus.OK)
            receiver.recv_no = receiver.loop_no(receiver.recv_no + 1)
            receiver.send_ack()
            log_send(receiver.send_ack_no, receiver.recv_no,
                    PacketType.ACK, 0, LogStatus.NEW)
            receiver.send_ack_no = receiver.loop_no(receiver.send_ack_no + 1)
    elif pdu.frame_no < receiver.recv_no:
        receiver.send_ack()
        log_send(receiver.send_ack_no, receiver.recv_no,
                PacketType.ACK, 0, LogStatus.NEW)
    else:
        receiver.send_ack()
        log_send(receiver.send_ack_no, receiver.recv_no,
                PacketType.ACK, 0, LogStatus.NEW)
        log_recv(pdu.frame_no, pdu.ack_no, 
                pdu.pdu_type, pdu.data_size, LogStatus.NOE)

def receive(receiver:UDPReceiver):
    while receiver.running:
        try:
            receiver.sock.settimeout(SK_TIMEOUT)
            pdu, addr = receiver.recv_pdu()
            if receiver.target_addr != addr:
                print(f"\rTarget address added: {addr} \n$ ", end="")
                receiver.target_addr = addr
                receiver.target_addrs.add(addr)
            if pdu == None:
                log_recv(receiver.send_ack_no, receiver.recv_no, 
                    PacketType.UNKNOWN, 0, LogStatus.DAE)
                continue
            if pdu.pdu_type == PacketType.MESSAGE or pdu.pdu_type == PacketType.FILE:
                receive_packet(receiver, pdu)
            elif pdu.pdu_type == PacketType.ACK:
                if pdu.ack_no == receiver.send_no:
                    log_recv(pdu.frame_no, pdu.ack_no, 
                             PacketType.ACK, 0, LogStatus.OK)
                    receiver.recv_ack_no = receiver.loop_no(receiver.recv_ack_no + 1)
        except socket.timeout:
            continue

def send_message(receiver:UDPReceiver, message:str):
    receiver.send_pdu(PacketType.MESSAGE, message.encode())
    log_send(receiver.send_no, receiver.recv_ack_no, 
             PacketType.MESSAGE, len(message), LogStatus.NEW)
    receiver.send_no = receiver.loop_no(receiver.send_no + 1)
    time.sleep(RT_TIMEOUT)
    while receiver.send_no != receiver.recv_ack_no:
        receiver.send_no = receiver.loop_no(receiver.send_no - 1)
        receiver.send_pdu(PacketType.MESSAGE, message.encode())
        log_send(receiver.send_no, receiver.recv_ack_no, 
                 PacketType.MESSAGE, len(message), LogStatus.TO)
        receiver.send_no = receiver.loop_no(receiver.send_no + 1)
        time.sleep(RT_TIMEOUT)

def main():
    init_logger("receiver.log")
    receiver = UDPReceiver(('192.168.10.129', UDP_PORT))
    recv_thread = threading.Thread(target=receive, args=(receiver,))
    recv_thread.daemon = True
    recv_thread.start()

    while True:
        message = input("$ ")
        if message.lower() == "exit":
            break
        elif message.lower() == "info":
            receiver.info()
        else:
            if receiver.target_addr is not None:
                threading.Thread(
                    target=send_message, 
                    args=(receiver, message)
                ).start()
            else:
                print("\rNo target address. ")

    receiver.running = False
    recv_thread.join()
    receiver.sock.close()

if __name__ == "__main__":
    main()

"""
SWS 6:
Receiving file: miziha_running.png (3324832 bytes) ...
File received: 100%|██████████████████████████████████| 3.32M/3.32M [06:48<00:00, 8.14kB/s]
<file_path>: received/miziha_running.png 

SWS 50:
Receiving file: miziha_running.png (3324832 bytes) ...
File received: 100%|██████████████████████████████████| 3.32M/3.32M [01:07<00:00, 49.4kB/s]
<file_path>: received/miziha_running.png 

SWS 99:
Receiving file: miziha_running.png (3324832 bytes) ...
File received: 100%|██████████████████████████████████| 3.32M/3.32M [00:35<00:00, 94.4kB/s]
<file_path>: received/miziha_running.png 

pdu lost 10%:
Receiving file: miziha_running.png (3324832 bytes) ...
File received: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████| 3.32M/3.32M [07:28<00:00, 7.42kB/s]
<file_path>: received/miziha_running.png 

pdu err 10%:
Receiving file: miziha_running.png (3324832 bytes) ...
File received: 100%|████████████████████████████████████████████████████████████████████████████████████| 3.32M/3.32M [07:29<00:00, 7.40kB/s]
<file_path>: received/miziha_running.png 

pdu lost 10% and err 10%:
Target address added: ('192.168.10.1', 52109) 
Receiving file: 1_chpt1_Introduction-2024.pdf (4914113 bytes) ...
File received: 100%|████████████████████████████████████████████████████████████████████████████████████| 4.91M/4.91M [21:08<00:00, 3.87kB/s]
<file_path>: received/1_chpt1_Introduction-2024.pdf 
"""