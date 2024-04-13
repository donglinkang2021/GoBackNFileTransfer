"""
CRC order: 16
CRC polynomial: 0x1021
Inital value: 0xFFFF
Final value: 0x0000
Direct: True
"""
def crc16(data : bytearray, offset:int , length:int):
    if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data):
        return 0
    crc = 0xFFFF
    print("crc: ")
    print("- bin: ", bin(crc))
    print("- hex: ", hex(crc))
    for i in range(0, length):
        print("data:")
        print("- bin: ", bin(data[offset + i]))
        print("- hex: ", hex(data[offset + i]))
        print("data[offset + i] << 8: ")
        print("- bin: ", bin(data[offset + i] << 8))
        print("- hex: ", hex(data[offset + i] << 8))
        crc ^= data[offset + i] << 8
        print("crc: ")
        print("- bin: ", bin(crc))
        print("- hex: ", hex(crc))
        for j in range(0,8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF

# test
data = bytearray(b'\x01\x02\x03\x04')

# show the result
print(hex(crc16(data, 0, len(data)))) # 0x31c3