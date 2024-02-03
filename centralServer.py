import socket
import threading
import time
from typing import Any, Callable
from lib import simple_hash, logger, berkeley, compute_formatted_time


class FileServer:
    def __init__(self, port: str) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', port))
        self.socket.listen(5)
        self.log = f"centralServerLog-{port}.txt"
        self.storage_nodes = [[('127.0.0.1', 8000)], [('127.0.0.1', 8001)]]
        self.synchronized_clock_offset = None
        print(f"Server listening on port {port}")

    def start(self) -> None:
        try:
            self.synchronize_nodes()
            while True:
                conn, addr = self.socket.accept()
                print(f"Connected by {addr}")
                t = threading.Thread(
                    target=self.handle_client, args=(conn, addr))
                t.start()
        except KeyboardInterrupt:
            print("Server stopped by user")
            self.socket.close()
            exit()

    def handle_client(self, conn: Any, addr: str) -> None:
        try:
            conn.sendall('Enter userId: '.encode())
            userId = conn.recv(1024).decode()
            user_storage_node = simple_hash(userId, len(self.storage_nodes))
            conn.sendall(f'Thank you for logging in user {userId}'.encode())
            while True:
                data = conn.recv(1024).decode()
                if not data or data == 'exit':
                    print('exiting from ', addr)
                    break
                # Handle the client request
                response = self.handle_request(data, userId, user_storage_node)
                conn.sendall(response.encode())
            conn.close()
        except ConnectionResetError:
            print('Connection disrupted')

    def handle_request(self, data: str, userId: str, user_storage_node: str) -> str | Callable:
        # Parse the client request and return the response
        splitted_request = data.split()
        command = splitted_request[0]

        # log request to the server
        log_message = f"\n{userId} : {compute_formatted_time(self.synchronized_clock_offset)} : {command}"
        logger(self.log, log_message)

        match command:
            case 'ls':
                if len(splitted_request) != 1:
                    return 'command Usage(lists the entire storage area for user): ls'
                return self.request_storage_node(f'{userId}:ls', user_storage_node, need_single_server=True)
            case 'create':
                if len(splitted_request) != 3 or splitted_request[1] != 'dir' and splitted_request[1] != 'file':
                    return 'command Usage: create type<dir,file> path'
                type, path = splitted_request[1], splitted_request[2]
                return self.request_storage_node(f'{userId}:create:{type}:{path}', user_storage_node)
            case 'write':
                if len(splitted_request) < 3:
                    return 'command Usage: write path\\to\\file data'
                filePath = splitted_request[1]
                fileData = ' '.join(splitted_request[2:])
                return self.request_storage_node(f'{userId}:write:{filePath}:{fileData}', user_storage_node)
            case 'read':
                if len(splitted_request) != 2:
                    return 'command Usage: read path\\to\\file'
                filePath = splitted_request[1]
                return self.request_storage_node(f'{userId}:read:{filePath}', user_storage_node, need_single_server=True)
            case 'delete':
                if len(splitted_request) != 2:
                    return 'command Usage: delete path\\to\\file_or_dir'
                path = splitted_request[1]
                return self.request_storage_node(f'{userId}:delete:{path}', user_storage_node)
            case 'rename':
                if len(splitted_request) != 3:
                    return 'command Usage: rename path\\to\\file_or_dir new_name'
                path = splitted_request[1]
                newName = splitted_request[2]
                return self.request_storage_node(f'{userId}:rename:{path}:{newName}')
            case other:
                return 'invalid request'

    def request_storage_node(self, message: str, user_storage_node: int, need_single_server: bool = False) -> Any:
        replicated_storage_nodes = self.storage_nodes[user_storage_node]
        for storage_node in replicated_storage_nodes:
            storage_node_IP, storage_node_port = storage_node
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((storage_node_IP, storage_node_port))
                    s.sendall(message.encode())
                    response = s.recv(2048).decode()
                    print('response', response)
                    if need_single_server and response:
                        break
            except:
                response = None
        return response

    def synchronize_nodes(self) -> None:
        node_clocks = []
        for replicated_storage_nodes in self.storage_nodes:
            for storage_node in replicated_storage_nodes:
                storage_node_IP, storage_node_port = storage_node
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((storage_node_IP, storage_node_port))
                    s.sendall("synchronize".encode())
                    node_clock = s.recv(2048).decode()
                    node_clocks.append(float(node_clock))
                    s.close()
        master_node_clock = time.time()
        node_clocks.append(master_node_clock)
        synchronized_time = berkeley(node_clocks)

        for replicated_storage_nodes in self.storage_nodes:
            for index, storage_node in enumerate(replicated_storage_nodes):
                storage_node_IP, storage_node_port = storage_node
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((storage_node_IP, storage_node_port))
                    synchronized_time_offset = synchronized_time - \
                        node_clocks[index]
                    s.sendall(str(synchronized_time_offset).encode())
                    s.close()
        self.synchronized_clock_offset = synchronized_time - master_node_clock


if __name__ == '__main__':
    server = FileServer(8080)
    server.start()
