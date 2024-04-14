# CRC-16/CCITT-FALSE
def crc16(data : bytes, offset : int , length : int):
    if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data):
        return 0
    crc = 0xffff
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for _ in range(8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF

# test
# data = bytearray(b'\x31\x32\x33\x34')
data = "1234".encode()

# show the result
print(hex(crc16(data, 0, len(data)))) # 0x5349