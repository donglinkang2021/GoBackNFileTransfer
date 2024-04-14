import socket

# 目标 Linux 虚拟机的 IP 地址和端口
linux_ip = '192.168.10.129'  # 例如 '192.168.1.100'
linux_port = 42477  # 选择一个未被占用的端口号

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # 输入消息
    message = input("请输入要发送的消息：")

    # 发送消息到 Linux 虚拟机
    sock.sendto(message.encode(), (linux_ip, linux_port))

    if message.lower() == "exit":
        break

# 关闭套接字
sock.close()
