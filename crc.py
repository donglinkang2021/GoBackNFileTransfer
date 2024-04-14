def bit_length(x):
    return len(bin(x)) - 2

def crc(data: int, poly: int) -> int:
    """
    Usage:

    example 1

    >>> data = 0b1101_0110_11
    >>> poly = 0b1_0011
    >>> remainder, crc_len = crc(data, poly)
    >>> print(f"Remainder: {remainder:0{crc_len}b}")
    Remainder: 1110

    example 2
    >>> data = 0b1101_0110_11_1110
    >>> poly = 0b1_0011
    >>> remainder, crc_len = crc(data, poly)
    >>> print(f"Remainder: {remainder:0{crc_len}b}")
    Remainder: 0000
    """
    data_len = bit_length(data)
    crc_len = bit_length(poly) - 1
    total_length = data_len + crc_len

    data <<= crc_len
    for i in range(data_len):
        if data & (1 << (total_length - 1 - i)):
            data ^= poly << (data_len - 1 - i)

    return data, crc_len

