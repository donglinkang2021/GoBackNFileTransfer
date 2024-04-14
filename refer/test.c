#include<stdio.h>
#include<crcLib.h>

int main()
{
    uint8_t data[] = {0x31, 0x32, 0x33, 0x34};
    uint16_t length = sizeof(data)/sizeof(data[0]);
    printf("CRC4_ITU: %X\n", crc4_itu(data, length));
    printf("CRC5_EPC: %X\n", crc5_epc(data, length));
    printf("CRC5_ITU: %X\n", crc5_itu(data, length));
    printf("CRC5_USB: %X\n", crc5_usb(data, length));
    printf("CRC6_ITU: %X\n", crc6_itu(data, length));
    printf("CRC7_MMC: %X\n", crc7_mmc(data, length));
    printf("CRC8: %X\n", crc8(data, length));
    printf("CRC8_ITU: %X\n", crc8_itu(data, length));
    printf("CRC8_ROHC: %X\n", crc8_rohc(data, length));
    printf("CRC8_MAXIM: %X\n", crc8_maxim(data, length));
    printf("CRC16_IBM: %X\n", crc16_ibm(data, length));
    printf("CRC16_MAXIM: %X\n", crc16_maxim(data, length));
    printf("CRC16_USB: %X\n", crc16_usb(data, length));
    printf("CRC16_MODBUS: %X\n", crc16_modbus(data, length));
    printf("CRC16_CCITT: %X\n", crc16_ccitt(data, length));
    printf("CRC16_CCITT_FALSE: %X\n", crc16_ccitt_false(data, length));
    printf("CRC16_X25: %X\n", crc16_x25(data, length));
    printf("CRC16_XMODEM: %X\n", crc16_xmodem(data, length));
    printf("CRC16_DNP: %X\n", crc16_dnp(data, length));
    printf("CRC32: %X\n", crc32(data, length));
    printf("CRC32_MPEG_2: %X\n", crc32_mpeg_2(data, length));
    return 0;
}

/*
CRC4_ITU: D
CRC5_EPC: 1D
CRC5_ITU: D
CRC5_USB: F
CRC6_ITU: 2E
CRC7_MMC: 3A
CRC8: C2
CRC8_ITU: 97
CRC8_ROHC: 85
CRC8_MAXIM: F1
CRC16_IBM: 14BA
CRC16_MAXIM: EB45
CRC16_USB: CF45
CRC16_MODBUS: 30BA
CRC16_CCITT: 8832
CRC16_CCITT_FALSE: 5349
CRC16_X25: 74EC
CRC16_XMODEM: D789
CRC16_DNP: 4213
CRC32: 9BE3E0A3
CRC32_MPEG_2: A695C4AA
*/