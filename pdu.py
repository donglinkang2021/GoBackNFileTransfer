import struct
from crc import CRC, CRC_ALGORITHMS

crc16 = CRC(**CRC_ALGORITHMS["CRC-16/CCITT"])

class PDU:
    def __init__(self, frame_no:int, ack_no:int, data:bytes, 
                 data_size:int=None, checksum:int = None):
        self.frame_no = frame_no
        self.ack_no = ack_no
        self.data = data
        self.data_size = len(data) if data_size is None else data_size
        self.checksum = checksum

    def __str__(self):
        return f'frame_no: {self.frame_no}, ack_no: {self.ack_no}, data_size: {self.data_size}, checksum: {self.checksum}'
    
    def get_packed_data(self):
        return struct.pack('HHH', self.frame_no, self.ack_no, self.data_size) + self.data

    def pack(self):
        packed_data = self.get_packed_data()
        self.checksum = crc16.calculate(packed_data)
        packed_data += struct.pack('H', self.checksum)
        return packed_data
    
    def is_corrupted(self):
        packed_data = self.get_packed_data()
        return crc16.calculate(packed_data) != self.checksum
    
    @staticmethod
    def unpack(packed_data:bytes):
        frame_no, ack_no, data_size = struct.unpack('HHH', packed_data[:6])
        data = packed_data[6:-2]
        checksum = struct.unpack('H', packed_data[-2:])[0]
        return PDU(frame_no, ack_no, data, data_size, checksum)

