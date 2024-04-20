import json

# 读取配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

# 读取配置文件
UDP_PORT = config['UDP_PORT']       # 请根据配置文件设置UDP端口
DATA_SIZE = config['DATA_SIZE']     # PDU数据字段的长度，单位为字节
ERROR_RATE = config['ERROR_RATE']   # PDU错误率
LOST_RATE = config['LOST_RATE']     # PDU丢失率
SW_SIZE = config['SW_SIZE']         # 发送窗口大小
MAX_SEQ_NO = config['MAX_SEQ_NO']   # 最大PDU序号
INIT_SEQ_NO = config['INIT_SEQ_NO'] # 起始PDU的序号
TIMEOUT = config['TIMEOUT']         # 超时定时器值，单位为毫秒

# for socket
MAX_SEQ_LEN = MAX_SEQ_NO - INIT_SEQ_NO + 1
SK_TIMEOUT = 1.0                 # socket 接收信息超时时间，单位为秒
BUF_SIZE = 2048                  # 缓冲区大小

# for file transfer
RT_TIMEOUT = TIMEOUT / 1000      # 超时重传的等待时间，单位为秒 很影响性能
SEP = "<SEP>"                    # 文件名和文件大小的分隔符

# others
ERROR_DATA = b'\x15/\x17pa<B\tgz\x1e#'  # 错误数据