import socket

# 创建 socket 对象
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 获取本地主机名
host = socket.gethostname()
print(f"本地主机名: {host}")
port = 12345  # 设置端口号

# 绑定端口号
server_socket.bind((host, port))

# 设置最大连接数，超过后排队
server_socket.listen(5)

print(f"服务器启动，监听来自 {host} 的连接，端口号 {port}...")

while True:
    # 建立客户端连接
    client_socket, addr = server_socket.accept()

    print(f"连接地址: {str(addr)}")

    msg = '欢迎访问服务器！' + "\r\n"
    client_socket.send(msg.encode('utf-8'))

    client_socket.close()  # 关闭连接
