import socket
# get host 
hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
print(f"host: {host}")
print(f"hostname: {hostname}")

def get_local_ip():
    # 创建套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # 连接到一个外部地址
        sock.connect(("192.168.10.129", 80))
        local_ip = sock.getsockname()
    except socket.error:
        local_ip = "未知"
    finally:
        sock.close()
    
    return local_ip

# 调用函数获取本地 IP 地址
local_ip = get_local_ip()
print("本地 IP 地址:", local_ip)
