import argparse
import socket
import struct
import sys

# Constants
HEADER_FORMAT = '!I I H H'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
SYN = 0b001
ACK = 0b010
FIN = 0b100
MAX_SEQ_NUM = 50000
DEFAULT_MTU = 412

class ConfundoSocket:
    def __init__(self, listen_ip, listen_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((listen_ip, listen_port))
        self.seq_num = 50000
        self.ack_num = 0
        self.connection_id = 0
        self.connected = False

    def listen(self):
        while True:
            seq_num, ack_num, connection_id, flags, _ = self._receive_packet()
            if flags & SYN:
                self.ack_num = (seq_num + 1) % MAX_SEQ_NUM
                self.connection_id = connection_id
                self._send_packet(flags=SYN | ACK)
                self.connected = True
            elif self.connected and flags & ACK:
                break

    def receive_file(self, output_file):
        with open(output_file, 'wb') as file:
            while True:
                seq_num, ack_num, _, flags, payload = self._receive_packet()
                if flags & FIN:
                    self.ack_num = (seq_num + 1) % MAX_SEQ_NUM
                    self._send_packet(flags=ACK)
                    break
                if seq_num == self.ack_num:
                    file.write(payload)
                    self.ack_num = (self.ack_num + len(payload)) % MAX_SEQ_NUM
                    self._send_packet(flags=ACK)

    def close(self):
        self.connected = False
        self.sock.close()

    def _send_packet(self, payload=b'', flags=0):
        header = struct.pack(HEADER_FORMAT, self.seq_num, self.ack_num, self.connection_id, flags)
        packet = header + payload
        self.sock.sendto(packet, self.sock.getsockname())

    def _receive_packet(self):
        packet, _ = self.sock.recvfrom(DEFAULT_MTU + HEADER_SIZE)
        seq_num, ack_num, connection_id, flags = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
        payload = packet[HEADER_SIZE:]
        return seq_num, ack_num, connection_id, flags, payload

def main():
    parser = argparse.ArgumentParser(description="Confundo Protocol Server")
    parser.add_argument("host", help="Hostname or IP address to bind to")
    parser.add_argument("port", type=int, help="Port number to bind to")
    parser.add_argument("output_file", help="Path to save the received file")
    args = parser.parse_args()

    try:
        server_socket = ConfundoSocket(args.host, args.port)
        server_socket.listen()
        server_socket.receive_file(args.output_file)
        server_socket.close()
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
