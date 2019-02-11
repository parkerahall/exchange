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

    def serialize(self):
        attributes = [self.symbol, self.side, self.price, self.amount]
        return "|".join(attributes)

    @classmethod
    def deserialize(cls, code):
        attributes = code.split("|")
        return Order(attributes[0], attributes[1], attributes[2], attributes[3])

    def __str__(self):
        return str(self.symbol) + " " + self.side + " " + str(self.amount) + " @ " + str(self.price)

    def __repr__(self):
        return str(self)