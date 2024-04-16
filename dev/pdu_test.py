import struct
from pdu import PDU

frame_no = 1
ack_no = 2

integer_value = 42
float_value = 3.14
byte_value = b'\x00\x01\x02\x03'
data = struct.pack('if4s', integer_value, float_value, byte_value)

pdu = PDU(frame_no, ack_no, data)
print(pdu)

packed_data = pdu.pack()

# Simulate data corruption
print('---Simulate data corruption---')
print(packed_data)
# change one byte at index 5
packed_data = packed_data[:5] + b'\x00' + packed_data[6:] 
print(packed_data)

unpacked_pdu = PDU.unpack(packed_data)
if unpacked_pdu.is_corrupted():
    print('PDU is corrupted')
else:
    print("PDU is not corrupted")
    print(unpacked_pdu)
    integer_value, float_value, byte_value = struct.unpack('if4s', unpacked_pdu.data)
    print(integer_value, float_value, byte_value)

