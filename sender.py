import socket
import threading
import os
from typing import Tuple
from pdu import PDU, PacketType
from config import BUF_SIZE, SK_TIMEOUT, INIT_SEQ_NO, MAX_SEQ_LEN, RT_TIMEOUT, DATA_SIZE, SW_SIZE, SEP
from tqdm import tqdm
from logger import LogStatus, init_logger, log_send, log_recv
import time

class UDPSender:
    def __init__(self, receiver_addr:Tuple[str, int]):
        self.receiver_addr = receiver_addr

        # as sender
        self.send_no = INIT_SEQ_NO      # pdu_to_send: sender's send no
        self.recv_ack_no = INIT_SEQ_NO  # acked_no: sender's expected no

        # as receiver
        self.recv_no = INIT_SEQ_NO      # pdu_exp: receiver's expected no
        self.send_ack_no = INIT_SEQ_NO  # pdu_recv: receiver's send ack no

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.timeout_retransmit = False

    def info(self):
        print(f"send_no: {self.send_no}")
        print(f"recv_ack_no: {self.recv_ack_no}")
        print(f"recv_no: {self.recv_no}")
        print(f"send_ack_no: {self.send_ack_no}")

    def loop_no(self, step:int):
        return (step - INIT_SEQ_NO) % MAX_SEQ_LEN + INIT_SEQ_NO

    def send_pdu(self, pdu_type:PacketType, data:bytes):
        pdu = PDU(self.send_no, self.recv_ack_no, data, pdu_type)
        self.sock.sendto(pdu.pack(), self.receiver_addr)

    def send_ack(self):
        pdu = PDU(self.send_ack_no, self.recv_no, b"", PacketType.ACK)
        self.sock.sendto(pdu.pack(), self.receiver_addr) 

    def recv_pdu(self):
        data, addr = self.sock.recvfrom(BUF_SIZE)
        pdu = PDU.unpack(data)
        return pdu, addr

def receive_msg_pdu(sender:UDPSender, pdu:PDU):
    if pdu.frame_no == sender.recv_no:
        if pdu.is_corrupted():
            log_recv(sender.send_ack_no, sender.recv_no, 
                    PacketType.MESSAGE, pdu.data_size, LogStatus.DAE)
        else:
            print(f"\r{sender.receiver_addr}: {pdu.data.decode()} \n$ ", end="")
            log_recv(sender.send_ack_no, sender.recv_no, 
                    PacketType.MESSAGE, pdu.data_size, LogStatus.OK)
            sender.recv_no = sender.loop_no(sender.recv_no + 1)
            sender.send_ack()
            log_send(sender.send_ack_no, sender.recv_no,
                    PacketType.ACK, 0, LogStatus.NEW)
            sender.send_ack_no = sender.loop_no(sender.send_ack_no + 1)
            
    else:
        log_recv(pdu.frame_no, sender.send_ack_no, 
                PacketType.MESSAGE, pdu.data_size, LogStatus.NOE)
        sender.send_ack()
        log_send(sender.send_ack_no, sender.recv_no,
                PacketType.ACK, 0, LogStatus.NEW)
        sender.send_ack_no = sender.loop_no(sender.send_ack_no + 1)

def receive(sender:UDPSender):
    while sender.running:
        try:
            sender.sock.settimeout(SK_TIMEOUT)
            pdu, addr = sender.recv_pdu()
            if pdu.pdu_type == PacketType.MESSAGE:
                receive_msg_pdu(sender, pdu)
            elif pdu.pdu_type == PacketType.ACK:
                if pdu.ack_no == sender.send_no:
                    log_recv(pdu.frame_no, pdu.ack_no, PacketType.ACK, 0, LogStatus.OK)
                    sender.recv_ack_no = sender.loop_no(sender.recv_ack_no + 1)
            elif pdu.pdu_type == PacketType.FILE:
                pass
            else:
                print("\rUnknown PDU type. \n$ ", end="")
        except socket.timeout:
            continue

def send_message(sender:UDPSender, message:str):
    sender.send_pdu(PacketType.MESSAGE, message.encode())
    log_send(sender.send_no, sender.recv_ack_no, 
             PacketType.MESSAGE, len(message), LogStatus.NEW)
    sender.send_no = sender.loop_no(sender.send_no + 1)
    time.sleep(RT_TIMEOUT)
    while sender.send_no != sender.recv_ack_no:
        sender.send_no = sender.loop_no(sender.send_no - 1)
        sender.send_pdu(PacketType.MESSAGE, message.encode())
        log_send(sender.send_no, sender.recv_ack_no, 
                 PacketType.MESSAGE, len(message), LogStatus.TO)
        sender.send_no = sender.loop_no(sender.send_no + 1)
        time.sleep(RT_TIMEOUT)


def send_file(sender:UDPSender, file_path:str):
    # send file name and size first
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    sender.send_pdu(PacketType.FILE, f"{file_name}{SEP}{file_size}".encode())
    
    print(f"\rSending {file_name} ({file_size} bytes) ...")
    pbar = tqdm(total=file_size, unit="B", unit_scale=True)
    with open(file_path, "rb") as file:
        data = file.read(DATA_SIZE)
        pbar.update(len(data))
        while data:
            sender.send_pdu(PacketType.FILE, data)
            data = file.read(DATA_SIZE)
            pbar.update(len(data))
    pbar.set_description("File sent")
    pbar.close()
    print("\r$ ", end="")

def main():
    init_logger("sender.log")
    sender = UDPSender(('192.168.10.129', 42477))
    print(f"Receiver address: {sender.receiver_addr} ")
    recv_thread = threading.Thread(target=receive, args=(sender,))
    recv_thread.daemon = True 
    recv_thread.start()

    while True:
        message = input("$ ")
        if message.lower() == "exit":
            break
        elif message.lower() == "info":
            sender.info()
        elif message.lower() == "sendfile" or message.lower() == "sf":
            file_path = input("<file_path>: ").strip()
            if os.path.exists(file_path):
                threading.Thread(
                    target=send_file,
                    args=(sender, file_path)
                ).start()
            else:
                print("File does not exist.")
        else:
            threading.Thread(
                target=send_message, 
                args=(sender, message)
            ).start()

    sender.running = False
    recv_thread.join()
    sender.sock.close()

if __name__ == "__main__":
    main()
