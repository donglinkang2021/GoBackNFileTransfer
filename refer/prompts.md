# GoBackN Prompts

## [已解决]编译报错

我的代码编译报错：

```shell
PS D:\Desktop2\Computer_Networks\lexue\PROJECT\GBN\GoBackN\refer> gcc -o test .\test.c .\crcLib.c
.\test.c:2:9: fatal error: crcLib.h: No such file or directory
 #include<crcLib.h>
         ^~~~~~~~~~
compilation terminated.
```

我的当前目录为

```shell
PS D:\Desktop2\Computer_Networks\lexue\PROJECT\GBN\GoBackN\refer> ls


    目录: D:\Desktop2\Computer_Networks\lexue\PROJECT\GBN\GoBackN\refer


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         2024/4/14     11:04          15778 crcLib.c
-a----         2024/4/14     11:05           1186 crcLib.h
-a----         2024/4/14     11:14            274 prompts.md
-a----         2024/4/14     11:13           1382 test.c
```

请问如何解决这个问题？

### 解答

使用` -I `选项来指定头文件所在的路径。

```shell
gcc -o test test.c crcLib.c -I.
```

## 希望使用十六进制打印

我希望使用十六进制打印，但是我不知道如何使用`printf`函数来打印十六进制。我的代码如下：

```c
#include<stdio.h>
#include<crcLib.h>

int main()
{
    uint8_t data[] = {0x31, 0x32, 0x33, 0x34};
    uint16_t length = sizeof(data)/sizeof(data[0]);
    printf("CRC4_ITU: %d\n", crc4_itu(data, length));
    printf("CRC5_EPC: %d\n", crc5_epc(data, length));
    printf("CRC5_ITU: %d\n", crc5_itu(data, length));
    printf("CRC5_USB: %d\n", crc5_usb(data, length));
    printf("CRC6_ITU: %d\n", crc6_itu(data, length));
    printf("CRC7_MMC: %d\n", crc7_mmc(data, length));
    printf("CRC8: %d\n", crc8(data, length));
    printf("CRC8_ITU: %d\n", crc8_itu(data, length));
    printf("CRC8_ROHC: %d\n", crc8_rohc(data, length));
    printf("CRC8_MAXIM: %d\n", crc8_maxim(data, length));
    printf("CRC16_IBM: %d\n", crc16_ibm(data, length));
    printf("CRC16_MAXIM: %d\n", crc16_maxim(data, length));
    printf("CRC16_USB: %d\n", crc16_usb(data, length));
    printf("CRC16_MODBUS: %d\n", crc16_modbus(data, length));
    printf("CRC16_CCITT: %d\n", crc16_ccitt(data, length));
    printf("CRC16_CCITT_FALSE: %d\n", crc16_ccitt_false(data, length));
    printf("CRC16_X25: %d\n", crc16_x25(data, length));
    printf("CRC16_XMODEM: %d\n", crc16_xmodem(data, length));
    printf("CRC16_DNP: %d\n", crc16_dnp(data, length));
    printf("CRC32: %d\n", crc32(data, length));
    printf("CRC32_MPEG_2: %d\n", crc32_mpeg_2(data, length));
    return 0;
}
```

### 解答

使用`%X`来打印十六进制。

```c
