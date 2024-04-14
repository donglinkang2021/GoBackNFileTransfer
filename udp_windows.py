import socket

HOST = '192.168.10.129'
PORT = 42477

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绑定地址和端口
sock.bind((HOST, PORT))

# 虚拟机 A
# 准备进入通信循环
print("虚拟机 A 启动，等待通信...")

while True:
    # 接收来自虚拟机 B 的消息
    data, addr = sock.recvfrom(1024)  # 缓冲区大小为 1024 字节
    print(f"虚拟机 A 接收到消息：{data.decode()} 来自 {addr}")

    # 向虚拟机 B 发送消息
    message = input("请输入要发送给虚拟机 B 的消息：")
    sock.sendto(message.encode(), addr)

    if message.lower() == "exit":
        break

# 关闭套接字
sock.close()
