# GBN实现可靠文件传输

> 从网上大概看了一下别人实现的代码，大概知道了一下方向，规划一下自己目前计划

- [x] 调研实现GBN还需要用到哪些库
  - [x] socket
  - [x] struct
  - [x] threading
- [x] 开始学习基础的socket编程
  - [x] 先实现简单的文件传输功能 (实现了本机中windows的简单传输)
  - [x] 实现了向虚拟机中传输文件
- [x] 学习基础的struct库
  - [x] 使用struct库来实现数据的打包和解包
  - [x] 实现了自己的CRC校验
  - [x] 实现了自定义的packet结构
- [x] 使用自己定义的基础pdu来用UDP传数据
  - [x] 学习UDP传输是怎么传的 写了各种简单的UDP传输异步收发信息
  - [x] 现在本地实现文件如何打包成packet
  - [x] 先传一个简单的packet (在linux和windows之间)
  - [x] 传packet并获得ack
  - [x] 实现记录通信日志
  - [x] 修改一下ack的逻辑 [fix bug]
  - [x] 添加显示收发了多少条信息的函数
  - [x] 添加超时重传模块
  - [x] 重构整个UDPClient.py为两个类，完成udp文件传输
    - [x] UDPSender
    - [x] UDPReceiver
    - [x] 但目前只实现了单向传输，但保证了文件的可靠传输
  - [x] 现在要做的事情是完成一个packet的重传
    - [x] 测试重传
  - [x] 优化命名
- [x] 改一下logging的顺序 感觉这边的逻辑还是有点问题
- [x] 实现滑动窗口传输文件
  - [x] 在一个packet的基础上操作就是多个packet的操作
  - [x] 测试不同窗口大小对传输速度的影响 看看有没有其它bug
  - [x] 错误生成是在发送端 发送多个packet的时候，随机生成PDU错误或者PDU丢失
  - [x] 测试错误生成
  - [x] 读取日志文件，对通信状态记录数据进行统计分析
  - [x] 看一下可不可以优化一下速度 减少超时重传的次数
    - [x] 优化Go Back N 的实现
    - [x] 思考超时重传和重传的关系
  - [ ] 下一步可以做的事情是统计数据
    - [ ] 文件划分的 PDU 总数量
    - [ ] 通信总次数
    - [ ] 超时次数
    - [ ] 重传 PDU 的数量
    - [ ] 总耗时
- [ ] 将两个类合并为一个类
  - [ ] 第一件要做的事情就是命名一致

## 基本功能实现情况

- [x] 自行定义帧（PDU）结构。需要在 PDU 末尾增加 checksum 字段。checksum 采用
CRC-CCITT 标准。
  - 这里的PDU结构是自己定义的，组成部分为：`frame_no,ack_no,data_size,data,checksum`，其中`frame_no`是帧的序号，`ack_no`是确认号，`data_size`是数据的大小，`data`是数据，`checksum`是校验和。
  - 其中自己实现了各种CRC校验，包括CRC-CCITT，CRC-16，CRC-32等并封装成了一个package，可以直接调用。
- [x] 采用 UDP Socket API 模拟并实现 PDU 的发送和接收，每个 UDP 数据报封装一个
PDU。
- [x] PDU 中数据部分的长度不要超过 4KB。自己的实现中，数据部分的长度为1KB。
- [x] 实现的 GBN 协议应支持全双工，实现双向文件传输
- [x] 生成器或方法，允许根据配置文件中给出的百分比（n%）随机产生 PDU 错误和 PDU 丢失
- [x] 3MB 以上的文件用于测试。本项目中分别准备了一个 3MB 以上的`.png`和`.pdf`文件，用于测试。
- [x] 文件传输完毕后，接收并保存的文件应与发送的原始文件一模一样
- [x] 通过配置文件配置通信通信或协议参数
- [x] 记录通信状态到日志中
- [ ] 读取日志文件，对通信状态记录数据进行统计分析，从多个维度分析比较不同的数据大小、窗口大小、PDU 错误率、PDU 丢失率和超时值时的通信效率，例如：文件划分的 PDU 总数量，通信总次数，超时次数，重传 PDU 的数量、总耗时等，可以用图表表示，并得出分析结论

## 增强功能实现情况

- [x] 支持多台主机之间的同时通信
- [x] 采用多线程实现多台主机之间的同时通信

## 日志文件

发送端和接收端都会记录日志文件，日志文件的格式如下：

### 发送文件端

- type: 帧的类型，有Send, Recv
- pdu_to_send: 发送的帧的序号
- acked_no: 发送文件端希望接收文件端确认的帧号 (该帧号-1则是已被确认的帧号，累计确认)
- data_size: 数据的大小
- status: 当前帧的状态，有New, Timeout, ReTransmit
  - New 表示新发送的帧
  - Timeout 表示超时重传
  - ReTransmit 表示重传
- time: 发送当前帧的时间戳

> 发送文件端

### 接收文件端

- type: 帧的类型，有Send, Recv
- pdu_recv: 发送的帧的序号
- pdu_exp: 接受文件端希望发送文件端发送的帧号
- data_size: 数据的大小
- status: 当前帧的状态，有DataErr, NoErr, OK
  - DataErr 表示数据出错
  - NoErr 表示数据没有出错
  - OK 表示数据正确
- time: 接收当前帧的时间戳

### 具体设计

| 文档要求 | 实际代码 | 含义 | 变化 |
| --- | --- | --- | --- |
| pdu_to_send | send_no | 发送端发送的data frame的序号 | 每当发送一个帧，send_no+1 |
| acked_no | recv_ack_no | 发送端希望接收端确认的data frame的序号 | 每当接收到一个ACK，ack_no+1 |
| pdu_recv | recv_no | 接收端希望发送端发送的data frame的序号 | 每当接收到一个帧，recv_no+1 |
| pdu_exp | send_ack_no | 接收端发送的data frame的序号 | 每当发送一个ACK，send_ack_no+1 |

下面用代码来解释一下：

```python
# 发送端
send_no = 1
recv_ack_no = 1
pdu = PDU(frame_no = send_no, ack_no = recv_ack_no, data)
send_pdu(pdu)
send_no += 1

# 👇

# 接收端
recv_no = 1
send_ack_no = 1
pdu = recv_pdu()
if recv_no == pdu.frame_no:
  recv_no += 1
  ack = PDU(frame_no = send_ack_no, ack_no = recv_no)
  send_ack(ack)
  send_ack_no += 1

# 👇

# 发送端
send_no = 2
recv_ack_no = 1
ack = recv_pdu()
if send_no == ack.ack_no:
  recv_ack_no += 1

# Finally
send_no = 2
recv_ack_no = 2
recv_no = 2
send_ack_no = 2
```