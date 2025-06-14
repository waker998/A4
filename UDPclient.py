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
   

            
