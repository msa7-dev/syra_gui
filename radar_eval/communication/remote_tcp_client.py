# import socket
# import threading
# import time
# import paramiko

# class SYRA_TCP_CLIENT:
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.start_remote_scripte("~/test.py")
#         self.connected = False
#         self.acquisition_active = threading.Event()
#         self.acquisition_thread = None

#     def start_remote_scripte(self, script_path):
#         try:
#             client = paramiko.SSHClient()
#             client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#             client.connect(self.host, 22, self.username, self.password)
#             stdin, stdout, stderr = client.exec_command(f'sudo python3 -B {script_path} &')
#             print(stdout.read().decode())
#             print(stderr.read().decode())
#             client.close()
#         except Exception as e:
#             print(f"SSH connection error: {e}")

#     def connect(self):
#         self.socket.connect((self.host, self.port))
#         self.connected = True
#         threading.Thread(target=self.listen_to_server, daemon=True).start()
#         print("Connected to server")

#     def listen_to_server(self):
#         while self.connected:
#             data = self.socket.recv(64).decode()
#             # if data == cmd:
#                 # self.handle_command(data)
#             # elif data == data_cmd:
#                 # data_frame = self.socket.recv(frame_len).decode()


#     def handle_command(self, command):
#         if command == "connect_sensor":
#             self.connect_sensor()
#         elif command.startswith("start_acquisition"):
#             _, fps = command.split()
#             self.start_data_acquisition(int(fps))
#         elif command == "stop_acquisition":
#             self.stop_data_acquisition()
#         elif command == "disconnect":
#             self.disconnect()
#         else:
#             print(f"Unknown command: {command}")

#     def connect_sensor(self):
#         # Implement sensor connection logic here
#         print("Sensor connected")

#     def start_data_acquisition(self, fps):
#         self.acquisition_active.set()
#         if not self.acquisition_thread or not self.acquisition_thread.is_alive():
#             self.acquisition_thread = threading.Thread(target=self.acquisition, args=(fps,), daemon=True)
#             self.acquisition_thread.start()

#     def acquisition(self, fps):
#         while self.acquisition_active.is_set():
#             frame = self.collect_usb_data()
#             self.send_data(frame)
#             time.sleep(1 / fps)

#     def stop_data_acquisition(self):
#         self.acquisition_active.clear()
#         if self.acquisition_thread:
#             self.acquisition_thread.join()
#             self.acquisition_thread = None

#     def collect_usb_data(self):
#         # Dummy function to simulate USB data collection
#         return "dummy_data"

#     def send_data(self, data):
#         if self.connected:
#             self.socket.sendall(data.encode())

#     def disconnect(self):
#         if self.socket:
#             self.socket.close()
#             self.connected = False
#             print("Disconnected from server")

# if __name__ == "__main__":
#     client = SYRA_TCP_CLIENT('192.168.188.21', 12345)
#     client.connect()
