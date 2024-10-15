#!env python

"""Chat server for CST311 Programming Assignment 4"""
__author__ = "[Stack Otterflow]"
__credits__ = [
    "Krishna Tagdiwala",
    "Jorge Vazquez",
    "Walid Elgammal",
    "Jesus Martinez Miranda"
]

import socket as s
import threading

# Configure logging
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

server_port = 12000

users = []
names = []
offline_messages = []


def connection_handler(connection_socket, address):

    # Sends the client a welcome message for the chat service
    welcome_message = "Welcome to the chat! To send a message, type the message and click enter."
    connection_socket.send(welcome_message.encode())

    # Asking client for a username and storing it in the local variable username
    connection_socket.send("Enter username: ".encode())
    username = connection_socket.recv(1024).decode()

    # Add the new client to the names list
    names.append(username)

    # Send any offline messages to the user upon connection
    send_offline_messages(username, connection_socket)

    # Initializes message to an empty string
    message = ""

    # If the sender sent "bye", server disconnects the sender client
    while message != "bye":
        try:
            # Waits to receive a message from the client
            message = connection_socket.recv(1024).decode()
            # Logs messages exchanged by clients (used for debugging purposes)
            # log.info("Message received by " + address[0] + ". Message: " + message)

            # Checks to see if the client sends "bye"
            # Notifies the other client accordingly
            if message == "bye":
                disconnect_message = f"{username} has left the chat"
                send_message(connection_socket, disconnect_message.encode())
            else:
                # Otherwise, the server relays the message or stores it as an offline message
                message_to_send = f"{username}: {message}"
                if len(users) > 1:
                    send_message(connection_socket, message_to_send.encode())
                else:
                    store_offline_message(username, message)  # Store if the other user isn't connected
        except:
            print("Exception error when receiving data.")
            break

    # Once user terminates session, close socket and remove username
    users.remove(connection_socket)
    names.remove(username)
    connection_socket.close()


# Sends messages from one client to the other client
def send_message(connection_socket, message):
    for socket in users:
        if socket is not connection_socket:
            socket.send(message)


# Stores offline messages if the other user isn't connected
def store_offline_message(sender, message):
    offline_messages.append((sender, message))  # Storing (username, message)

# Sends all stored offline messages to the connected user
def send_offline_messages(username, connection_socket):
    global offline_messages
    # Deliver all messages from the other user to this user
    for message in offline_messages:
        sender, offline_message = message
        if sender != username:  # Deliver messages sent by other users
            connection_socket.send(f"{sender}: {offline_message}\n".encode())

def main():
    # Create a TCP socket
    server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)

    # Assign port number to socket, and bind to chosen port
    server_socket.bind(('10.0.2.4', server_port))

    # Configure how many requests can be queued on the server at once
    server_socket.listen(1)

    # Alert user we are now online
    log.info("The server is ready to receive on port " + str(server_port))

    # Surround with a try-finally to ensure we clean up the socket after we're done
    try:
        # Enter forever loop to listen for requests
        while True:
            # When a client connects, create a new socket and record their address
            connection_socket, address = server_socket.accept()
            log.info("Connected to client at " + str(address))

            # Keeps track of the connection sockets to relay messages between clients
            users.append(connection_socket)

            # Setting up multiple threads to accept connections
            thread = threading.Thread(target=connection_handler, args=(connection_socket, address))
            thread.start()

    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
