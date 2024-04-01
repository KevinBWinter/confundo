import argparse
import socket
import struct
import time
import sys

# Constants
HEADER_FORMAT = '!I I H H'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
SYN = 0b001
ACK = 0b010
FIN = 0b100
MAX_SEQ_NUM = 50000
DEFAULT_MTU = 412
RETRANSMISSION_TIMEOUT = 0.5
MAX_IDLE_TIME = 10
CWND = 412
SSTHRESH = 12000

class ConfundoSocket:
    def __init__(self, dest_ip, dest_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(MAX_IDLE_TIME)
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.seq_num = 50000
        self.ack_num = 0
        self.connection_id = 0
        self.connected = False
        self.cwnd = CWND
        self.ssthresh = SSTHRESH

    def connect(self):
        self._send_packet(flags=SYN)
        self.seq_num = (self.seq_num + 1) % MAX_SEQ_NUM

        while True:
            seq_num, ack_num, connection_id, flags, _ = self._receive_packet()
            if flags & SYN and flags & ACK:
                self.ack_num = ack_num
                self.connection_id = connection_id
                break

        self._send_packet(flags=ACK)
        self.connected = True

    def send_file(self, filename):
        with open(filename, 'rb') as file:
            data = file.read(self.cwnd)
            while data:
                self._send_packet(payload=data)
                self.seq_num = (self.seq_num + len(data)) % MAX_SEQ_NUM

                while True:
                    _, ack_num, _, flags, _ = self._receive_packet()
                    if flags & ACK and ack_num == self.seq_num:
                        break

                if self.cwnd < self.ssthresh:
                    self.cwnd += DEFAULT_MTU
                else:
                    self.cwnd += int(DEFAULT_MTU * DEFAULT_MTU / self.cwnd)

                data = file.read(self.cwnd)

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

def main():
    parser = argparse.ArgumentParser(description="Confundo Protocol Client")
    parser.add_argument("host", help="Hostname or IP address of the server")
    parser.add_argument("port", type=int, help="Port number of the server")
    parser.add_argument("file", help="Path to the file to send")
    args = parser.parse_args()

    try:
        client_socket = ConfundoSocket(args.host, args.port)
        client_socket.connect()
        client_socket.send_file(args.file)
        client_socket.close()
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
