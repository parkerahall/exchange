import sys
import socket
import threading

class Exchange_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.books = {}
        self.book_locks = {}