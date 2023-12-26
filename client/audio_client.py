import socket
import pyaudio

# Define the server address and port
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 56789

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect((SERVER_ADDRESS, SERVER_PORT))

    print(f"Connected to {SERVER_ADDRESS}:{SERVER_PORT}")

    # Get username and password from the user
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Send username and password to the server
    client_socket.send(username.encode())
    client_socket.send(password.encode())

    # Receive authentication result from the server
    auth_result = client_socket.recv(1024).decode()

    print(auth_result)

    if auth_result == "Authentication successful":
        # Send request to the server to get the list of available audio files
        client_socket.send('list_files'.encode())

        # Receive the list of available audio files from the server
        files_list = client_socket.recv(1024).decode()
        print("Available audio files:")

        # Split the received file list into separate filenames
        available_files = files_list.split('\n')

        # Display the files with corresponding numbers
        for idx, file_name in enumerate(available_files, start=1):
            print(f"{idx}. {file_name}")

        # Request a specific audio file from the server
        choice = input("Enter the number of the file to stream: ")

        try:
            file_number = int(choice)
            if 1 <= file_number <= len(available_files):
                selected_file = available_files[file_number - 1]
                print(f"You've chosen: {selected_file}")

                # Send the selected file name to the server for streaming
                client_socket.send('stream_file'.encode())
                client_socket.send(selected_file.encode())

                # Wait for the server's response before proceeding
                response = client_socket.recv(1024).decode()
                if response == 'ready':
                    print("Server ready to stream. Starting audio playback...")

                    # Initialize PyAudio
                    audio = pyaudio.PyAudio()

                    # Define audio parameters - Update these based on your audio
                    CHUNK = 1024
                    FORMAT = pyaudio.paInt16
                    CHANNELS = 2
                    RATE = 44100

                    # Open a stream for audio playback
                    stream = audio.open(format=FORMAT,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        output=True)

                    # Begin receiving the audio file from the server
                    while True:
                        audio_chunk = client_socket.recv(CHUNK)
                        if not audio_chunk:
                            break
                        stream.write(audio_chunk)

                    print("\nFile transfer complete.")
                    stream.stop_stream()
                    stream.close()
                    audio.terminate()
                else:
                    print("Server not ready.")

            else:
                print("Invalid choice. Please enter a number within the given range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

except ConnectionAbortedError as e:
    print(f"ConnectionAbortedError: {e}. Connection might have been unexpectedly terminated.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the client socket
    client_socket.close()