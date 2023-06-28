import socket
import threading
import os
import mimetypes

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    headers = request.split('\n')
    filename = headers[0].split()[1]

    if filename == "/":
        filename = "/index.html"

    filepath = 'htdocs' + filename
    try:
        with open(filepath, 'rb') as fin:  # Use 'rb' to read binary files
            content = fin.read()

        mime_type, _ = mimetypes.guess_type(filepath)
        response = 'HTTP/1.0 200 OK\n'
        if mime_type:
            response += f'Content-Type: {mime_type}\n'
        response += '\n'
        client_socket.send(response.encode() + content)  # Send header and file content
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\n\n File Not Found'
        client_socket.send(response.encode())

    client_socket.close()

def main():
    bind_ip = "0.0.0.0"
    bind_port = 8001

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)

    print(f"[*] Listening on {bind_ip}:{bind_port}")

    while True:
        client, addr = server.accept()
        print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    main()
