import socket

BUY = "BUY"
SELL = "SELL"

class Symbols:
    def __init__(self, actual, ticker):
        self.actual = actual
        self.ticker = ticker

    def __lt__(self, other):
        return self.ticker < other.ticker

    def __eq__(self, other):
        return self.ticker == other.ticker

    def __str__(self):
        return self.actual + " (" + self.ticker + ")"

    def __repr__(self, other):
        return str(self)

    def __hash__(self):
        return hash(str(self))

class Order:
    def __init__(self, symbol, side, price, amount):
        assert ((self.side == BUY) or (self.side == SELL))
        
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

    def add(self, order, order_id):
        assert order.symbol == self.symbol

        if order.side == BUY:
            location = 0
            while True:
                if index == len(self.bids):
                    self.bids.append((order.price, order.amount, order_id))
                    break

                if order.price > self.bids[location][0]:
                    self.bids.insert(location, (order.price, order.amount, order_id))
                    break

                location += 1

        elif order.side == SELL:
            location = 0
            while True:
                if index == len(self.asks):
                    self.asks.append((order.price, order.amount, order_id))
                    break

                if order.price < self.bids[location][0]:
                    self.asks.insert(location, (order.price, order.amount, order_id))
                    break

                location += 1

        else:
            raise ValueError("INVALID ORDER SIDE")

    def __str__(self):
        output = [self.symbol + ":"]
        min_length = min(len(self.bids), len(self.asks))

        for i in range(min_length):
            bid_price, bid_amount, _ = self.bids[i]
            ask_price, ask_amount, _ = self.asks[i]

            line_string = str(bid_amount) + " $" + str(bid_price) + "\t|\t$" + str(ask_price) + " " + str(ask_amount)
            output.append(line_string)

        for i in range(min_length, len(self.bids) - min_length):
            bid_price, bid_amount, _ = self.bids[i]

            line_string = str(bid_amount) + " $" + str(bid_price) + "\t|"
            output.append(line_string)

        for i in range(min_length, len(self.asks) - min_length):
            ask_price, ask_amount, _ = self.asks[i]

            line_string = "\t\t|\t$" + str(ask_price) + " " + str(ask_amount)
            output.append(line_string)

        return "\n".join(output)


class Exchange_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.books = {}