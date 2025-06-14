import socket
import threading
import random
import os
import base64
import sys

class UDPServer:
    def __init__(self, port):
        self.welcome_port = port
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.welcome_socket.bind(('', self.welcome_port))
        print(f"Server started on port {self.welcome_port}")
    def start(self):
        while True:
            try:
                data, client_address = self.welcome_socket.recvfrom(1024)
                client_request = data.decode().strip()
                print(f"Received from {client_address}: {client_request}")
                
                parts = client_request.split()
                if len(parts) < 2 or parts[0] != "DOWNLOAD":
                    continue
                
                filename = parts[1]
                if not os.path.exists(filename):
                    response = f"ERR {filename} NOT_FOUND"
                    self.welcome_socket.sendto(response.encode(), client_address)
                    continue
                
                file_size = os.path.getsize(filename)
                data_port = random.randint(50000, 51000)
                
                response = f"OK {filename} SIZE {file_size} PORT {data_port}"
                self.welcome_socket.sendto(response.encode(), client_address)
                
                threading.Thread(target=self.handle_file_transmission, 
                                args=(filename, client_address, data_port)).start()
            except Exception as e:
                print(f"Error in main server loop: {e}")
                break
                
        raise Exception("Max retries reached, giving up")
    def download_file(self, filename):
        try:
            # Step 1: Send DOWNLOAD request
            download_msg = f"DOWNLOAD {filename}"
            response = self.send_and_receive(download_msg, self.server_host, self.server_port)    
            parts = response.split()
            if parts[0] == "ERR":
                print(f"Error: {response}")
                return False
                
            if parts[0] != "OK" or parts[1] != filename:
                print(f"Invalid response: {response}")
                return False
                
            # Parse response
            file_size = int(parts[3])
            data_port = int(parts[5])
            print(f"Downloading {filename} (size: {file_size} bytes)")

            # Step 2: Download file in chunks
            with open(filename, 'wb') as file:
                bytes_received = 0
                block_size = 1000  # bytes per chunk
                
                while bytes_received < file_size:
                    start = bytes_received
                    end = min(bytes_received + block_size - 1, file_size - 1)
                    
                    file_msg = f"FILE {filename} GET START {start} END {end}"
                    response = self.send_and_receive(file_msg, self.server_host, data_port)
                    
                    resp_parts = response.split()
                    if resp_parts[0] != "FILE" or resp_parts[1] != filename or resp_parts[2] != "OK":
                        print(f"Invalid file response: {response}")
                        return False
                        
                    data_start = response.find("DATA") + 5
                    base64_data = response[data_start:]
                    chunk = base64.b64decode(base64_data)
                    file.seek(start)
                    file.write(chunk)
                    
                    bytes_received += len(chunk)
                    print("*", end='', flush=True)
                
                print()  # New line after progress stars

                # Step 3: Send CLOSE message
                close_msg = f"FILE {filename} CLOSE"
                response = self.send_and_receive(close_msg, self.server_host, data_port)
                
                if response != f"FILE {filename} CLOSE_OK":
                    print(f"Invalid close response: {response}")
                    return False
                    
            print(f"Successfully downloaded {filename}")
            return True
            
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return False
    def run(self):
        try:
            with open(self.file_list, 'r') as f:
                files = [line.strip() for line in f if line.strip()]
                
            for filename in files:
                self.download_file(filename)
                
        except FileNotFoundError:
            print(f"Error: File list '{self.file_list}' not found")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.socket.close()
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 UDPclient.py <hostname> <port> <file_list>")
        sys.exit(1)
    
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    file_list = sys.argv[3]
    
    client = UDPClient(hostname, port, file_list)
    client.run()           