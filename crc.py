"""
crc demo here
"""

data = 0b0010_1001
original_data = data
poly = 0b1101

def bit_length(x):
    return len(bin(x)) - 2

data_len = bit_length(data)
crc_len = bit_length(poly) - 1
total_length = data_len + crc_len

data <<= crc_len
print(f"Data: {bin(data)}")


quotient = []
for i in range(data_len):
    print(f"mask: {bin(1 << (total_length - 1 - i))}")
    if data & (1 << (total_length - 1 - i)):
        quotient.append("1")
        print(f"poly: {bin(poly << (data_len - 1 - i))}")
        data ^= poly << (data_len - 1 - i)
        print(f"Data: {bin(data)}")
    else:
        quotient.append("0")

print(f"Quotient: {''.join(quotient)}")
print(f"Remainder: {data:0{crc_len}b}")

print(f"Transmitted data: {bin(original_data << crc_len | data)}")


