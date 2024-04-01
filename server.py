import sys
import argparse

import confundo.socket as socket

def start():
    parser = argparse.ArgumentParser("Parser")
    parser.add_argument("host", help="Set Hostname")
    parser.add_argument("port", help="Set Port Number", type=int)
    parser.add_argument("output_file", help="Set Output File")
    args = parser.parse_args()

    try:
        with socket.Socket() as server_socket:
            server_socket.bind((args.host, args.port))
            server_socket.listen(1)
            client_socket, _ = server_socket.accept()

            with open(args.output_file, "wb") as f:
                while True:
                    data = client_socket.recv(50000)
                    if not data:
                        break
                    f.write(data)
    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()
