import struct
from enum import Enum
from crc import CRC, CRC_ALGORITHMS

crc16 = CRC(**CRC_ALGORITHMS["CRC-16/CCITT"])

class PacketType(Enum):
    MESSAGE = 0
    FILE = 1
    ACK = 2
    UNKNOWN = 3

    def __str__(self) -> str:
        return self.name

class PDU:
    def __init__(self, frame_no:int, ack_no:int, data:bytes, 
                 pdu_type:PacketType=PacketType.MESSAGE,
                 data_size:int=None, checksum:int = None):
        self.frame_no = frame_no
        self.ack_no = ack_no
        self.pdu_type = pdu_type
        self.data = data
        self.data_size = len(data) if data_size is None else data_size
        self.checksum = checksum

    def __str__(self) -> str:
        return f'frame_no: {self.frame_no}, ack_no: {self.ack_no}, pdu_type: {self.pdu_type}, data_size: {self.data_size}, checksum: {self.checksum}'
    
    def get_packed_data(self) -> bytes:
        return struct.pack('HHHH', self.frame_no, self.ack_no, self.data_size, self.pdu_type.value) + self.data

    def pack(self) -> bytes:
        packed_data = self.get_packed_data()
        self.checksum = crc16.calculate(packed_data)
        packed_data += struct.pack('H', self.checksum)
        return packed_data
    
    def is_corrupted(self) -> bool:
        packed_data = self.get_packed_data()
        return crc16.calculate(packed_data) != self.checksum
    
    @staticmethod
    def unpack(packed_data:bytes):
        sender_checksum = struct.unpack('H', packed_data[-2:])[0]
        data_checksum = crc16.calculate(packed_data[:-2])
        if data_checksum != sender_checksum:
            return None
        frame_no, ack_no, data_size, pdu_type = struct.unpack('HHHH', packed_data[:8])
        data = packed_data[8:-2]
        checksum = struct.unpack('H', packed_data[-2:])[0]
        return PDU(frame_no, ack_no, data, PacketType(pdu_type), data_size, checksum)

"""Windows PowerShell
PS D:\Desktop2\Computer_Networks\lexue\PROJECT\GBN\GoBackN> python .\UDPhost.py
$ hello
('192.168.10.129', 42477): hihi 
('192.168.10.129', 42477): hahah 
$ okkkk
File received: 100%|████████████████████████████████████████████████████████████████████| 3.32M/3.32M [04:27<00:00, 12.4kB/s] 
<file_path>: 192.168.10.1_42477/received\miziha_running.png
$ jell
$ info
target_addr: ('192.168.10.129', 42477)
send_no: 4
recv_ack_no: 4
recv_no: 51
send_ack_no: 51
$ sf
<file_path>: file_examples\level_768.0_KB.txt
File sent: 100%|██████████████████████████████████████████████████████████████████████████| 786k/786k [00:58<00:00, 13.5kB/s] 
$ exit
"""

"""Ubuntu Terminal
(.venv) linkdom@ubuntu:~/Desktop/GBN$ python UDPhost.py 
('192.168.10.1', 42477): hello 
$ hihi
$ hahah
('192.168.10.1', 42477): okkkk 
$ sf
<file_path>: received/miziha_running.png
File sent: : 3.32MB [04:27, 12.4kB/s]                                                                                         
('192.168.10.1', 42477): jell 
$ info
target_addr: ('192.168.10.1', 42477)
send_no: 51
recv_ack_no: 51
recv_no: 4
send_ack_no: 4
Receiving file: level_768.0_KB.txt (786432 bytes) ...
File received: 100%|███████████████████████████████████████████████████████████████████████| 786k/786k [00:58<00:00, 13.4kB/s]
<file_path>: 192.168.10.129_42477/received/level_768.0_KB.txt 
$ exit
"""