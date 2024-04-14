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