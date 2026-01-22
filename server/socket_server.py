import socket
import json
from handlers import handle_request

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 4096


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen(10)

    print(f"✅ Socket server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"📥 Client connected: {addr}")

        buffer = ""

        try:
            # 🔁 KEEP CONNECTION ALIVE
            while True:
                data = client_socket.recv(BUFFER_SIZE)

                if not data:
                    break  # client disconnected

                buffer += data.decode()

                # 🔑 Process full messages (newline-delimited)
                while "\n" in buffer:
                    raw_request, buffer = buffer.split("\n", 1)

                    if not raw_request.strip():
                        continue

                    try:
                        request_data = json.loads(raw_request)
                        response = handle_request(request_data)
                    except json.JSONDecodeError:
                        response = {
                            "status": "error",
                            "message": "Invalid JSON format"
                        }
                    except Exception as e:
                        response = {
                            "status": "error",
                            "message": str(e)
                        }

                    response_json = json.dumps(response) + "\n"
                    client_socket.sendall(response_json.encode())

        except Exception as e:
            print("❌ Client error:", e)

        finally:
            print(f"🔌 Client disconnected: {addr}")
            client_socket.close()


if __name__ == "__main__":
    start_server()
