import socket
import sys
import base64
import os

class UDPClient:
    def __init__(self, hostname, port, file_list):
        self.server_host = hostname
        self.server_port = port
        self.file_list = file_list
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.initial_timeout = 1000  # 1 second in milliseconds
        self.max_retries = 5

    def send_and_receive(self, message, address, port, timeout=None):
        current_timeout = timeout if timeout else self.initial_timeout
        retries = 0
    
        while retries < self.max_retries:
            try:
                self.socket.settimeout(current_timeout / 1000)
                self.socket.sendto(message.encode(), (address, port))
                response, _ = self.socket.recvfrom(4096)
                return response.decode().strip()
            except socket.timeout:
                retries += 1
                current_timeout *= 2
                print(f"Timeout, retrying {retries}/{self.max_retries} with timeout {current_timeout}ms")
                continue
            except Exception as e:
                print(f"Error in send_and_receive: {e}")
                break

        print(f"Failed after {self.max_retries} retries")
        raise Exception("Max retries reached, giving up")