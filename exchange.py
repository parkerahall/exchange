import socket

class Exchange_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.books = {}