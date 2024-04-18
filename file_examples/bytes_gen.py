import struct
from config import *

# gennerate a fixed bytes
def repeat_bytes(data:bytes, size:int):
    return data * size

# generate a random bytes
my_data = b'\x15/\x17pa<B\tgz\x1e#' * 2048 # 24.0 KB
data = repeat_bytes(my_data, 32)
print(f"data size: {len(data) / 1024} KB") # 1.5 KB
with open(f"level_{len(data) / 1024}_KB.txt", "wb") as file:
    file.write(data)

n_data = len(data)
num_frames = (n_data + DATA_SIZE - 1) // DATA_SIZE
print(f"n_data: {n_data} bytes")
print(f"num_frames: {num_frames}")


"""
data size: 1.5 KB
n_data: 1536 bytes
num_frames: 2
"""

"""
sf
level1.txt
"""