import struct
from enum import Enum
from crc import CRC, CRC_ALGORITHMS

crc16 = CRC(**CRC_ALGORITHMS["CRC-16/CCITT"])

class PacketType(Enum):
    MESSAGE = 0
    FILE = 1
    ACK = 2

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
        frame_no, ack_no, data_size, pdu_type = struct.unpack('HHHH', packed_data[:8])
        data = packed_data[8:-2]
        checksum = struct.unpack('H', packed_data[-2:])[0]
        return PDU(frame_no, ack_no, data, PacketType(pdu_type), data_size, checksum)

