import socket
import symbols

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
        self.bids = []
        self.asks = []

        self.open_orders = {}

    def add(self, order, order_id):
        assert order.symbol == self.symbol

        if order.side == BUY:
            location = 0
            while True:
                if location == len(self.bids):
                    self.bids.append((order.price, order.amount, order_id))
                    break

                if order.price > self.bids[location][0]:
                    self.bids.insert(location, (order.price, order.amount, order_id))
                    break

                location += 1

        elif order.side == SELL:
            location = 0
            while True:
                if location == len(self.asks):
                    self.asks.append((order.price, order.amount, order_id))
                    break

                if order.price < self.asks[location][0]:
                    self.asks.insert(location, (order.price, order.amount, order_id))
                    break

                location += 1

        else:
            raise ValueError("INVALID ORDER SIDE")

        self.open_orders[order_id] = order

    def remove(self, order_id):
        if order_id not in self.open_orders:
            raise ValueError("ORDER NO LONGER OPEN")

        order_to_remove = self.open_orders[order_id]

        if order_to_remove.side == BUY:
            location = 0
            while location < len(self.bids):
                if self.bids[location][2] == order_id:
                    break
            del self.bids[location]

        elif order_to_remove.side == SELL:
            location = 0
            while location < len(self.asks):
                if self.asks[location][2] == order_id:
                    break
            del self.asks[location]

        else:
            raise ValueError("INVALID ORDER SIZE")

        del self.open_orders[order_id]

    def __str__(self):
        output = [str(self.symbol) + ":"]

        bid_strings = []
        bid_max_length = 0
        for bid_price, bid_amount, _ in self.bids:
            # quad spaces used here to avoid length differences due to different tab lengths
            line_string = str(bid_amount) + "    $" + str(bid_price)
            bid_max_length = max(bid_max_length, len(line_string))
            bid_strings.append(line_string)

        for i in range(len(bid_strings)):
            bid_strings[i] = bid_strings[i] + " " * (bid_max_length - len(bid_strings[i]))

        ask_strings = []
        ask_max_length = 0
        for ask_price, ask_amount, _ in self.asks:
            line_string = "$" + str(ask_price) + "\t" + str(ask_amount)
            ask_max_length = max(ask_max_length, len(line_string))
            ask_strings.append(line_string)

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