import socket

# 创建 socket 对象
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 获取本地主机名
host = socket.gethostname()
port = 12345  # 设置端口号

# 连接服务，指定主机和端口
client_socket.connect((host, port))

# 接收服务器消息
msg = client_socket.recv(1024)
print(msg.decode('utf-8'))

client_socket.close()  # 关闭连接
