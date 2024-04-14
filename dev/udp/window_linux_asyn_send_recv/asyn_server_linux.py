# Linux 虚拟机（服务器端）

import socket
import threading

# 设置服务器端地址和端口
host = '0.0.0.0'       # 使用所有网络接口
port = 12345           # 使用一个未被占用的端口号

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绑定地址和端口
sock.bind((host, port))

print("服务器已启动，等待通信...")

addr_set = set()

def receive_messages():
    while True:
        # 接收来自客户端（Windows主机）的消息
        data, addr = sock.recvfrom(1024)  # 缓冲区大小为 1024 字节
        print(f"接收到来自 {addr} 的消息：{data.decode()}")
        addr_set.add(addr)

def main():
    # 创建接收消息的线程
    recv_thread = threading.Thread(target=receive_messages)
    recv_thread.daemon = True  # 设置线程为守护线程，主程序退出时线程也会退出
    recv_thread.start()

    while True:
        # 从键盘输入要发送给客户端的消息
        message = input("请输入要发送给客户端的消息：")
        
        # 向客户端发送消息
        # 广播
        for addr in addr_set:
            sock.sendto(message.encode(), addr)  # 注意这里的地址是客户端的地址和端口号

if __name__ == "__main__":
    main()
