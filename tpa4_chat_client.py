#!env python

"""Chat client for CST311 Programming Assignment 4"""
__author__ = "[Stack Otterflow]"
__credits__ = [
    "Krishna Tagdiwala",
    "Jorge Vazquez",
    "Walid Elgammal",
    "Jesus Martinez Miranda"
]

# Import statements
import socket as s
import ssl

# Configure logging
import logging
import threading

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Set global variables
server_name = '10.0.2.4'
server_port = 12000

def main():
    # Create socket
    client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    # Added these lines 
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations("/etc/ssl/demoCA/tpa4.chat.test.pem")

    try:
        # Establish TCP connection
        # client_socket.connect((server_name, server_port))
        # Added these lines
        secure_socket = context.wrap_socket(client_socket, server_hostname=server_name)
        secure_socket.connect((server_name, server_port))
    except Exception as e:
        log.exception(e)
        log.error("***Advice:***")
        if isinstance(e, s.gaierror):
            log.error("\tCheck that server_name and server_port are set correctly.")
        elif isinstance(e, ConnectionRefusedError):
            log.error("\tCheck that server is running and the address is correct")
        else:
            log.error("\tNo specific advice, please contact teaching staff and include text of error and code.")
        exit(8)

    # Creates and starts threads for sending and receiving messages
    # So that both functions occur simeltaneously (in real-time)
    sending_thread = threading.Thread(target=send_message, args=(secure_socket,))
    receiving_thread = threading.Thread(target=receive_message, args=(secure_socket,))
    sending_thread.start()
    receiving_thread.start()

# Allows the client to send messages to the other client through the server
def send_message(secure_socket):
    message = ""

    # Checks to see if the message is "bye" to determine when the client wants to disconnect
    while message != "bye":
        message = input('')
        secure_socket.send(message.encode())

    secure_socket.close()

# Allows the client to receive messages from the other client through the server
def receive_message(secure_socket):

    response = ""

    # Constantly checks to see if the server has relayed any messages
    while True:
        try:
            response = secure_socket.recv(1024)
            response_decoded = response.decode()
            print(response_decoded)
        except:
            print("Leaving chat...")
            break


# This helps shield code from running when we import the module
if __name__ == "__main__":
    main()
