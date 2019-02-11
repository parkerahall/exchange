import sys
import socket
import threading

from message import *

MSG_SIZE = 512

class ServeThread(threading.Thread):
    def __init__(self, exchange, sock, cid):
        self.exchange = exchange
        self.socket = sock
        self.client_id = cid

    def run(self):
        msg_id = 0
        with self.socket:
            while True:
                raw_msg = self.socket.recv(MSG_SIZE)
                if not raw_msg:
                    break
                msg = Message.deserialize(raw_msg)
                self.exchange.handle_message(msg, self.client_id, msg_id)
                msg_id += 1

class Exchange_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.books = {}
        self.book_locks = {}

        self.clients = {}

    def handle_message(self, msg, client_id, msg_id):
        unique_id = (client_id, msg_id)

        if msg.type == ADD:
            order = msg.data
            symbol = order.symbol
            self.book_locks[symbol].aquire()
            filled_orders = self.books[symbol].add(order, unique_id)
            self.book_locks[symbol].release()
            self.clients[client_id].send("YOUR ORDER:\n" + str(order) + "\nHAS BEEN PLACED")
            self.handle_filled_orders(filled_orders)

        elif msg_type == REMOVE:
            order_id = msg.data
            try:
                self.book_locks[symbol].aquire()
                self.books[symbol].remove(order_id)
                self.book_locks[symbol].release()
                self.clients[client_id].send("YOUR ORDER WITH ID " + str(order_id) + "HAS BEEN REMOVED")
            except ValueError as e:
                self.clients[client_id].send("CANNOT REMOVE ORDER: " + str(e))

        else:
            symbol = msg.data
            to_print = [symbol] if symbol != ALL else self.books.keys()
            for key in to_print:
                self.book_locks[key].aquire()
                self.clients[client_id].send(str(self.books[key]))
                self.book_locks[key].release()

    def handle_filled_orders(self, filled_orders):
        for unique_id, placed_order, filled_order in filled_orders:
            client_id, _ = unique_id
            partially = "" if placed_order.amount == filled_order.amount else "PARTIALLY "
            send_string = "YOUR PLACED ORDER:\n" + str(order) + "\nHAS BEEN " + partially + "FILLED:\n" + str(filled_order)
            self.clients[client_id].send(send_string)

    def serve(self):
        server = socket.socket()
        server.bind(self.host, self.port)
        sever.listen()

        client_id = 0

        try:
            while True:
                conn, addr = server.accept()
                ip, port = addr
                print("CONNECTION MADE AT " + ip + ": " + str(port))

                self.clients[client_id] = conn
                new_thread = ServeThread(self, conn, client_id)
                new_thread.start()

                client_id += 1
        finally:
            sever.close()
            print("\nEXCHANGE CLOSED\n")