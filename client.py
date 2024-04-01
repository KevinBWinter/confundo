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
    def __init__(self, dest_ip, dest_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.seq_num = 50000
        self.ack_num = 0
        self.connection_id = 0
        self.connected = False

    def connect(self):
        self._send_packet(flags=SYN)
        self.seq_num = (self.seq_num + 1) % MAX_SEQ_NUM

        while True:
            _, ack_num, connection_id, flags, _ = self._receive_packet()
            if flags & SYN and flags & ACK:
                self.ack_num = ack_num
                self.connection_id = connection_id
                break

        self._send_packet(flags=ACK)
        self.connected = True

    def send_file(self, filename):
        with open(filename, 'rb') as file:
            while True:
                data = file.read(DEFAULT_MTU)
                if not data:
                    break

                self._send_packet(payload=data)
                self.seq_num = (self.seq_num + len(data)) % MAX_SEQ_NUM

                while True:
                    _, ack_num, _, flags, _ = self._receive_packet()
                    if flags & ACK and ack_num == self.seq_num:
                        break

    def close(self):
        self._send_packet(flags=FIN)
        self.seq_num = (self.seq_num + 1) % MAX_SEQ_NUM

        while True:
            _, ack_num, _, flags, _ = self._receive_packet()
            if flags & ACK and ack_num == self.seq_num:
                break

        self.connected = False
        self.sock.close()

    def _send_packet(self, payload=b'', flags=0):
        header = struct.pack(HEADER_FORMAT, self.seq_num, self.ack_num, self.connection_id, flags)
        packet = header + payload
        self.sock.sendto(packet, (self.dest_ip, self.dest_port))

    def _receive_packet(self):
        packet, _ = self.sock.recvfrom(DEFAULT_MTU + HEADER_SIZE)
        seq_num, ack_num, connection_id, flags = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
        payload = packet[HEADER_SIZE:]
        return seq_num, ack_num, connection_id, flags, payload

def main(hostname, port, filename):
    client_socket = ConfundoSocket(hostname, port)
    client_socket.connect()
    client_socket.send_file(filename)
    client_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit("Usage: python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>")

    hostname, port, filename = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    main(hostname, port, filename)
