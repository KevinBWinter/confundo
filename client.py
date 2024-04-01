import socket
import struct
import sys
import time

# Constants
DEFAULT_MTU = 412
DEFAULT_CWND = 412
DEFAULT_SSTHRESH = 12000
MAX_SEQ_NUM = 50000
SYN = 0b001
ACK = 0b010
FIN = 0b100
HEADER_FORMAT = '!I I H H'  # Sequence Number, Acknowledgment Number, Connection ID, Flags
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
RETRANSMISSION_TIMEOUT = 0.5
FIN_WAIT_TIME = 2
MAX_IDLE_TIME = 10

# Confundo Socket class
class ConfundoSocket:
    def __init__(self, dest_ip, dest_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.seq_num = 50000
        self.ack_num = 0
        self.connection_id = 0
        self.cwnd = DEFAULT_CWND
        self.ssthresh = DEFAULT_SSTHRESH
        self.connected = False
        self.sock.settimeout(MAX_IDLE_TIME)

    def connect(self):
        # Send SYN packet
        self._send_packet(flags=SYN)
        self.seq_num = (self.seq_num + 1) % MAX_SEQ_NUM

        # Wait for SYN-ACK packet
        while True:
            try:
                _, ack_num, connection_id, flags, _ = self._receive_packet()
                if flags & SYN and flags & ACK:
                    self.ack_num = ack_num
                    self.connection_id = connection_id
                    break
            except socket.timeout:
                # Retransmit SYN packet
                self._send_packet(flags=SYN)

        # Send ACK packet
        self._send_packet(flags=ACK)
        self.connected = True

    def send_file(self, filename):
        with open(filename, 'rb') as file:
            while True:
                if not self.connected:
                    print("Connection lost")
                    return

                data = file.read(self.cwnd)
                if not data:
                    break

                # Send data
                self._send_packet(payload=data)
                self.seq_num = (self.seq_num + len(data)) % MAX_SEQ_NUM

                # Wait for ACK
                start_time = time.time()
                while True:
                    try:
                        _, ack_num, _, flags, _ = self._receive_packet()
                        if flags & ACK and ack_num == self.seq_num:
                            break
                    except socket.timeout:
                        if time.time() - start_time > RETRANSMISSION_TIMEOUT:
                            # Retransmit data
                            self.ssthresh = max(self.cwnd // 2, DEFAULT_CWND)
                            self.cwnd = DEFAULT_CWND
                            self._send_packet(payload=data)
                            start_time = time.time()

                # Update congestion window
                if self.cwnd < self.ssthresh:
                    self.cwnd += DEFAULT_CWND  # Slow start
                else:
                    self.cwnd += DEFAULT_CWND * DEFAULT_CWND // self.cwnd  # Congestion avoidance

    def close(self):
        # Send FIN packet
        self._send_packet(flags=FIN)
        self.seq_num = (self.seq_num + 1) % MAX_SEQ_NUM

        # Wait for ACK
        while True:
            try:
                _, ack_num, _, flags, _ = self._receive_packet()
                if flags & ACK and ack_num == self.seq_num:
                    break
            except socket.timeout:
                # Retransmit FIN packet
                self._send_packet(flags=FIN)

        # Wait for FIN from server
        self.sock.settimeout(FIN_WAIT_TIME)
        while True:
            try:
                _, _, _, flags, _ = self._receive_packet()
                if flags & FIN:
                    # Send ACK for server's FIN
                    self._send_packet(flags=ACK)
            except socket.timeout:
                break

        self.connected = False
        self.sock.close()

    def _send_packet(self, payload=b'', flags=0):
        # Construct and send a packet with the given payload and flags
        header = struct.pack(HEADER_FORMAT, self.seq_num, self.ack_num, self.connection_id, flags)
        packet = header + payload
        self.sock.sendto(packet, (self.dest_ip, self.dest_port))

    def _receive_packet(self):
        # Receive and parse a packet
        packet, _ = self.sock.recvfrom(DEFAULT_MTU + HEADER_SIZE)
        seq_num, ack_num, connection_id, flags = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
        payload = packet[HEADER_SIZE:]
        return seq_num, ack
