import socket
import threading

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 准备进入通信循环
print("等待通信...")

addr_set = set()
target_addr = " "

def receive_messages():
    while True:
        try:
            # 尝试接收服务器端（Linux虚拟机）的回复消息，设置非阻塞
            sock.settimeout(1.0)  # 设置超时时间为1秒
            data, addr = sock.recvfrom(1024)  # 缓冲区大小为 1024 字节
            print(f"\r{addr}: {data.decode()} \n${target_addr} ", end="")
            addr_set.add(addr)
        except socket.timeout:
            continue  # 如果超时，继续循环接收消息


# 创建接收消息的线程
recv_thread = threading.Thread(target=receive_messages)
recv_thread.daemon = True  # 设置线程为守护线程，主程序退出时线程也会退出
recv_thread.start()

while True:
    message = input(f"${target_addr} ")
    if message.lower() == "addr":
        addr = input("输入发送的<ip:port>: ").strip().split(":")
        addr_set.add((addr[0], int(addr[1])))
    elif message.lower() == "exit":
        break
    elif message.lower() == "list" or message.lower() == "ls":
        print(addr_set)
    elif message.lower() == "host":
        print(socket.gethostbyname(socket.gethostname()))
    elif message.lower() == "bind":
        host, port = input("输入要绑定的<ip:port>: ").strip().split(":")
        sock.bind((host, int(port)))
    elif message.lower() == "unicast" or message.lower() == "uni":
        target_addr = input("输入发送的<ip:port>: ").strip()
    elif message.lower() == "broadcast" or message.lower() == "bro":
        target_addr = " "
    else:
        if target_addr != " ":
            host, port = target_addr.split(":")
            sock.sendto(message.encode(),  (host, int(port)))
        else:
            for addr in addr_set:
                sock.sendto(message.encode(), addr)  # 广播

# 关闭套接字
sock.close()