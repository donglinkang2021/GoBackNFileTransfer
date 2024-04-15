# logger.py
import logging
from utils import get_time
from enum import Enum

class LogType(Enum):
    SEND = 'Send'
    RECV = 'Recv'

    def __str__(self):
        return self.value

class LogStatus(Enum):

    NEW = 'New'
    TO = 'TimeOut'
    RT = 'Retransmit'

    DAE = 'DataErr'
    NOE = 'NoErr' # No. Err
    OK = 'OK'

    ACK = 'ACK'

    def __str__(self):
        return self.value

def init_logger(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_file,
        filemode='w')

def log_send(pdu_to_send:int, acked_no:int,
             data_size:int, status:LogStatus):
    """
    >>> pdu = PDU(1, 1, b'hello')
    >>> log_send(pdu.frame_no, pdu.ack_no, pdu.data_size, LogStatus.NEW)
    """
    log_info = f"time={get_time('%Y-%m-%d_%H:%M:%S')}, "
    log_info += f"pdu_type={LogType.SEND}, "
    log_info += f"pdu_to_send={pdu_to_send}, "
    log_info += f"acked_no={acked_no}, "
    log_info += f"data_size={data_size}, "
    log_info += f"status={status}"
    logging.info(log_info)

def log_recv(pdu_recv:int, pdu_exp:int, 
             data_size:int, status:LogStatus):
    """
    >>> pdu, addr = client.receive_pdu()
    >>> log_recv(pdu.frame_no, client.recv_no, pdu.data_size, LogStatus.OK)
    """
    log_info = f"time={get_time('%Y-%m-%d_%H:%M:%S')}, "
    log_info += f"pdu_type={LogType.RECV}, "
    log_info += f"pdu_recv={pdu_recv}, "
    log_info += f"pdu_exp={pdu_exp}, "
    log_info += f"data_size={data_size}, "
    log_info += f"status={status}"
    logging.info(log_info)