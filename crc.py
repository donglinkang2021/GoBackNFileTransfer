def bit_length(x):
    return len(bin(x)) - 2

def crc(data: int, poly: int) -> int:
    data_len = bit_length(data)
    crc_len = bit_length(poly) - 1
    total_length = data_len + crc_len

    data <<= crc_len
    for i in range(data_len):
        if data & (1 << (total_length - 1 - i)):
            data ^= poly << (data_len - 1 - i)

    return data, crc_len

# data = 0b101_1001
# poly = 0b1_1001
data = 0b1101_0110_11
poly = 0b1_0011

remainder, crc_len = crc(data, poly)
print(f"Remainder: {remainder:0{crc_len}b}")


