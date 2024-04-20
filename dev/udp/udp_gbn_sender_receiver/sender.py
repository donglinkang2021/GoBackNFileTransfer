import socket
import threading
import os
from typing import Tuple
from pdu import PDU, PacketType
from config import *
from logger import *
from tqdm import tqdm
import time
import random

random.seed(1337)

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

        self.send_window = []  # list of send_no of PDUs to send
        self.window_left = 0
        self.window_right = 0

    def info(self):
        print(f"send_no: {self.send_no}")
        print(f"recv_ack_no: {self.recv_ack_no}")
        print(f"recv_no: {self.recv_no}")
        print(f"send_ack_no: {self.send_ack_no}")

    def loop_no(self, step:int):
        return (step - INIT_SEQ_NO) % MAX_SEQ_LEN + INIT_SEQ_NO

    def send_pdu(self, pdu_type:PacketType, data:bytes, frame_no:int=None, ack_no:int=None):
        frame_no = self.send_no if frame_no is None else frame_no
        ack_no = self.recv_ack_no if ack_no is None else ack_no
        pdu = PDU(frame_no, ack_no, data, pdu_type)
        packed_data = pdu.pack()
        if random.random() < ERROR_RATE / 100:
            packed_data = packed_data[:5] + ERROR_DATA + packed_data[6:]
        if random.random() >= LOST_RATE / 100:
            self.sock.sendto(packed_data, self.receiver_addr)

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
                    sender.recv_ack_no = pdu.ack_no
                elif pdu.ack_no < sender.send_no:
                    log_recv(pdu.frame_no, pdu.ack_no, PacketType.ACK, 0, LogStatus.RT)
                    sender.recv_ack_no = max(sender.recv_ack_no, pdu.ack_no)
                else:
                    log_recv(pdu.frame_no, pdu.ack_no, PacketType.ACK, 0, LogStatus.DAE)
            elif pdu.pdu_type == PacketType.FILE:
                pass
            else:
                print("\rUnknown PDU type. \n$ ", end="")
        except socket.timeout:
            continue

def send_packet(sender:UDPSender, data:bytes, pdu_type:PacketType=PacketType.MESSAGE):
    sender.send_pdu(pdu_type, data)
    log_send(sender.send_no, sender.recv_ack_no, 
             pdu_type, len(data), LogStatus.NEW)
    sender.send_no = sender.loop_no(sender.send_no + 1)
    time.sleep(RT_TIMEOUT)
    while sender.send_no != sender.recv_ack_no:
        sender.send_no = sender.loop_no(sender.send_no - 1)
        sender.send_pdu(pdu_type, data)
        log_send(sender.send_no, sender.recv_ack_no, 
                 pdu_type, len(data), LogStatus.TO)
        sender.send_no = sender.loop_no(sender.send_no + 1)
        time.sleep(RT_TIMEOUT)

def send_message(sender:UDPSender, message:str):
    send_packet(sender, message.encode(), PacketType.MESSAGE)

def send_file_gbn(sender:UDPSender, file_path:str):
    # send file name and size first
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    header = f"{file_name}{SEP}{file_size}".encode()
    send_packet(sender, header, PacketType.FILE)
    
    pbar = tqdm(total=file_size, unit="B", unit_scale=True)
    with open(file_path, "rb") as file:
        data = file.read()

    n_data = len(data)
    num_frames = (n_data + DATA_SIZE - 1) // DATA_SIZE
    while sender.window_left < num_frames:
        while sender.window_right < min(sender.window_left + SW_SIZE, num_frames):
            start = sender.window_right * DATA_SIZE
            end = min(start + DATA_SIZE, n_data)
            rel_step = sender.window_right - sender.window_left
            if  rel_step < len(sender.send_window):
                sender.send_pdu(
                    PacketType.FILE, 
                    data[start:end], 
                    sender.send_window[rel_step]
                )
                log_send(sender.send_window[rel_step], sender.recv_ack_no,
                         PacketType.FILE, end - start, LogStatus.TO)
            else:
                sender.send_pdu(PacketType.FILE, data[start:end])
                log_send(sender.send_no, sender.recv_ack_no,
                        PacketType.FILE, end - start, LogStatus.NEW)
                sender.send_window.append(sender.send_no)
                sender.send_no = sender.loop_no(sender.send_no + 1)
            sender.window_right += 1

        time.sleep(RT_TIMEOUT)

        if sender.send_no == sender.recv_ack_no:
            sender.window_left = sender.window_right
            pbar.update(len(sender.send_window) * DATA_SIZE)
            sender.send_window.clear()
        else: 
            num_frame_sent = sender.send_window.index(sender.recv_ack_no)
            sender.window_left += num_frame_sent
            # Go Back N
            sender.window_right = sender.window_left
            sender.send_window = sender.send_window[num_frame_sent:]
            pbar.update(num_frame_sent * DATA_SIZE)

    pbar.set_description("File sent")
    pbar.close()
    print("\r$ ", end="")
    sender.window_left = 0
    sender.window_right = 0
    sender.send_window.clear()

def send_file_sw(sender:UDPSender, file_path:str):
    # stop and wait
    # send file name and size first
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    header = f"{file_name}{SEP}{file_size}".encode()
    send_packet(sender, header, PacketType.FILE)
    
    pbar = tqdm(total=file_size, unit="B", unit_scale=True)
    with open(file_path, "rb") as file:
        data = file.read()

    n_data = len(data)
    num_frames = (n_data + DATA_SIZE - 1) // DATA_SIZE
    for num_frame in range(num_frames):
        start = num_frame * DATA_SIZE
        end = min(start + DATA_SIZE, n_data)
        send_packet(sender, data[start:end], PacketType.FILE)
        pbar.update(end - start)

    pbar.set_description("File sent")
    pbar.close()
    print("\r$ ", end="")

def main():
    init_logger("sender.log")
    sender = UDPSender(('192.168.10.129', UDP_PORT))
    print(f"Receiver address: {sender.receiver_addr} ")
    recv_thread = threading.Thread(
        target=receive, 
        args=(sender,), 
        daemon = True
    )
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
                    target=send_file_gbn,
                    args=(sender, file_path),
                    daemon=True
                ).start()
            else:
                print("File does not exist.")
        else:
            threading.Thread(
                target=send_message, 
                args=(sender, message),
                daemon=True
            ).start()

    sender.running = False
    recv_thread.join()
    sender.sock.close()

if __name__ == "__main__":
    main()


"""
SWS 6:
<file_path>: file_examples\miziha_running.png        
Sending miziha_running.png (3324832 bytes) ... 
File sent: : 3.32MB [06:49, 8.12kB/s]

SWS 50:
<file_path>: file_examples\miziha_running.png
Sending miziha_running.png (3324832 bytes) ...
File sent: : 3.32MB [01:08, 48.8kB/s]

SWS 99:
<file_path>: file_examples\miziha_running.png
Sending miziha_running.png (3324832 bytes) ...
File sent: : 3.32MB [00:36, 92.1kB/s]


pdu lost 10%:
$ sf
<file_path>: file_examples\miziha_running.png
File sent: : 3.32MB [07:28, 7.42kB/s]

pdu err 10%:
$ sf
<file_path>: file_examples\miziha_running.png
File sent: : 3.32MB [07:29, 7.40kB/s]

pdu lost 10% and err 10%:
$ sf
<file_path>: file_examples\1_chpt1_Introduction-2024.pdf
File sent: : 4.91MB [21:08, 3.87kB/s]

pdu lost 10% and err 10%:
$ sf
<file_path>: file_examples\miziha_running.png
File sent: : 3.32MB [03:49, 14.5kB/s]
"""