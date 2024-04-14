def reverse(poly, width):
    result = 0
    for _ in range(width):
        result = (result << 1) | (poly & 1)
        poly >>= 1
    return result

poly = 0x4C11DB7

# print(hex(reverse(poly, 32)))

def get_mask(width:int):
    return 1 << (width // 8 + 1) * 8 - 1

print(hex(get_mask(7)))