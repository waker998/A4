import socket
import threading
import random
import os
import base64

class UDPServer:
    def __init__(self, port):
        self.welcome_port = port
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.welcome_socket.bind(('', self.welcome_port))
        print(f"Server started on port {self.welcome_port}")