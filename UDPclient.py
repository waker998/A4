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