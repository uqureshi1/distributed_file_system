import os
import shutil
from socket import *
import threading
import sys
import time
from lib import logger, compute_formatted_time


class StorageServer:
    def __init__(self, root_dir, host='localhost', port=8000):
        self.root_dir = root_dir
        self.host = host
        self.port = port
        self.synchronizedClockOffset = None
        self.log = f"storageServerLog-{port}.txt"
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def create_root_dir(self):
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)

    def synchronize_clock(self):
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
            self.synchronizedClockOffset = float(clockOffset)
            socket.close()

    def start(self):
        self.create_root_dir()
        self.server_socket.listen(5)
        print(f'Storage server started on {self.host}:{self.port}')

        self.synchronize_clock()

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(
                f'Accepted connection from {client_address[0]}:{client_address[1]}')
            t = threading.Thread(target=self.handle_client,
                                 args=(client_socket,))
            t.start()

    def handle_client(self, client_socket):
        request = client_socket.recv(1024).decode()
        splittedRequest = request.split(':')
        userId, command = splittedRequest[0], splittedRequest[1]
        userBasePath = self.get_user_base_path(userId)

        # log request to the server
        logMessage = f"\n{userId} : {compute_formatted_time(self.synchronizedClockOffset)} : {command} : {userBasePath}"
        logger(self.log, logMessage)
        print(splittedRequest)
        match command:
            case 'ls':
                response = self.list_directory_structure(userBasePath)
            case 'create':
                type, path = splittedRequest[2], splittedRequest[3]
                response = self.create_file(
                    type, os.path.join(userBasePath, path))
            case 'write':
                path, data = splittedRequest[2], splittedRequest[3]
                response = self.write_file(
                    os.path.join(userBasePath, path), data)
            case 'read':
                path = splittedRequest[2]
                response = self.read_file(os.path.join(userBasePath, path))
            case 'delete':
                path = splittedRequest[2]
                response = self.delete_file(os.path.join(userBasePath, path))
            case 'rename':
                old_path, new_path = splittedRequest[2], splittedRequest[3]
                self.rename_file(os.path.join(userBasePath, old_path),
                                 os.path.join(userBasePath, new_path))
            case other:
                response = 'invalid Request'
        client_socket.send(response.encode())
        client_socket.close()

    def create_file(self, type, path):
        # Create directory
        if type == 'dir':
            try:
                os.makedirs(path)
                return f"Folder {path} created!"
            except FileExistsError:
                return f"Folder {path} already exists"

        # Create file
        elif type == 'file':
            try:
                # Trying to create a new file or open one
                file = open(path, "a")
                file.close()
                return f"File {path} created successfully"
            except:
                return "Error creating file"
        else:
            return 'invalid type'

    def write_file(self, path, data):
        try:
            file = open(path, "a")
            file.write(data)
            file.close()
            return f"Data written to file {path}"
        except FileNotFoundError:
            return "File or directory not found"
        except:
            return "Error writing to file"

    def read_file(self, path):
        try:
            file = open(path, "r")   # Trying to create a new file or open one
            content = file.read()
            file.close()
            return content if content != '' else 'no data in file'
        except FileNotFoundError:
            return "File or directory not found"
        except:
            return "Error reading file"

    def delete_file(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                return 'No such file or directory found'
            return f'{path} deleted'
        except FileNotFoundError:
            return "File or directory not found"

    def rename_file(self, old_name, new_name):
        try:
            os.rename(old_name, new_name)
            return f'{old_name} changed to {new_name}'
        except FileNotFoundError:
            return "File or directory not found"
        except:
            return "Error in renaming file"

    def get_user_base_path(self, userId):
        userBasePath = f'{self.root_dir}\\{userId}_DIR'
        if not os.path.exists(userBasePath):
            os.mkdir(userBasePath)
        return userBasePath

    def list_directory_structure(self, path):
        outputString = ''
        for root, dirs, files in os.walk(path):
            for name in files:
                outputString += os.path.join(root, name) + '\n'
            for name in dirs:
                outputString += os.path.join(root, name) + '\n'
        return outputString if outputString != '' else 'no files or directories'


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Enter rootDirForServer and portNo.')
        exit()
    rootDir, portNo = sys.argv[1], int(sys.argv[2])
    storageServer = StorageServer(rootDir, port=portNo)
    storageServer.start()
