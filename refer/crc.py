class CRC:
    def __init__(self, width, poly, crc_init, refin, refout, xorout):
        
        self.width = width
        self.poly = poly
        self.crc_init = crc_init
        self.refin = refin
        self.refout = refout
        self.xorout = xorout

        # crc_len must be 8, 16 or 32
        self.crc_len = ((width - 1) // 8 + 1) * 8
        self.res_mask = (1 << width) - 1

    def reverse(self, poly, width):
        result = 0
        for _ in range(width):
            result = (result << 1) | (poly & 1)
            poly >>= 1
        return result


    def calculate(self, data:bytes):
        
        if self.refin:
            # reverse: operate from right bit
            crc = self.crc_init
            op_mask = 1 
            poly = self.reverse(self.poly, self.width)
            for data_byte in data:
                crc ^= data_byte
                for _ in range(8):
                    if (crc & op_mask) > 0: crc = (crc >> 1) ^ poly
                    else: crc = crc >> 1
        else:
            # operate from left bit
            crc = self.crc_init << (self.crc_len - self.width)
            op_mask = 1 << (self.crc_len - 1)
            poly = self.poly << (self.crc_len - self.width)
            for data_byte in data:
                crc ^= data_byte << (self.crc_len - 8)
                for _ in range(8):
                    if (crc & op_mask) > 0: crc = (crc << 1) ^ poly
                    else: crc = crc << 1
            crc = crc >> (self.crc_len - self.width)
        return crc & self.res_mask ^ self.xorout

from predefined import CRC_ALGORITHMS

data = "1234".encode()
for algo in CRC_ALGORITHMS.keys():
    crc =  CRC(**CRC_ALGORITHMS[algo])
    print(f"{algo}:", hex(crc.calculate(data)))


"""
CRC-4/ITU: 0xd
CRC-5/EPC: 0x1d
CRC-5/ITU: 0xd
CRC-5/USB: 0xf
CRC-6/ITU: 0x2e
CRC-7/MMC: 0x3a
CRC-8: 0xc2
CRC-8/ITU: 0x97
CRC-8/ROHC: 0x85
CRC-8/MAXIM: 0xf1
CRC-16/IBM: 0x14ba
CRC-16/MAXIM: 0xeb45
CRC-16/USB: 0xcf45
CRC-16/MODBUS: 0x30ba
CRC-16/CCITT: 0x8832
CRC-16/CCITT-FALSE: 0x5349
CRC-16/X25: 0x74ec
CRC-16/XMODEM: 0xd789
CRC-16/DNP: 0x4213
CRC-32: 0x9be3e0a3
CRC-32/MPEG-2: 0xa695c4aa
"""