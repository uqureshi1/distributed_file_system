import socket

host = '127.0.0.1'  # as both code is running on same pc
port = 8080  # socket server port number


def client_program():

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    # username exchange
    data = client_socket.recv(2048).decode()
    print(data)

    message = input(" -> ")  # take input

    cond = True
    while cond:
        client_socket.send(message.encode())  # send message
        response = client_socket.recv(2048).decode()  # receive response

        print(response)  # show in terminal

        message = input(' -> ')  # again take input

        if message.lower().strip() == 'exit':
            cond = False
            client_socket.send('exit'.encode())

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()
