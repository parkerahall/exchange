import socket
import symbols

from linked_list import LinkedListNode
from linked_list import LinkedList

BUY = "BUY"
SELL = "SELL"

class Order:
    def __init__(self, symbol, side, price, amount):
        assert ((side == BUY) or (side == SELL))
        
        self.symbol = symbol
        self.side = side
        self.price = price
        self.amount = amount

    def __str__(self):
        return str(self.symbol) + " " + self.side + " " + str(self.amount) + " @ " + str(self.price)

    def __repr__(self):
        return str(self)

class Book:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bids = LinkedList()
        self.asks = LinkedList()

        self.open_orders = {}

    def add(self, order, order_id):
        assert order.symbol == self.symbol

        order_node = LinkedListNode(order_id, order)

        if order.side == BUY:
            current_node = self.bids.head
            while current_node != None:
                if order_node.value.price > current_node.value.price:
                    self.bids.add_before(order_node, current_node)
                    break
                current_node = current_node.next
            if current_node == None:
                self.bids.append_back(order_node)

        elif order.side == SELL:
            current_node = self.asks.head
            while current_node != None:
                if order_node.value.price < current_node.value.price:
                    self.asks.add_before(order_node, current_node)
                    break
                current_node = current_node.next
            if current_node == None:
                self.asks.append_back(order_node)

        else:
            raise ValueError("INVALID ORDER SIDE")

        self.open_orders[order_id] = order_node

    def remove(self, order_id):
        if order_id not in self.open_orders:
            raise ValueError("ORDER NO LONGER OPEN")

        order_node_to_remove = self.open_orders[order_id]

        if order_node_to_remove.value.side == BUY:
            self.bids.remove(order_node_to_remove)
        elif order_node_to_remove.value.side == SELL:
            self.asks.remove(order_node_to_remove)
        else:
            raise ValueError("INVALID ORDER SIZE")

        del self.open_orders[order_id]

    def __str__(self):
        output = [str(self.symbol) + ":"]

        bid_strings = []
        bid_max_length = 0
        current_node = self.bids.head
        while current_node != None:
            current_order = current_node.value
            bid_price = current_order.price
            bid_amount = current_order.amount

            # quad spaces used here to avoid length differences due to different tab lengths
            line_string = str(bid_amount) + "    $" + str(bid_price)
            bid_max_length = max(bid_max_length, len(line_string))
            bid_strings.append(line_string)

            current_node = current_node.next

        for i in range(len(bid_strings)):
            bid_strings[i] = bid_strings[i] + " " * (bid_max_length - len(bid_strings[i]))

        ask_strings = []
        ask_max_length = 0
        current_node = self.asks.head
        while current_node != None:
            current_order = current_node.value
            ask_price = current_order.price
            ask_amount = current_order.amount

            line_string = "$" + str(ask_price) + "\t" + str(ask_amount)
            ask_max_length = max(ask_max_length, len(line_string))
            ask_strings.append(line_string)

            current_node = current_node.next

        for i in range(len(ask_strings)):
            ask_strings[i] = ask_strings[i] + " " * (ask_max_length - len(ask_strings[i]))

        min_length = min(len(bid_strings), len(ask_strings))
        
        for i in range(min_length):
            line_string = bid_strings[i] + " | " + ask_strings[i]
            output.append(line_string)

        for i in range(min_length, len(bid_strings)):
            line_string = bid_strings[i] + " | "
            output.append(line_string)

        empty_bid = " " * bid_max_length
        for i in range(min_length, len(ask_strings)):
            line_string = empty_bid + " | " + ask_strings[i]
            output.append(line_string)

        return "\n".join(output)

class Exchange_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.books = {}

if __name__ == "__main__":
    bid_1 = Order(symbols.PARKER, BUY, 5, 20)
    bid_2 = Order(symbols.PARKER, BUY, 4.95, 25)

    ask_1 = Order(symbols.PARKER, SELL, 5.1, 15)
    ask_2 = Order(symbols.PARKER, SELL, 5.50, 7)

    orders = [bid_1, bid_2, ask_1, ask_2]

    book = Book(symbols.PARKER)
    for i in range(len(orders)):
        book.add(orders[i], i)
    print(book)

    book.remove(2)
    print(book)