import socket
import struct
import sys

# Constants
DEFAULT_MTU = 412
HEADER_FORMAT = '!I I H H'  # Sequence Number, Acknowledgment Number, Connection ID, Flags
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
SYN = 0b001
ACK = 0b010
FIN = 0b100
MAX_SEQ_NUM = 50000

class ConfundoSocket:
    def __init__(self, listen_ip, listen_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((listen_ip, listen_port))
        self.connection_id = 0
        self.expected_seq_num = 0
        self.ack_num = 0
        self.connected = False

    def listen(self):
        while True:
            packet, client_address = self.sock.recvfrom(DEFAULT_MTU + HEADER_SIZE)
            seq_num, ack_num, connection_id, flags = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
            payload = packet[HEADER_SIZE:]

            if flags & SYN:
                self.connection_id = connection_id
                self.expected_seq_num = (seq_num + 1) % MAX_SEQ_NUM
                self.ack_num = self.expected_seq_num
                self._send_packet(client_address, flags=SYN | ACK)
                self.connected = True
            elif self.connected and flags & ACK and seq_num == self.expected_seq_num:
                self.expected_seq_num = (self.expected_seq_num + len(payload)) % MAX_SEQ_NUM
                self.ack_num = self.expected_seq_num
                self._send_packet(client_address, flags=ACK)
            elif self.connected and flags & FIN:
                self.connected = False
                self._send_packet(client_address, flags=ACK)
                break

    def _send_packet(self, client_address, flags=0):
        header = struct.pack(HEADER_FORMAT, self.ack_num, 0, self.connection_id, flags)
        self.sock.sendto(header, client_address)

def main(listen_ip, listen_port, output_filename):
    server_socket = ConfundoSocket(listen_ip, listen_port)
    with open(output_filename, 'wb') as output_file:
        for payload in server_socket.listen():
            output_file.write(payload)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit("Usage: python3 server.py <LISTEN-IP> <LISTEN-PORT> <OUTPUT-FILENAME>")

    listen_ip, listen_port, output_filename = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    main(listen_ip, listen_port, output_filename)
