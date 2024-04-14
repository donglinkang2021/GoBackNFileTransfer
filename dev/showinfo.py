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
        sock.connect(("8.8.8.8", 80))  # 使用谷歌的 DNS 服务器地址作为连接目标
        local_ip = sock.getsockname()[0]
    except socket.error:
        local_ip = "未知"
    finally:
        sock.close()
    
    return local_ip

# 调用函数获取本地 IP 地址
local_ip = get_local_ip()
print("本地 IP 地址:", local_ip)
