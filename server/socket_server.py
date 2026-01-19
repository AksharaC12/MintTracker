import socket
import threading
import json
from handlers import handle_request

HOST = "0.0.0.0"
PORT = 5000

def client_handler(conn, addr):
    print(f"[CONNECTED] {addr}")

    try:
        while True:
            data = conn.recv(4096).decode()

            if not data:
                break

            print(f"[REQUEST] {data}")

            request = json.loads(data)
            response = handle_request(request)

            conn.sendall(json.dumps(response).encode())

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[STARTED] MintTracker Socket Server running on port {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(
            target=client_handler,
            args=(conn, addr),
            daemon=True
        )
        thread.start()


if __name__ == "__main__":
    start_server()
