import socket
import threading
import os
import sys
import time

class UDPServer:
    def __init__(self, port):
        """自动处理端口冲突的初始化"""
        self.port = port
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind(('', self.port))
                print(f"服务器成功启动于端口 {self.port}")
                return
            except OSError as e:
                if attempt == max_attempts - 1:
                    print(f"无法绑定端口 {self.port}，错误：{e}")
                    sys.exit(1)
                print(f"端口 {self.port} 被占用，尝试端口 {self.port + 1}...")
                self.port += 1
                time.sleep(1)

    def handle_download(self, filename, client_addr):
        """处理文件下载请求（二进制模式）"""
        try:
            print(f"处理请求: {filename}")
            if not os.path.exists(filename):
                error_msg = f"ERR {filename} NOT_FOUND"
                self.socket.sendto(error_msg.encode(), client_addr)
                return

            # 二进制模式读取文件
            with open(filename, 'rb') as f:
                file_data = f.read()
                file_size = len(file_data)
                ok_msg = f"OK {filename} SIZE {file_size}"
                self.socket.sendto(ok_msg.encode(), client_addr)
                print(f"已发送文件头: {filename} ({file_size} bytes)")

        except Exception as e:
            print(f"处理下载时出错: {e}")

    def run(self):
        """主服务器循环"""
        print("等待客户端连接...")
        try:
            while True:
                data, addr = self.socket.recvfrom(1024)
                message = data.decode().strip()
                if message.startswith("DOWNLOAD"):
                    filename = message.split()[1]
                    threading.Thread(target=self.handle_download, args=(filename, addr)).start()
        except KeyboardInterrupt:
            print("\n服务器关闭中...")
        finally:
            self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python UDPserver.py <端口>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        server = UDPServer(port)
        server.run()
    except ValueError:
        print("错误: 端口必须是数字")
    except Exception as e:
        print(f"服务器错误: {e}")