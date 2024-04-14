# Linux 虚拟机（服务器端）

import socket

# 设置服务器端地址和端口
host = '0.0.0.0'       # 使用所有网络接口
port = 12345           # 使用一个未被占用的端口号

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绑定地址和端口
sock.bind((host, port))

print("服务器已启动，等待通信...")

while True:
    # 接收来自客户端（Windows主机）的消息
    data, addr = sock.recvfrom(1024)  # 缓冲区大小为 1024 字节
    print(f"接收到来自 {addr} 的消息：{data.decode()}")

    # 向客户端发送回复消息
    reply_message = input("请输入要发送给客户端的消息：")
    sock.sendto(reply_message.encode(), addr)

    if reply_message.lower() == "exit":
        break
