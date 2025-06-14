import socket
import os
import sys
import base64

class UDPClient:
    def __init__(self, hostname, port, file_list):
        """初始化客户端"""
        print(f"连接服务器: {hostname}:{port}")
        self.server_host = hostname
        self.server_port = port
        self.file_list = file_list
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5.0)

    def reliable_transfer(self, message, max_retries=3):
        """可靠传输（自动重试）"""
        retries = 0
        while retries < max_retries:
            try:
                self.socket.sendto(message.encode(), (self.server_host, self.server_port))
                response, _ = self.socket.recvfrom(4096)
                return response.decode().strip()
            except socket.timeout:
                retries += 1
                print(f"超时，重试 {retries}/{max_retries}...")
        raise Exception("传输失败：达到最大重试次数")

    def download_file(self, filename):
        """下载文件（二进制模式）"""
        print(f"\n开始下载: {filename}")
        try:
            # 1. 发送下载请求
            response = self.reliable_transfer(f"DOWNLOAD {filename}")
            
            # 2. 解析响应
            if response.startswith("ERR"):
                print(f"错误: {response}")
                return False
                
            parts = response.split()
            if parts[0] != "OK":
                print(f"无效响应: {response}")
                return False

            file_size = int(parts[3])
            print(f"文件大小: {file_size} bytes")

            # 3. 二进制模式创建文件
            with open(filename, 'wb') as f:
                print(f"保存到: {os.path.abspath(filename)}")
                received = 0
                while received < file_size:
                    # 4. 请求数据块
                    chunk_msg = f"GET {filename} {received} {min(received+1024, file_size)}"
                    data_response = self.reliable_transfer(chunk_msg)
                    
                    # 5. 处理二进制数据
                    if not data_response.startswith("DATA"):
                        print(f"无效数据包: {data_response[:50]}...")
                        return False
                        
                    chunk_data = base64.b64decode(data_response.split(maxsplit=1)[1])
                    f.write(chunk_data)
                    received += len(chunk_data)
                    print(f"进度: {received}/{file_size} bytes", end='\r')

            print(f"\n下载完成: {filename}")
            return True

        except Exception as e:
            print(f"下载失败: {e}")
            if os.path.exists(filename):
                os.remove(filename)
            return False

    def run(self):
        """主客户端逻辑"""
        try:
            # 使用UTF-8读取文件列表
            with open(self.file_list, 'r', encoding='utf-8') as f:
                files = [line.strip() for line in f if line.strip()]
                
            for filename in files:
                self.download_file(filename)
                
        except FileNotFoundError:
            print(f"错误: 文件列表 '{self.file_list}' 不存在")
        except Exception as e:
            print(f"客户端错误: {e}")
        finally:
            self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("使用方法: python UDPclient.py <主机> <端口> <文件列表>")
        sys.exit(1)

    try:
        client = UDPClient(sys.argv[1], int(sys.argv[2]), sys.argv[3])
        client.run()
    except ValueError:
        print("错误: 端口必须是数字")
    except Exception as e:
        print(f"启动失败: {e}")