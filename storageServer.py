import os
import shutil
from socket import *
import threading
import sys
import time
from typing import Any
from lib import logger, compute_formatted_time

USERS = 5


class StorageServer:
    def __init__(self, root_dir: str, host: str = 'localhost', port: int = 8000) -> None:
        self.root_dir = root_dir
        self.host = host
        self.port = port
        self.synchronized_clock_offset = None
        self.log = f"StorageServerLog-{port}.txt"
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def create_root_dir(self) -> None:
        """Creates personal directory for the user"""

        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)

    def synchronize_clock(self) -> None:
        """Synchronizes clock of storage server woth central server"""

        socket, _ = self.server_socket.accept()
        request = socket.recv(1024).decode()
        if request == "synchronize":
            current_time = time.time()
            socket.send(str(current_time).encode())
            socket.close()

            # we accept a new connection here as previous
            # socket gets closed on the server
            socket, _ = self.server_socket.accept()
            clockOffset = socket.recv(1024).decode()
            self.synchronized_clock_offset = float(clockOffset)
            socket.close()

    def start(self) -> None:
        """Starts the storage server and listens to user connection"""

        self.create_root_dir()
        self.server_socket.listen(USERS)
        print(f'Storage server started on {self.host}:{self.port}')

        self.synchronize_clock()

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(
                f'Accepted connection from {client_address[0]}:{client_address[1]}')
            t = threading.Thread(target=self.handle_client,
                                 args=(client_socket,))
            t.start()

    def handle_client(self, client_socket: Any) -> None:
        """Handles client commands and logs to respective storage server log"""

        request = client_socket.recv(1024).decode()
        splitted_request = request.split(':')
        userId, command = splitted_request[0], splitted_request[1]
        user_base_path = self.get_user_base_path(userId)

        # log request to the server
        log_message = f"\n{userId} : {compute_formatted_time(self.synchronized_clock_offset)} : {command} : {user_base_path}"
        logger(self.log, log_message)
        print(splitted_request)

        response = ""
        match command:
            case 'ls':
                response = self.list_directory_structure(user_base_path)
            case 'create':
                type, path = splitted_request[2], splitted_request[3]
                response = self.create_file(
                    type, os.path.join(user_base_path, path))
            case 'write':
                path, data = splitted_request[2], splitted_request[3]
                response = self.write_file(
                    os.path.join(user_base_path, path), data)
            case 'read':
                path = splitted_request[2]
                response = self.read_file(os.path.join(user_base_path, path))
            case 'delete':
                path = splitted_request[2]
                response = self.delete_file(os.path.join(user_base_path, path))
            case 'rename':
                old_path, new_path = splitted_request[2], splitted_request[3]
                response = self.rename_file(os.path.join(user_base_path, old_path),
                                            os.path.join(user_base_path, new_path))
            case other:
                response = 'Invalid Request!'
        client_socket.send(response.encode())
        client_socket.close()

    def create_file(self, type: str, path: str) -> str:
        """Creates file or directory for the user"""

        # Create directory
        if type == 'dir':
            try:
                os.makedirs(path)
                return f"Folder {path} created!"
            except FileExistsError:
                return f"Folder {path} already exists!"

        # Create file
        elif type == 'file':
            try:
                # Trying to create a new file or open one
                file = open(path, "a")
                file.close()
                return f"File {path} created successfully!"
            except:
                return "Error creating file!"
        else:
            return 'Invalid Type!'

    def write_file(self, path: str, data: Any) -> str:
        """Writes to a file given filepath and data"""

        try:
            file = open(path, "a")
            file.write(data)
            file.close()
            return f"Data written to file {path}"
        except FileNotFoundError:
            return "File or directory not found!"
        except:
            return "Error writing to file!"

    def read_file(self, path: str) -> str:
        """Reads file given file path"""

        try:
            file = open(path, "r")   # Trying to create a new file or open one
            content = file.read()
            file.close()
            return content if content != '' else 'No data in file!'
        except FileNotFoundError:
            return "File or directory not found!"
        except:
            return "Error reading file!"

    def delete_file(self, path: str) -> str:
        """Deletes file or directory given path"""

        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                return 'No such file or directory found!'
            return f'{path} deleted!'
        except FileNotFoundError:
            return "File or directory not found!"

    def rename_file(self, old_name: str, new_name: str) -> str:
        """Rename file or directory given old path and new path till file and extention"""

        try:
            os.rename(old_name, new_name)
            return f'{old_name} changed to {new_name}!'
        except FileNotFoundError:
            return "File or directory not found!"
        except:
            return "Error in renaming file!"

    def get_user_base_path(self, userId: str) -> str:
        """Finds user base path using the user ID"""

        user_base_path = f'{self.root_dir}\\{userId}_DIR'
        if not os.path.exists(user_base_path):
            os.mkdir(user_base_path)
        return user_base_path

    def list_directory_structure(self, path: str) -> str:
        """Formats output for ls command given path"""

        output_string = ''
        for root, dirs, files in os.walk(path):
            for name in files:
                output_string += os.path.join(root, name) + '\n'
            for name in dirs:
                output_string += os.path.join(root, name) + '\n'
        return output_string if output_string != '' else 'No files or directories!'


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Enter root directory for server and port no.: ')
        exit()
    root_dir, portNo = sys.argv[1], int(sys.argv[2])
    storage_server = StorageServer(root_dir, port=portNo)
    storage_server.start()
