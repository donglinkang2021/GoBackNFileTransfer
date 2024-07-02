import struct
from crc import CRC, CRC_ALGORITHMS


# 创建要打包的数据
integer_value = 42
float_value = 3.14
byte_value = b'\x00\x01\x02\x03'

# 使用 struct.pack 将数据打包
packed_data = struct.pack('if4s', integer_value, float_value, byte_value)
print(len(packed_data))

# 添加 CRC 校验
crc_ccitt = CRC(**CRC_ALGORITHMS["CRC-16/CCITT"])
crc_value = crc_ccitt.calculate(packed_data)
print(hex(crc_value))
packed_data += struct.pack('H', crc_value)

# 使用 struct.unpack 解包数据
unpacked_data = packed_data[:-2]
crc_value = packed_data[-2:]
print(crc_value)
print(hex(crc_ccitt.calculate(unpacked_data)))
# 判断校验值是否正确
if crc_ccitt.calculate(unpacked_data) == struct.unpack('H', crc_value)[0]:
    print('CRC 校验成功')

integer_value, float_value, byte_value = struct.unpack('if4s', unpacked_data)
print(integer_value, float_value, byte_value)
