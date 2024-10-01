import socket
import threading

class SYRA_TCP_SERVER:
    def __init__(self, 
                 host: str,
                 port: str,
                 username: str,
                 password: str):
        self.host = str(host)
        self.port = int(port)
        self.username = str(username)
        self.password = str(password)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        print(f"Server listening on {host}:{port}")

    def handle_client(self, client_socket):
        while self.running:
            try:
                command = input("Enter command to send ('connect_sensor', 'start_acquisition [fps]', 'stop_acquisition', 'disconnect'): ")
                client_socket.send(command.encode())
                if command == "disconnect":
                    break
            except Exception as e:
                print(f"Error sending command: {e}")
                break

    def start(self):
        self.socket.settimeout(1)  # Set a timeout for the accept call
        while self.running:
            try:
                client_sock, address = self.socket.accept()
                print(f"Accepted connection from {address}")
                client_handler = threading.Thread(target=self.handle_client, args=(client_sock,))
                client_handler.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def close(self):
        self.running = False
        self.socket.close()
        print("Server closed")

if __name__ == "__main__":
    client = SYRA_TCP_SERVER('0,0,0,0', 22)
    client.connect()

