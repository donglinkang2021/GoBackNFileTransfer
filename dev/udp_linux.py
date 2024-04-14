import socket

# 监听的地址和端口
windows_ip = '192.168.10.129' # 与主机上的IP地址相同
windows_port = 42477  # 与主机上的端口号相同

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绑定地址和端口
sock.bind((windows_ip, windows_port))

print(f"等待来自Windows主机 {windows_ip} 的消息...")

while True:
    # 接收消息
    data, address = sock.recvfrom(1024)  # 一次最多接收1024字节数据

    # 解码消息
    message = data.decode()

    # 打印接收到的消息和发送者的地址
    print(f"收到来自 {address[0]}:{address[1]} 的消息：{message}")

    if message.lower() == "exit":
        break

# 关闭套接字
sock.close()
