import socket

host = '127.0.0.1'  # For test run, we run central server and client on same pc
port = 8080  # central server port number


def client_program() -> None:
    """This manages user input and client-server communication"""

    client_socket = socket.socket()
    client_socket.connect((host, port))  # connect to the server

    # username exchange
    data = client_socket.recv(2048).decode()
    print(data)

    message = input(" -> ")  # take command from user

    cond = True
    while cond:
        client_socket.send(message.encode())  # send message
        response = client_socket.recv(2048).decode()  # receive response

        print(response)

        message = input(' -> ')

        if message.lower().strip() == 'exit':
            cond = False
            client_socket.send('exit'.encode())

    client_socket.close()


if __name__ == '__main__':
    client_program()
