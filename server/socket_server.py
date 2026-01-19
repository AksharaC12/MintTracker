import socket
import threading
import json
from handlers import handle_request

HOST = "0.0.0.0"
PORT = 5000


def client_handler(conn, addr):
    print(f"[CONNECTED] {addr}")
    buffer = ""

    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break

            buffer += data

            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                request = json.loads(message)
                response = handle_request(request)

                conn.sendall((json.dumps(response) + "\n").encode())

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("[STARTED] Socket server on port 5000")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=client_handler,
            args=(conn, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    start_server()
