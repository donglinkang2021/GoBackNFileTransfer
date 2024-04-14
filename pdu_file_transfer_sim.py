from pdu import PDU
from config import INIT_SEQ_NO, MAX_SEQ_NO, DATA_SIZE

with open('file_examples/miziha_running.png', 'rb') as file:
    file_data = file.read()

pdu_list = []
seq_num = INIT_SEQ_NO
ack_num = INIT_SEQ_NO
max_seq_len = MAX_SEQ_NO - INIT_SEQ_NO + 1
chunk_size = DATA_SIZE
for i in range(0, len(file_data), chunk_size):
    data_chunk = file_data[i:i+chunk_size]
    frame_no = (seq_num - INIT_SEQ_NO) % max_seq_len + INIT_SEQ_NO
    pdu = PDU(frame_no, ack_num, chunk_size, data_chunk)
    pdu_list.append(pdu)
    seq_num += 1

print("PDU list length: ", len(pdu_list))