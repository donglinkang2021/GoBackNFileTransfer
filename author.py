from config import ERROR_DATA

def xor_two_bytes(b1:bytes, b2:bytes) -> bytes:
    return bytes([b1[i] ^ b2[i] for i in range(len(b1))])

print(xor_two_bytes(ERROR_DATA, "😘🤗🤔".encode()).decode())

