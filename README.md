# confundo
Confundo Protocol Project

Kevin Winter
6332082

Overview
In this project, we've created a simplified version of a transport protocol called Confundo, which operates over UDP (User Datagram Protocol). UDP is a communication protocol used on the internet that allows data to be sent between devices. Unlike TCP (Transmission Control Protocol), UDP is connectionless, meaning it doesn't require a connection to be established before data can be sent. This makes UDP faster but less reliable. Our Confundo protocol adds some reliability features to UDP, making sure that data gets from one computer to another correctly.

Key Components
client.py: This file contains the code for the client application. The client is responsible for initiating the connection, sending a file to the server, and then closing the connection. It does this by sending special packets with flags like SYN (synchronize), ACK (acknowledge), and FIN (finish) to manage the connection state.

server.py: This file contains the code for the server application. The server listens for incoming connections from the client, receives the file sent by the client, and then closes the connection. It responds to the client's packets to acknowledge receipt and manage the connection state.

ConfundoSocket class: This class is defined in both client.py and server.py. It provides the methods for sending and receiving packets, managing the connection state, and handling the file transfer. It also implements a simple form of congestion control to manage how much data is sent at once.

How It Works
Connection Establishment: The client initiates the connection by sending a SYN packet to the server. The server responds with a SYN-ACK packet, and the client sends an ACK packet to complete the three-way handshake.

File Transfer: Once the connection is established, the client reads the file to be sent and sends it in chunks to the server. The server acknowledges each chunk received. The client and server use sequence numbers to keep track of which data has been sent and received.

Congestion Control: The client uses a congestion window (CWND) to control the amount of data it sends before waiting for an acknowledgment. It starts with a small window and increases it gradually to avoid overwhelming the network. If a packet is lost (detected by a timeout), the window size is reduced to avoid further congestion.

Connection Termination: After the file is transferred, the client sends a FIN packet to the server to indicate that it has finished sending data. The server responds with an ACK packet and then sends its own FIN packet. The client responds with a final ACK, and the connection is closed.

Running the Project
To run the project, you'll need two terminals: one for the server and one for the client.

In the server terminal, navigate to the project folder and run:

python3 server.py 127.0.0.1 12345 received.txt
This starts the server listening on IP address 127.0.0.1 and port 12345, and it will save the received file as received.txt.

In the client terminal, navigate to the project folder and run:

python3 client.py 127.0.0.1 12345 send.txt
This starts the client, which will connect to the server at IP address 127.0.0.1 and port 12345, and send the file send.txt.

Replace 127.0.0.1, 12345, received.txt, and send.txt with the appropriate values for your setup.

Conclusion
This project is a fun way to learn about how computers communicate over the internet and how protocols like TCP and UDP work. By implementing the Confundo protocol, we get a better understanding of the challenges of reliable data transfer and congestion control.

