import sys
import argparse
import confundo.socket as csocket

def main():
    parser = argparse.ArgumentParser(description="Confundo Protocol Client")
    parser.add_argument("host", help="Hostname or IP address of the server")
    parser.add_argument("port", type=int, help="Port number of the server")
    parser.add_argument("file", help="Path to the file to send")
    args = parser.parse_args()

    try:
        with csocket.Socket() as sock:
            sock.connect((args.host, args.port))
            with open(args.file, "rb") as file:
                while True:
                    data = file.read(412)
                    if not data:
                        break
                    sock.send(data)
            sock.close()
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
