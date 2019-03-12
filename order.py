from symbol import *

BUY = "BUY"
SELL = "SELL"

class Order:
    def __init__(self, symbol, side, price, amount):
        assert ((side == BUY) or (side == SELL))
        
        self.symbol = symbol
        self.side = side
        self.price = price
        self.amount = amount

    def copy(self):
        return Order(self.symbol, self.side, self.price, self.amount)

    def serialize(self):
        attributes = [str(self.symbol), self.side, str(self.amount), str(self.price)]
        return "|".join(attributes)

    @classmethod
    def deserialize(cls, code):
        sym, side, amount, price = code.split("|")
        sym = Symbol.deserialize(sym)
        price = float(price)
        amount = int(amount)
        return Order(sym, side, price, amount)

    def __eq__(self, other):
        same_symbol = self.symbol == other.symbol
        same_side = self.side == other.side
        same_price = self.price == other.price
        same_amount = self.amount == other.amount
        return same_amount and same_side and same_price and same_amount

    def __str__(self):
        return str(self.symbol) + " " + self.side + " " + str(self.amount) + " @ " + str(self.price)

    def __repr__(self):
        return str(self)

if __name__ == "__main__":
    bid_1 = Order(PARKER, BUY, 5, 20)
    bid_2 = Order(PARKER, BUY, 4.95, 25)
    bid_3 = Order(PARKER, BUY, 5.50, 25)

    ask_1 = Order(PARKER, SELL, 5.1, 15)
    ask_2 = Order(PARKER, SELL, 5.50, 7)

    for order in [bid_1, bid_2, bid_3, ask_1, ask_2]:
        assert Order.deserialize(order.serialize()) == order