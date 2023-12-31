import os
import socket
import threading
from pathlib import Path
import mimetypes
import logging
import time
import configparser

logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.DEBUG)

# ALLOWED_EXTENSIONS = {".html", ".txt", ".js", ".css"} # to jest niepotrzebne chyba bo chodzi o obsluge wszsytkich plikow statycznych

config = configparser.ConfigParser()
config.read('server_config.ini')

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        headers = request.split('\n')

        if not headers[0]:
            print("Puste żądanie")
            return

        split_header = headers[0].split()
        if len(split_header) < 2:
            print("Niekompletne żądanie")
            return

        http_method = split_header[0]
        filename = split_header[1]

        if filename == "/":
            filename = "/index.html"

        root_dir = Path('htdocs').resolve()
        filepath = root_dir.joinpath(filename.lstrip("/")).resolve()

        # if filepath.suffix not in ALLOWED_EXTENSIONS:
        #     raise PermissionError("File type not allowed")

        try:
            filepath.relative_to(root_dir) #sprawdzam sobie czy jest w katalogu htdocs

            if http_method.upper() == "GET":
                with open(filepath, 'rb') as fin:
                    content = fin.read()
                response_code = '200 OK'
            elif http_method.upper() == "HEAD":
                content = b""
                response_code = '200 OK'
            else:
                content = b""
                response_code = '501 Not Implemented'



        except FileNotFoundError:
            response_code = '404 NOT FOUND'
            content = b"File Not Found"
        except (IsADirectoryError, PermissionError):
            response_code = '403 FORBIDDEN'
            content = b"Access Denied"
        except Exception as e:
            response_code = '500 INTERNAL SERVER ERROR'
            content = b"Internal Server Error"
            logging.error(f"Error handling request: {e}")

        mime_type, _ = mimetypes.guess_type(str(filepath))
        response = f'HTTP/1.0 {response_code}\n'
        if mime_type:
            response += f'Content-Type: {mime_type}\n'
        response += '\n'
        client_socket.send(response.encode() + content)

        logging.info(f"{time.asctime()} - {http_method} {filename} {response_code}")

    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()

def main():
    bind_ip = config.get('DEFAULT', 'bind_ip')
    bind_port = config.getint('DEFAULT', 'bind_port')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)

    print(f"[*] Listening on {bind_ip}:{bind_port}")

    try:
        while True:
            client, addr = server.accept()
            print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.start()
    except Exception as e:
        logging.error(f"Error accepting connection: {e}")
    finally:
        server.close()


if __name__ == "__main__":
    main()
# TODO: sprawdzic wiresharkiem czy wszystko git