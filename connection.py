import socket
import os
from typing import Tuple
from pdu import PDU, PacketType
from config import *
from logger import log_send, log_recv, LogStatus
from tqdm import tqdm
from utils import addr_to_str
import time
import random

random.seed(1337)

class UDPConnection:
    def __init__(self, bind_addr:Tuple[str, int]=None, target_addr:Tuple[str, int]=None):
        assert bind_addr is not None, "Bind address is required."
        # as sender
        self.send_no = INIT_SEQ_NO      # pdu_to_send: sender's send no
        self.recv_ack_no = INIT_SEQ_NO  # acked_no: sender's expected no

        # as receiver
        self.recv_no = INIT_SEQ_NO      # pdu_exp: receiver's expected no
        self.send_ack_no = INIT_SEQ_NO  # pdu_recv: receiver's send ack no

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind_addr)
        self.running = True
        
        self.target_addr = target_addr

        # for logging
        self.log_dir = addr_to_str(bind_addr)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # send file
        self.send_window = []  # list of send_no of PDUs to send
        self.window_left = 0
        self.window_right = 0

        # recv file
        self.recv_dir = f"{self.log_dir}/received"
        self.file_transfer = False
        self.pbar = None
        self.file_path = None
        self.file_size = 0
        self.file_data = bytes()

    def info(self):
        print(f"target_addr: {self.target_addr}")
        print(f"send_no: {self.send_no}")
        print(f"recv_ack_no: {self.recv_ack_no}")
        print(f"recv_no: {self.recv_no}")
        print(f"send_ack_no: {self.send_ack_no}")
    
    def init_file_transfer(self, file_name:str, file_size:int):
        print(f"\rReceiving file: {file_name} ({file_size} bytes) ...")
        self.pbar = tqdm(total=file_size, unit="B", unit_scale=True)
        if not os.path.exists(self.recv_dir):
            os.makedirs(self.recv_dir)
        self.file_path = os.path.join(self.recv_dir, file_name)
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self.file_size = file_size
        self.file_transfer = True

    def finish_file_transfer(self):
        self.pbar.set_description(f"File received")
        self.pbar.close()
        with open(self.file_path, "wb") as file:
            file.write(self.file_data)
        print(f"\r<file_path>: {self.file_path} \n$ ", end="")
        self.pbar = None
        self.file_path = None
        self.file_transfer = False
        self.file_size = 0
        self.file_data = bytes()

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
            self.sock.sendto(packed_data, self.target_addr)

    def send_ack(self):
        pdu = PDU(self.send_ack_no, self.recv_no, b"", PacketType.ACK)
        self.sock.sendto(pdu.pack(), self.target_addr) 

    def recv_pdu(self):
        data, addr = self.sock.recvfrom(BUF_SIZE)
        pdu = PDU.unpack(data)
        return pdu, addr

def receive_file(connection:UDPConnection, pdu:PDU):
    if not connection.file_transfer:
        file_header = pdu.data.decode().split(SEP)
        connection.init_file_transfer(file_header[0], int(file_header[1]))
    else:
        connection.file_data += pdu.data
        connection.pbar.update(pdu.data_size)
        connection.file_size -= pdu.data_size
        if connection.file_size == 0:
            connection.finish_file_transfer()

def receive_msg(connection:UDPConnection, pdu:PDU):
    print(f"\r{connection.target_addr}: {pdu.data.decode()} \n$ ", end="")

def receive_packet(connection:UDPConnection, pdu:PDU):
    if pdu.frame_no == connection.recv_no:
        if pdu.is_corrupted():
            log_recv(connection.send_ack_no, connection.recv_no, 
                    pdu.pdu_type, pdu.data_size, LogStatus.DAE)
        else:
            if pdu.pdu_type == PacketType.MESSAGE:
                receive_msg(connection, pdu)
            elif pdu.pdu_type == PacketType.FILE:
                receive_file(connection, pdu)
            else:
                log_recv(connection.send_ack_no, connection.recv_no, 
                        pdu.pdu_type, pdu.data_size, LogStatus.DAE)
            log_recv(connection.send_ack_no, connection.recv_no, 
                    pdu.pdu_type, pdu.data_size, LogStatus.OK)
            connection.recv_no = connection.loop_no(connection.recv_no + 1)
            connection.send_ack()
            log_send(connection.send_ack_no, connection.recv_no,
                    PacketType.ACK, 0, LogStatus.NEW)
            connection.send_ack_no = connection.loop_no(connection.send_ack_no + 1)
    elif pdu.frame_no < connection.recv_no:
        connection.send_ack()
        log_send(connection.send_ack_no, connection.recv_no,
                PacketType.ACK, 0, LogStatus.NEW)
    else:
        connection.send_ack()
        log_send(connection.send_ack_no, connection.recv_no,
                PacketType.ACK, 0, LogStatus.NEW)
        log_recv(pdu.frame_no, pdu.ack_no, 
                pdu.pdu_type, pdu.data_size, LogStatus.NOE)

def receive(connection:UDPConnection):
    while connection.running:
        try:
            connection.sock.settimeout(SK_TIMEOUT)
            pdu, addr = connection.recv_pdu()
            if connection.target_addr != addr:
                print(f"\rTarget address added: {addr} \n$ ", end="")
                connection.target_addr = addr
            if pdu == None:
                log_recv(connection.send_ack_no, connection.recv_no, 
                    PacketType.UNKNOWN, 0, LogStatus.DAE)
                continue
            if pdu.pdu_type == PacketType.MESSAGE or pdu.pdu_type == PacketType.FILE:
                receive_packet(connection, pdu)
            elif pdu.pdu_type == PacketType.ACK:
                if pdu.ack_no == connection.send_no:
                    log_recv(pdu.frame_no, pdu.ack_no, PacketType.ACK, 0, LogStatus.OK)
                    connection.recv_ack_no = pdu.ack_no
                elif pdu.ack_no < connection.send_no:
                    log_recv(pdu.frame_no, pdu.ack_no, PacketType.ACK, 0, LogStatus.RT)
                    connection.recv_ack_no = max(connection.recv_ack_no, pdu.ack_no)
                else:
                    log_recv(pdu.frame_no, pdu.ack_no, PacketType.ACK, 0, LogStatus.DAE)
        except socket.timeout:
            continue

def send_packet(connection:UDPConnection, data:bytes, pdu_type:PacketType=PacketType.MESSAGE):
    connection.send_pdu(pdu_type, data)
    log_send(connection.send_no, connection.recv_ack_no, 
             pdu_type, len(data), LogStatus.NEW)
    connection.send_no = connection.loop_no(connection.send_no + 1)
    time.sleep(RT_TIMEOUT)
    while connection.send_no != connection.recv_ack_no:
        connection.send_no = connection.loop_no(connection.send_no - 1)
        connection.send_pdu(pdu_type, data)
        log_send(connection.send_no, connection.recv_ack_no, 
                 pdu_type, len(data), LogStatus.TO)
        connection.send_no = connection.loop_no(connection.send_no + 1)
        time.sleep(RT_TIMEOUT)

def send_message(connection:UDPConnection, message:str):
    send_packet(connection, message.encode(), PacketType.MESSAGE)

def send_file_gbn(connection:UDPConnection, file_path:str):
    # send file name and size first
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    header = f"{file_name}{SEP}{file_size}".encode()
    send_packet(connection, header, PacketType.FILE)
    
    pbar = tqdm(total=file_size, unit="B", unit_scale=True)
    with open(file_path, "rb") as file:
        data = file.read()

    n_data = len(data)
    num_frames = (n_data + DATA_SIZE - 1) // DATA_SIZE
    while connection.window_left < num_frames:
        while connection.window_right < min(connection.window_left + SW_SIZE, num_frames):
            start = connection.window_right * DATA_SIZE
            end = min(start + DATA_SIZE, n_data)
            rel_step = connection.window_right - connection.window_left
            if  rel_step < len(connection.send_window):
                connection.send_pdu(
                    PacketType.FILE, 
                    data[start:end], 
                    connection.send_window[rel_step]
                )
                log_send(connection.send_window[rel_step], connection.recv_ack_no,
                         PacketType.FILE, end - start, LogStatus.TO)
            else:
                connection.send_pdu(PacketType.FILE, data[start:end])
                log_send(connection.send_no, connection.recv_ack_no,
                        PacketType.FILE, end - start, LogStatus.NEW)
                connection.send_window.append(connection.send_no)
                connection.send_no = connection.loop_no(connection.send_no + 1)
            connection.window_right += 1

        time.sleep(RT_TIMEOUT)

        if connection.send_no == connection.recv_ack_no:
            connection.window_left = connection.window_right
            pbar.update(len(connection.send_window) * DATA_SIZE)
            connection.send_window.clear()
        else: 
            num_frame_sent = connection.send_window.index(connection.recv_ack_no)
            connection.window_left += num_frame_sent
            # Go Back N
            connection.window_right = connection.window_left
            connection.send_window = connection.send_window[num_frame_sent:]
            pbar.update(num_frame_sent * DATA_SIZE)

    pbar.set_description("File sent")
    pbar.close()
    print("\r$ ", end="")
    connection.window_left = 0
    connection.window_right = 0
    connection.send_window.clear()

def send_file_sw(connection:UDPConnection, file_path:str):
    # stop and wait
    # send file name and size first
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    header = f"{file_name}{SEP}{file_size}".encode()
    send_packet(connection, header, PacketType.FILE)
    
    pbar = tqdm(total=file_size, unit="B", unit_scale=True)
    with open(file_path, "rb") as file:
        data = file.read()

    n_data = len(data)
    num_frames = (n_data + DATA_SIZE - 1) // DATA_SIZE
    for num_frame in range(num_frames):
        start = num_frame * DATA_SIZE
        end = min(start + DATA_SIZE, n_data)
        send_packet(connection, data[start:end], PacketType.FILE)
        pbar.update(end - start)

    pbar.set_description("File sent")
    pbar.close()
    print("\r$ ", end="")
