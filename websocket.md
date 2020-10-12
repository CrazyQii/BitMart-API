# Websocket

**WebSocket 协议本质上是一个基于 TCP 的协议。**

*为了建立一个 WebSocket 连接，客户端浏览器首先要向服务器发起一个 HTTP 请求，这个请求和通常的 HTTP 请求不同，包含了一些附加头信息，其中附加头信息"Upgrade: WebSocket"表明这是一个申请协议升级的 HTTP 请求，服务器端解析这些附加的头信息然后产生应答信息返回给客户端，客户端和服务器端的 WebSocket 连接就建立起来了，双方就可以通过这个连接通道自由的传递信息，并且这个连接会持续存在直到客户端或者服务器端的某一方主动的关闭连接。*

**WebSocket 的出现，让服务器端可以主动向客户端发送信息，使得浏览器具备了实时双向通信的能力**

想要实现 `Websocket` 就需要先补充一些额外的知识

---
WebSocket 是独立的、创建在 TCP 上的协议。

Websocket 通过 HTTP/1.1 协议的101状态码进行握手。

为了创建Websocket连接，需要通过浏览器发出请求，之后服务器进行回应，这个过程通常称为“握手”（handshaking）。

**客户端请求**
```
GET / HTTP/1.1
Connection: Upgrade 表示要升级协议
Upgrade: websocket  表示要升级到websocket协议。
Host: example.com
Origin: http://example.com
Sec-WebSocket-Key: sN9cRrP/n9NdMgdcy2VJFQ==   与后面服务端响应首部的Sec-WebSocket-Accept是配套的，
提供基本的防护，比如恶意的连接，或者无意的连
Sec-WebSocket-Version: 13   里面包含服务端支持的版本号
```
**服务端回应**
```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: fFBooB7FAkLlXgRSz0BT3v4hq5s=
Sec-WebSocket-Location: ws://example.com/
```


### 异步IO

> 同步IO：在一个线程中，CPU执行代码的速度极快，然而，一旦遇到IO操作，如读写文件、发送网络数据时，就需要等待IO操作完成，才能继续进行下一步操作，这种情况是同步IO。

存在的问题：

*在IO操作的过程中，当前线程被挂起，而其他需要CPU执行的代码就无法被当前线程执行了。*

解决方案：

1. 多线程或多进程：每个用户都会分配一个线程，如果遇到IO导致线程被挂起，其他用户的线程不受影响。
2. 异步IO：当代码需要执行一个耗时的IO操作时，它只发出IO指令，并不等待IO结果，然后就去执行其他代码了。一段时间后，当IO返回结果时，再通知CPU进行处理。

**异步模型**

异步IO模型需要一个消息循环，在消息循环中，主线程不断地重复“读取消息-处理消息”这一过程：

```python
loop = get_event_loop()
while True:
    event = loop.get_event()
    process_event(event)
```

#### **协程（Coroutine）**

正常的函数调用是通过堆栈进行的，一个线程就是执行一个子程序。比如A调用B，B在执行过程中又调用了C，C执行完毕返回，B执行完毕返回，最后是A执行完毕。

但是**协程**不同之处在于，函数执行过程中，程序内部是能够被打断的，类似于CPU的中断。（函数执行中断，去执行其他函数，而不是调用函数）

#### python 异步标准库（asyncio）

[Python标准库]: https://docs.python.org/zh-cn/3/library/asyncio.html

| 参数                                         | 含义                                                |
| -------------------------------------------- | :-------------------------------------------------- |
| asyncio.get_event_loop()                     | 返回一个事件循环对象，是asyncio.BaseEventLoop的实例 |
| AbstractEventLoop.stop()                     | 停止运行事件循环                                    |
| AbstractEventLoop.run_forever()              | 一直运行，直到stop()                                |
| AbstractEventLoop.run_until_complete(future) | 运行直到Future对象运行完成                          |
| AbstractEventLoop.close()                    | 关闭事件循环                                        |
| AbstractEventLoop.is_running()               | 返回事件循环是否运行                                |
| AbstractEventLoop.close()                    | 关闭事件                                            |


- websocket-client 是一个websocket服务的client端模块，对新手较为友好，可以开箱即用

调用websocket-client 
`pip install websocket-client`

### 官方示例
#### 长连接

```python
import websocket
from threading import Thread
import time
import sys


class MyApp(websocket.WebSocketApp):
    def on_message(self, message):
        print(message)

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("### closed ###")

    def on_open(self):
        def run(*args):
            for i in range(3):
                # send the message, then wait
                # so thread doesn't exit and socket
                # isn't closed
                self.send("Hello %d" % i)
                time.sleep(1)

            time.sleep(1)
            self.close()
            print("Thread terminating...")

        Thread(target=run).start()


if __name__ == "__main__":
    websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = "ws://echo.websocket.org/"
    else:
        host = sys.argv[1]
    ws = MyApp(host)
    ws.run_forever()
```

**短连接**
```python
from websocket import create_connection
ws = create_connection("ws://echo.websocket.org/")
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()
```

[长连接、短连接、长轮询和WebSocket]: http://caibaojian.com/http-connection-and-websocket.html

- websockets是一个模块有server端和client端，涉及到协程以及异步

### Example 登录验证


调用websockets包
`pip install websockets`

**客户端**

```python
import websockets
import asyncio
async def client(url):

    async with websockets.connect(url) as wss:
		
        # 一直输入登陆直到成功
        while True:
            name = input('input your name')
            # 发送 name 到服务端
            await wss.send(name)
            # 接收服务端传送的数据
            resp = await wss.recv()
            if resp == 'True':
                break
            else:
                print(resp)

asyncio.get_event_loop().run_until_complete(client('ws://192.168.0.105:8765/'))
```

**服务端**

```python
import websockets
import asyncio
async def auth(websocket, path):
    while True:
        # 接收客户端传来的数据
        name = await websocket.recv()
        if name == 'hlq':
            # 验证成功，返回响应到客户端
            await websocket.send('True')
            return True
        else:
            await websocket.send('name is not exist')

# 启动服务器
start_server = websockets.serve(auth, '192.168.0.105', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
# 持续循环
asyncio.get_event_loop().run_forever()
```

