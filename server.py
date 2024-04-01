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
            elif self.connected and
