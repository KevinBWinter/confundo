import sys
import argparse
import confundo.socket as csocket

def main():
    parser = argparse.ArgumentParser(description="Confundo Protocol Server")
    parser.add_argument("host", help="Hostname or IP address to bind to")
    parser.add_argument("port", type=int, help="Port number to bind to")
    parser.add_argument("output_file", help="Path to save the received file")
    args = parser.parse_args()

    try:
        with csocket.Socket() as server_socket:
            server_socket.bind((args.host, args.port))
            server_socket.listen(1)
            client_socket, _ = server_socket.accept()
            with open(args.output_file, "wb") as file:
                while True:
                    data = client_socket.recv(412)
                    if not data:
                        break
                    file.write(data)
            client_socket.close()
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
