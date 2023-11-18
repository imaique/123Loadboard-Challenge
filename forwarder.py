import socket
import threading
import queue
import json

PORT = 8080


class Forwarder:
    def __init__(self) -> None:
        self.message_queue = queue.Queue()
        threading.Thread(target=self.listen, daemon=True).start()
        self.message_queue.join()
        pass

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", PORT))
        sock.listen(5)
        sock.settimeout(0.2)
        print("listen")
        while True:
            try: 
                client, _ = sock.accept() 
                self.handle_client(client)
            except socket.timeout:
                pass 
            except Exception as e:
                break
        
    def handle_client(self, client):
        try:
            while True:
                message = self.message_queue.get()
                client.send(json.dumps(message).encode())
                print("Sent message:", message['seq'])
                self.message_queue.task_done()
        except Exception as e:
            print("Client disconnected:", e)
        finally:
            client.close()

    def add_message(self, message) -> None:
        self.message_queue.put(message)

