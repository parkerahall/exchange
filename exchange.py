import sys
import socket
import threading

from book import *
from symbol import *
from message import *

MSG_SIZE = 512
BYTE_CODE = "utf-8"

def encode(string):
    return (string + "\n\n").encode(BYTE_CODE)


WELCOME_MESSAGE = encode("WELCOME TO THE EXCHANGE!\nType 'help' for more info")

HELP_MESSAGE = encode("Valid commands:\n" +
               "ADD-TICKER|SIDE|AMOUNT|PRICE to add an order\n" +
               "REMOVE-ID to remove an order\n" +
               "BOOK-TICKER to see open orders on the book (use 'ALL' for all tickers)")

class ServeThread(threading.Thread):
    def __init__(self, exchange, sock, cid):
        super(ServeThread, self).__init__()
        self.exchange = exchange
        self.socket = sock
        self.client_id = cid

    def run(self):
        msg_id = 0
        with self.socket:
            self.socket.send(WELCOME_MESSAGE)
            while True:
                raw_msg = self.socket.recv(MSG_SIZE).decode(BYTE_CODE).strip()
                if not raw_msg:
                    break
                try:
                    msg = Message.deserialize(raw_msg.upper())
                    self.exchange.handle_message(msg, self.client_id, msg_id)
                    msg_id += 1
                except Exception as e:
                    if self.exchange.debug:
                        raise e
                    else:
                        self.socket.send(encode("ERROR OCCURRED: " + str(e)))

        del self.exchange.clients[self.client_id]

class Exchange_Server:
    def __init__(self, host, port, debug):
        self.host = host
        self.port = port

        self.books = {symbol : Book(symbol) for symbol in ALL_SYMBOLS}
        self.book_locks = {symbol : threading.Lock() for symbol in ALL_SYMBOLS}

        self.clients = {}
        self.order_ids = {}

        self.debug = debug

    def handle_message(self, msg, client_id, msg_id):
        if msg.type == HELP:
            self.clients[client_id].send(HELP_MESSAGE)

        elif msg.type == MY_ORDERS:
            self.send_open_orders(client_id)

        elif msg.type == ADD:
            order = msg.data
            symbol = order.symbol
            unique_id = (client_id, msg_id)
            self.order_ids[unique_id] = symbol
            self.book_locks[symbol].acquire()
            filled_orders = self.books[symbol].add(order.copy(), unique_id)
            self.book_locks[symbol].release()
            self.clients[client_id].send(encode(str(order) + "\nHAS BEEN PLACED WITH ORDER ID " + str(msg_id)))
            self.handle_filled_orders(filled_orders)

        elif msg.type == REMOVE:
            order_id = msg.data
            unique_id = (client_id, order_id)
            try:
                symbol = self.order_ids[unique_id]
                self.book_locks[symbol].acquire()
                self.books[symbol].remove(unique_id)
                self.book_locks[symbol].release()
                self.clients[client_id].send(encode("ORDER " + str(order_id) + " HAS BEEN REMOVED"))

                del self.order_ids[unique_id]
            except ValueError as e:
                self.clients[client_id].send(encode("CANNOT REMOVE ORDER: " + str(e)))

        elif msg.type == BOOK:
            symbol = msg.data
            to_print = [symbol] if symbol != ALL else self.books.keys()
            for key in to_print:
                self.book_locks[key].acquire()
                self.clients[client_id].send(encode(str(self.books[key])))
                self.book_locks[key].release()

        else:
            self.clients[client_id].send(encode("MESSAGE TYPE NOT SUPPORTED: " + str(msg)))

    def handle_filled_orders(self, filled_orders):
        for unique_id, placed_order, filled_order in filled_orders:
            client_id, msg_id = unique_id
            if client_id in self.clients:
                partially = "" if placed_order.amount == filled_order.amount else "PARTIALLY "
                send_string = encode("ORDER " + str(msg_id) + ":\n" + str(placed_order) + "\nHAS BEEN " + partially + "FILLED:\n" + str(filled_order))
                self.clients[client_id].send(send_string)
            else:
                print("Client ID " + str(client_id) + " not found")

    def send_open_orders(self, client_id):
        sent = False
        for symbol in self.books:
            self.book_locks[symbol].acquire()
            for order_id in self.books[symbol].open_orders:
                cid, msg_id = order_id
                if client_id == cid:
                    order = self.books[symbol].open_orders[order_id].value
                    order_string = "ORDER " + str(msg_id) + ": " + str(order)
                    self.clients[client_id].send(encode(order_string))
                    sent = True
            self.book_locks[symbol].release()

        if not sent:
            self.clients[client_id].send(encode("NO OPEN ORDERS FOUND"))

    def serve(self):
        server = socket.socket()
        server.bind((self.host, self.port))
        server.listen()

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
        except KeyboardInterrupt:
            server.close()
            print("\nEXCHANGE CLOSED\n")

if __name__ == "__main__":
    debug = False
    port = int(sys.argv[1])
    if len(sys.argv) > 2:
        debug = bool(sys.argv[2])
    server = Exchange_Server('localhost', port, debug)
    server.serve()