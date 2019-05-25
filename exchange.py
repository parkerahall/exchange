import sys
import socket
import threading
import datetime

from book import *
from symbol import *
from message import *

MSG_SIZE = 512
BYTE_CODE = "utf-8"

def encode(string):
    return (f"{string}\n\n").encode(BYTE_CODE)

def encode_for_logging(string, unique_id=None):
    date = datetime.datetime.now()
    log_string = f"{str(date)}: "
    if unique_id != None:
        client_id, msg_id = unique_id
        log_string += f"CLIENT {str(client_id)}, MESSAGE {str(msg_id)}: "
    log_string += f"{string}\n"
    return log_string


WELCOME_MESSAGE = encode("WELCOME TO THE EXCHANGE!\nType 'help' for more info")

HELP_MESSAGE = encode("Valid commands:\n" +
               "ADD-TICKER|SIDE|AMOUNT|PRICE to add an order\n" +
               "REMOVE-ID to remove an order\n" +
               "BOOK-TICKER to see open orders on the book (use 'ALL' for all tickers)\n" +
               "MY ORDERS to view your open orders\n\n" +
               "press 'enter' to exit the exchange")

OPEN_MESSAGE = "EXCHANGE OPENED"

EXIT_MESSAGE = "EXCHANGE CLOSED"

class ServeThread(threading.Thread):
    def __init__(self, exchange, sock, cid):
        super(ServeThread, self).__init__(daemon=True)
        self.exchange = exchange
        self.socket = sock
        self.client_id = cid

    def run(self):
        msg_id = 0
        with self.socket:
            self.socket.send(WELCOME_MESSAGE)
            while True:
                raw_msg_stream = self.socket.recv(MSG_SIZE).decode(BYTE_CODE)
                if raw_msg_stream == "\n":
                    break
                try:
                    extra = [raw_msg_stream[-1]]
                    while extra[-1] != "\n":
                        extra.append(self.socket.recv(1).decode(BYTE_CODE))

                    raw_msgs = raw_msg_stream.strip().split("\n")
                    for i in range(len(raw_msgs)):
                        raw_msg = raw_msgs[i]
                        if i == len(raw_msgs) - 1:
                            raw_msg += "".join(extra[1:-1])
                        msg = Message.deserialize(raw_msg.upper())
                        self.exchange.handle_message(msg, self.client_id, msg_id)
                        msg_id += 1
                except Exception as e:
                    error_msg = f"INVALID INPUT: {raw_msg}"
                    self.exchange.write_to_log(encode_for_logging(error_msg, (self.client_id, msg_id)))
                    if self.exchange.debug:
                        raise e
                    else:
                        self.socket.send(encode(error_msg))

        disconnect_msg = f"CLIENT {str(self.client_id)} HAS DISCONNECTED"
        print(disconnect_msg)
        self.exchange.write_to_log(encode_for_logging(disconnect_msg))
        del self.exchange.clients[self.client_id]

class StreamThread(threading.Thread):
    def __init__(self, exchange):
        super(StreamThread, self).__init__(daemon=True)
        self.exchange = exchange
        self.server = socket.socket()

    def run(self):
        self.server.bind((self.exchange.host, self.exchange.stream_port))
        self.server.listen()

        try:
            while True:
                conn, addr = self.server.accept()
                ip, port = addr

                conn.send(encode(OPEN_MESSAGE))
                self.exchange.stream_clients_lock.acquire()
                self.exchange.stream_clients.append(conn)
                self.exchange.stream_clients_lock.release()
        except KeyboardInterrupt:
            self.server.close()

class Exchange_Server:
    def __init__(self, host, order_port, stream_port, log_file, debug):
        self.host = host
        self.order_port = order_port
        self.stream_port = stream_port
        self.stream_clients = []
        self.stream_clients_lock = threading.Lock()

        self.books = {symbol : Book(symbol) for symbol in ALL_SYMBOLS}
        self.book_locks = {symbol : threading.Lock() for symbol in ALL_SYMBOLS}

        self.clients = {}
        self.order_ids = {}

        self.log_file = log_file
        self.debug = debug

    def handle_message(self, msg, client_id, msg_id):
        log_msg = f"MESSAGE RECEIVED: {str(msg)}"
        self.write_to_log(encode_for_logging(log_msg, (client_id, msg_id)))

        if msg.type == HELP:
            self.clients[client_id].send(HELP_MESSAGE)

        elif msg.type == MY_ORDERS:
            self.send_open_orders(client_id)

        elif msg.type == ADD:
            order = msg.data
            symbol = order.symbol
            
            unique_id = (client_id, msg_id)
            self.order_ids[unique_id] = symbol

            stream_message = f"ORDER PLACED: {str(order)}"
            self.stream_clients_lock.acquire()
            for client in self.stream_clients:
                client.send(encode(stream_message))
            self.stream_clients_lock.release()
            
            self.book_locks[symbol].acquire()
            filled_orders = self.books[symbol].add(order.copy(), unique_id)
            self.book_locks[symbol].release()

            self.stream_clients_lock.acquire()
            for _, _, order in filled_orders:
                stream_message = f"ORDER FILLED: {str(order)}"
                for client in self.stream_clients:
                    client.send(encode(stream_message))
            self.stream_clients_lock.release()
            
            confirm_msg = f"{str(order)}\nHAS BEEN PLACED WITH ORDER ID {str(msg_id)}"
            self.clients[client_id].send(encode(confirm_msg))
            
            log_msg = f"MESSAGE SENT: {confirm_msg}"
            self.write_to_log(encode_for_logging(log_msg, (client_id, msg_id)))
            
            self.handle_filled_orders(filled_orders)

        elif msg.type == REMOVE:
            order_id = msg.data
            unique_id = (client_id, order_id)
            try:
                symbol = self.order_ids[unique_id]

                order = self.books[symbol].get_open_order(unique_id)
                
                self.book_locks[symbol].acquire()
                self.books[symbol].remove(unique_id)
                self.book_locks[symbol].release()

                stream_message = f"ORDER REMOVED: {str(order)}"
                self.stream_clients_lock.acquire()
                for client in self.stream_clients:
                    client.send(encode(stream_message))
                self.stream_clients_lock.release()
                
                confirm_msg = f"ORDER {str(order_id)} HAS BEEN REMOVED"
                self.clients[client_id].send(encode(confirm_msg))
                
                log_msg = f"MESSAGE SENT: {confirm_msg}"
                self.write_to_log(encode_for_logging(log_msg, (client_id, msg_id)))

                del self.order_ids[unique_id]
            except ValueError as e:
                error_msg = f"CANNOT REMOVE ORDER: {str(e)}"
                self.write_to_log(encode_for_logging(error_msg, (client_id, msg_id)))
                if self.debug:
                    raise e
                else:
                    self.clients[client_id].send(encode(error_msg))

        elif msg.type == BOOK:
            symbol = msg.data
            to_print = [symbol] if symbol != ALL else self.books.keys()
            for key in to_print:
                self.book_locks[key].acquire()
                self.clients[client_id].send(encode(str(self.books[key])))
                self.book_locks[key].release()

        else:
            error_msg = f"MESSAGE TYPE NOT SUPPORTED: {str(msg)}"
            self.clients[client_id].send(encode(error_msg))

            log_msg = f"MESSAGE SENT: {error_msg}"
            self.write_to_log(encode_for_logging(log_msg, (client_id, msg_id)))


    def handle_filled_orders(self, filled_orders):
        for unique_id, placed_order, filled_order in filled_orders:
            client_id, msg_id = unique_id
            partially = "" if placed_order.amount == filled_order.amount else " PARTIALLY"
            
            log_msg = f"ORDER: {str(placed_order)}{partially} FILLED: {str(filled_order)}"
            self.write_to_log(encode_for_logging(log_msg, unique_id))
            
            if client_id in self.clients:
                send_string = encode(f"ORDER {str(msg_id)}:\n{str(placed_order)}\nHAS BEEN{partially} FILLED:\n{str(filled_order)}")
                self.clients[client_id].send(send_string)
            else:
                missing_msg = f"CLIENT ID {str(client_id)} NOT FOUND"
                self.write_to_log(encode_for_logging(missing_msg))

    def send_open_orders(self, client_id):
        sent = False
        for symbol in self.books:
            self.book_locks[symbol].acquire()
            for order_id in self.books[symbol].open_orders:
                cid, msg_id = order_id
                if client_id == cid:
                    order = self.books[symbol].open_orders[order_id].value
                    order_string = f"ORDER {str(msg_id)}: {str(order)}"
                    self.clients[client_id].send(encode(order_string))
                    sent = True
            self.book_locks[symbol].release()

        if not sent:
            self.clients[client_id].send(encode("NO OPEN ORDERS FOUND"))
    
    def close_order_clients(self):
        for client_id in self.clients:
            self.clients[client_id].send(encode(EXIT_MESSAGE))
            self.clients[client_id].close()

    def close_stream_clients(self):
        for stream_client in self.stream_clients:
            stream_client.send(encode(EXIT_MESSAGE))
            stream_client.close()

    def write_to_log(self, string):
        self.log_file.write(string)
        self.log_file.flush()

    def serve(self):
        self.write_to_log(encode_for_logging(OPEN_MESSAGE))
        print(f"\n{OPEN_MESSAGE}\n")

        stream_thread = StreamThread(self)
        stream_thread.start()
        
        server = socket.socket()
        server.bind((self.host, self.order_port))
        server.listen()

        client_id = 0

        try:
            while True:
                conn, addr = server.accept()
                ip, port = addr
                
                connect_msg = f"CLIENT {str(client_id)} CONNECTED AT {ip}: {str(port)}"
                print(connect_msg)

                self.write_to_log(encode_for_logging(connect_msg))

                self.clients[client_id] = conn
                new_thread = ServeThread(self, conn, client_id)
                new_thread.start()

                client_id += 1
        except KeyboardInterrupt:
            server.close()
            self.close_order_clients()
            self.close_stream_clients()
            self.write_to_log(encode_for_logging(EXIT_MESSAGE))
            print(f"\nEXIT_MESSAGE\n")

if __name__ == "__main__":
    debug = False
    order_port = int(sys.argv[1])
    stream_port = int(sys.argv[2])
    if len(sys.argv) > 3:
        debug = bool(sys.argv[3])
    log_file = open(f"logs/log_{str(datetime.datetime.now().date())}.txt", "a")
    server = Exchange_Server('localhost', order_port, stream_port, log_file, debug)
    server.serve()
