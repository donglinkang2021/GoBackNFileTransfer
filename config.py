UDP_PORT = 42477            # 请根据配置文件设置UDP端口
DATA_SIZE = 1024            # PDU数据字段的长度，单位为字节
ERROR_RATE = 10             # PDU错误率
LOST_RATE = 10              # PDU丢失率
SW_SIZE = 90                # 发送窗口大小
MAX_SEQ_NO = 100            # 最大PDU序号
INIT_SEQ_NO = 1             # 起始PDU的序号
TIMEOUT = 1000              # 超时定时器值，单位为毫秒

# for socket
MAX_SEQ_LEN = MAX_SEQ_NO - INIT_SEQ_NO + 1
SK_TIMEOUT = 1.0                 # socket 接收信息超时时间，单位为秒
BUF_SIZE = 2048                  # 缓冲区大小

# for file transfer
RT_TIMEOUT = TIMEOUT / 1000      # 超时重传的等待时间，单位为秒 很影响性能
SEP = "<SEP>"                    # 文件名和文件大小的分隔符

# others
ERROR_DATA = b'\x15/\x17pa<B\tgz\x1e#'  # 错误数据