# Windows 主机（客户端）

import socket
import threading

# 设置服务器端地址和端口（Linux虚拟机的地址）
server_address = '192.168.10.129'  # Linux虚拟机的IP地址或主机名
server_port = 12345                     # 服务器端的端口号

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def receive_messages():
    while True:
        try:
            # 尝试接收服务器端（Linux虚拟机）的回复消息，设置非阻塞
            sock.settimeout(1.0)  # 设置超时时间为1秒
            data, addr = sock.recvfrom(1024)  # 缓冲区大小为 1024 字节
            print(f"接收到来自 {addr} 的回复：{data.decode()}")
        except socket.timeout:
            continue  # 如果超时，继续循环接收消息

def main():
    # 创建接收消息的线程
    recv_thread = threading.Thread(target=receive_messages)
    recv_thread.daemon = True  # 设置线程为守护线程，主程序退出时线程也会退出
    recv_thread.start()

    while True:
        # 从键盘输入要发送给服务器端的消息
        message = input("请输入要发送给服务器端的消息：")
        
        # 向服务器端发送消息
        sock.sendto(message.encode(), (server_address, server_port))

        if message.lower() == "exit":
            break

if __name__ == "__main__":
    main()
