import socket
import sqlite3
import os
from hashlib import sha256

# Define the server address and port
SERVER_ADDRESS = '127.0.0.1' 
SERVER_PORT = 56789

# Function to authenticate user credentials
def authenticate_user(username, password):
    conn = sqlite3.connect('C:/v1/database/users.db')
    cursor = conn.cursor()

    # Hash the password to match the hashed password in the database
    hashed_password = sha256(password.encode()).hexdigest()

    # Check if the username and hashed password match any records in the database
    cursor.execute('''
        SELECT * FROM users WHERE username=? AND password=?
    ''', (username, hashed_password))

    user = cursor.fetchone()
    conn.close()

    return user is not None

# Function to retrieve a list of available audio files
def get_audio_files():
    media_folder_path = 'C:/v1/media'
    audio_files = os.listdir(media_folder_path)
    return audio_files

# Function to handle file download
def handle_file_download(client_socket, requested_file):
    # Check if the requested file exists in the 'media' folder
    media_folder_path = 'C:/v1/media/'
    file_path = os.path.join(media_folder_path, requested_file)

    if os.path.isfile(file_path):
        # Open and send the requested file to the client
        with open(file_path, 'rb') as file:
            file_data = file.read()

            # Send file size first
            client_socket.send(str(len(file_data)).encode())

            # Wait for acknowledgment from the client before sending the file
            confirmation = client_socket.recv(1024).decode()

            if confirmation == 'ready':
                # Increase buffer size for sending file
                client_socket.sendall(file_data)
    else:
        client_socket.send("File not found".encode())

# Function to handle file streaming
def handle_file_stream(client_socket, requested_file):
    media_folder_path = 'C:/v1/media/'
    file_path = os.path.join(media_folder_path, requested_file)

    if os.path.isfile(file_path):
        print(f"Streaming {requested_file} to {client_socket.getpeername()}")  # Feedback before streaming
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(1024)  # Read a chunk of 1024 bytes
                if not chunk:
                    break
                client_socket.send(chunk)
        print(f"Streaming complete for {requested_file}")  # Feedback after streaming
    else:
        print(f"Requested file {requested_file} not found")  # Feedback for file not found
        client_socket.send("File not found".encode())

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(5)

print(f"Server listening on {SERVER_ADDRESS}:{SERVER_PORT}")

while True:
    # Accept incoming connections
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")

    # Receive username and password from the client
    username = client_socket.recv(1024).decode()
    password = client_socket.recv(1024).decode()

    # Authenticate user
    authenticated = authenticate_user(username, password)

    if authenticated:
        print(f"User '{username}' authenticated.")
        # Send authentication success message to the client
        client_socket.send("Authentication successful".encode())

        # Receive a request from the client
        request = client_socket.recv(1024).decode()

        if request == 'list_files':
            # Send the list of available audio files to the client
            files_list = get_audio_files()
            files_str = "\n".join(files_list)
            client_socket.send(files_str.encode())

        elif request == 'download_file':
            # Get the requested file name from the client
            requested_file = client_socket.recv(1024).decode()
            handle_file_download(client_socket, requested_file)

        elif request == 'stream_file':
            # Get the requested file name from the client
            requested_file = client_socket.recv(1024).decode()
            handle_file_stream(client_socket, requested_file)

        else:
            print("Invalid request")
        
        # Receive completion signal from the client
        completion_signal = client_socket.recv(1024).decode()
        
        if completion_signal == 'done':
            # Close the client socket after receiving completion signal
            client_socket.close()
            print(f"Connection from {client_address} closed.")

    else:
        # Send authentication failure message to the client
        print("Authentication failed.")
        client_socket.send("Authentication failed".encode())

        # After handling the request, wait for client's completion signal
        completion_signal = client_socket.recv(1024).decode()
        
        if completion_signal == 'done':
            # Close the client socket after receiving completion signal
            client_socket.close()
            print(f"Connection from {client_address} closed.")

# Close the server socket
server_socket.close()