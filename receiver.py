import socket
import threading
import os
from typing import Tuple
from pdu import PDU, PacketType
from config import BUF_SIZE, SK_TIMEOUT, INIT_SEQ_NO, MAX_SEQ_LEN, RT_TIMEOUT, DATA_SIZE, SW_SIZE, SEP
from tqdm import tqdm

class UDPReceiver:
    def __init__(self, addr:Tuple[str, int], recv_dir:str="received"):
        self.addr = addr

        self.send_no = INIT_SEQ_NO
        self.ack_no = INIT_SEQ_NO
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

    def init_file_transfer(self, file_name:str, file_size:int):
        print(f"\rReceiving file: {file_name} ({file_size} bytes) ...")
        self.pbar = tqdm(total=file_size, unit="B", unit_scale=True)
        if not os.path.exists(self.recv_dir):
            os.makedirs(self.recv_dir)
        self.file_path = os.path.join("received", file_name)
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self.file_size = file_size

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
        pdu = PDU(self.send_no, self.ack_no, data, pdu_type)
        self.sock.sendto(pdu.pack(), self.target_addr)

    def recv_pdu(self):
        data, addr = self.sock.recvfrom(BUF_SIZE)
        pdu = PDU.unpack(data)
        return pdu, addr

def receive_file_pdu(receiver:UDPReceiver, pdu:PDU):
    if not receiver.file_transfer:
        receiver.file_transfer = True
        file_header = pdu.data.decode().split(SEP)
        receiver.init_file_transfer(file_header[0], int(file_header[1]))
    else:
        with open(receiver.file_path, "ab") as file:
            file.write(pdu.data)
        receiver.pbar.update(pdu.data_size)
        receiver.file_size -= pdu.data_size
        if receiver.file_size == 0:
            receiver.finish_file_transfer()

def receive(receiver:UDPReceiver):
    while receiver.running:
        try:
            receiver.sock.settimeout(SK_TIMEOUT)
            pdu, addr = receiver.recv_pdu()
            if receiver.target_addr != addr:
                print(f"\rTarget address added: {addr} \n$ ", end="")
                receiver.target_addr = addr
                receiver.target_addrs.add(addr)
            if pdu.pdu_type == PacketType.MESSAGE:
                print(f"\r{addr}: {pdu.data.decode()} \n$ ", end="")
            elif pdu.pdu_type == PacketType.ACK:
                pass
            elif pdu.pdu_type == PacketType.FILE:
                receive_file_pdu(receiver, pdu)
            else:
                print("\rUnknown PDU type. \n$ ", end="")
        except socket.timeout:
            continue

def send_message(sender:UDPReceiver, message:str):
    sender.send_pdu(PacketType.MESSAGE, message.encode())

def main():
    receiver = UDPReceiver(('192.168.10.129', 42477))
    recv_thread = threading.Thread(target=receive, args=(receiver,))
    recv_thread.daemon = True
    recv_thread.start()

    while True:
        message = input("$ ")
        if message.lower() == "exit":
            break
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
