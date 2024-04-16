import socket
import threading
import os
from typing import Tuple
from pdu import PDU, PacketType
from config import BUF_SIZE, SK_TIMEOUT, INIT_SEQ_NO, MAX_SEQ_LEN, RT_TIMEOUT, DATA_SIZE, SW_SIZE, SEP
from tqdm import tqdm

class UDPSender:
    def __init__(self, receiver_addr:Tuple[str, int]):
        self.receiver_addr = receiver_addr

        self.send_no = INIT_SEQ_NO
        self.ack_no = INIT_SEQ_NO
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True

    def loop_no(self, step:int):
        return (step - INIT_SEQ_NO) % MAX_SEQ_LEN + INIT_SEQ_NO

    def send_pdu(self, pdu_type:PacketType, data:bytes):
        pdu = PDU(self.send_no, self.ack_no, data, pdu_type)
        self.sock.sendto(pdu.pack(), self.receiver_addr)

    def recv_pdu(self):
        data, addr = self.sock.recvfrom(BUF_SIZE)
        pdu = PDU.unpack(data)
        return pdu, addr

def receive(sender:UDPSender):
    while sender.running:
        try:
            sender.sock.settimeout(SK_TIMEOUT)
            pdu, addr = sender.recv_pdu()
            if pdu.pdu_type == PacketType.MESSAGE:
                print(f"\r{addr}: {pdu.data.decode()} \n$ ", end="")
            elif pdu.pdu_type == PacketType.ACK:
                pass
            elif pdu.pdu_type == PacketType.FILE:
                pass
            else:
                print("\rUnknown PDU type. \n$ ", end="")
        except socket.timeout:
            continue

def send_message(sender:UDPSender, message:str):
    sender.send_pdu(PacketType.MESSAGE, message.encode())

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
    sender = UDPSender(('192.168.10.129', 42477))
    print(f"Receiver address: {sender.receiver_addr} ")
    recv_thread = threading.Thread(target=receive, args=(sender,))
    recv_thread.daemon = True 
    recv_thread.start()

    while True:
        message = input("$ ")
        if message.lower() == "exit":
            break
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
