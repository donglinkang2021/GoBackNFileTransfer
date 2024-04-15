# GBN实现可靠文件传输

> 从网上大概看了一下别人实现的代码，大概知道了一下方向，规划一下自己目前计划

- [ ] 调研实现GBN还需要用到哪些库
  - [x] socket
  - [x] struct
  - [x] thread
- [ ] 开始学习基础的socket编程
  - [x] 先实现简单的文件传输功能 (实现了本机中windows的简单传输)
  - [x] 实现了向虚拟机中传输文件
- [ ] 学习基础的struct库
  - [x] 使用struct库来实现数据的打包和解包
  - [x] 实现了自己的CRC校验
  - [x] 实现了自定义的packet结构
- [ ] 使用自己定义的基础pdu来用UDP传数据
  - [x] 学习UDP传输是怎么传的 写了各种简单的UDP传输异步收发信息
  - [x] 现在本地实现文件如何打包成packet
  - [x] 先传一个简单的packet (在linux和windows之间)
  - [x] 传packet并获得ack
