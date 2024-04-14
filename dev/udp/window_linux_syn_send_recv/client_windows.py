# Windows 主机（客户端）

import socket

# 设置服务器端地址和端口（Linux虚拟机的地址）
server_address = '192.168.10.129'  # Linux虚拟机的IP地址或主机名
server_port = 12345                     # 服务器端的端口号

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("客户端已启动")

while True:
    # 向服务器端（Linux虚拟机）发送消息
    message = input("请输入要发送给服务器端的消息：")
    sock.sendto(message.encode(), (server_address, server_port))

    # 接收服务器端（Linux虚拟机）的回复消息
    data, addr = sock.recvfrom(1024)  # 缓冲区大小为 1024 字节
    print(f"接收到来自服务器端的回复：{data.decode()}")

    if message.lower() == "exit":
        break

# 注意：在实际使用中，请将 'linux_vm_ip_address' 替换为运行服务器端代码的Linux虚拟机的实际IP地址或主机名。
