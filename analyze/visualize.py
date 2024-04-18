import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

colors = {
    'status': {
        'New': 'blue', 
        'OK': 'green', 
        'TimeOut': 'red', 
        'Retransmit': 'yellow', 
        'DataErr': 'black', 
        'NoErr': 'purple'
    },
    'action': {
        'Send': 'blue', 
        'Recv': 'green'
    },
    'pdu_type': {
        'MESSAGE': 'blue', 
        'FILE': 'red', 
        'ACK': 'green', 
        'UNKNOWN': 'black'
    }
}

labels = {
    'status': {
        'New': 'New', 
        'OK': 'OK', 
        'TimeOut': 'TimeOut', 
        'Retransmit': 'Retransmit', 
        'DataErr': 'DataErr', 
        'NoErr': 'NoErr'
    },
    'action': {
        'Send': 'Send', 
        'Recv': 'Recv'
    },
    'pdu_type': {
        'MESSAGE': 'MESSAGE', 
        'FILE': 'FILE', 
        'ACK': 'ACK', 
        'UNKNOWN': 'UNKNOWN'
    }
}

def get_dataframe_log(log_file:str='sender.log'):
    data_rows = []
    with open(log_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                items = line.split(', ')
                row = {}
                for item in items:
                    key, value = item.split('=')
                    if key == 'pdu_to_send' or key == 'pdu_recv':
                        key = 'frame_no'
                    elif key == 'acked_no' or key == 'pdu_exp':
                        key = 'ack_no'
                    row[key] = value
                data_rows.append(row)

    df_log = pd.DataFrame(data_rows)
    # 将frame_no, ack_no, data_size列转换为整数
    df_log['frame_no'] = df_log['frame_no'].astype(int)
    df_log['ack_no'] = df_log['ack_no'].astype(int)
    df_log['data_size'] = df_log['data_size'].astype(int)

    # 将time列转换为时间类型 
    df_log['time'] = pd.to_datetime(df_log['time'], format='%Y-%m-%d_%H:%M:%S')

    # 将action, pdu_type, status列转换为类别类型
    df_log['action'] = df_log['action'].astype('category')
    df_log['pdu_type'] = df_log['pdu_type'].astype('category')
    df_log['status'] = df_log['status'].astype('category')

    return df_log

def get_title(attribute:str, show_value:str):
    title = ''
    if show_value == 'data_size':
        title += 'Data Size'
    else:
        title += 'Frame No. / Ack No.'
    title += ' vs Time'
    title += ' with'
    if attribute == 'status':
        title += ' Status'
    elif attribute == 'action':
        title += ' Action'
    else:
        title += ' PDU Type'
    return title

def plot_log(df_log:pd.DataFrame, attribute:str='status', show_value:str='data_size', save_dir:str=None, width=10, height=5):
    assert attribute in ['status', 'action', 'pdu_type'], 'attribute must be one of status, action, pdu_type'
    assert show_value in ['data_size', 'frame_no'], 'show_value must be one of data_size, frame_no'
    plt.figure(figsize = (width, height))
    for attribute_value, group in df_log.groupby(attribute):
        if show_value == 'data_size':
            plt.plot(group['time'], group['data_size'], 'o-',
                    color=colors[attribute][attribute_value], 
                    label=labels[attribute][attribute_value])
        else:
            plt.scatter(group['time'], group['frame_no' if 'frame_no' in df_log.columns else 'ack_no'],
                    color=colors[attribute][attribute_value], 
                    label=labels[attribute][attribute_value])
    plt.xlabel('Time')
    plt.ylabel('Data Size' if show_value == 'data_size' else 'Frame No. / Ack No.')
    plt.title(get_title(attribute, show_value))
    plt.legend()
    plt.grid(True)
    if save_dir: 
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_path = f"{save_dir}/{attribute}_{show_value}.png" 
    else: 
        save_path = f"{attribute}_{show_value}.png"
    plt.savefig(save_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize the log file')
    parser.add_argument('--log_file', type=str, default='sender.log', help='The log file to visualize')
    parser.add_argument('--save_dir', type=str, default=None, help='The dir to save the plot')
    parser.add_argument('--attribute', type=str, default='status', help='The attribute to group by')
    parser.add_argument('--show_value', type=str, default='data_size', help='The value to show')
    args = parser.parse_args()
    df_log = get_dataframe_log(args.log_file)
    plot_log(df_log, args.attribute, args.show_value, args.save_dir)