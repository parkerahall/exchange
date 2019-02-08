class Symbol:
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

PARKER = Symbol("Parker", "PAH")
JAKE   = Symbol("Jake", "JJG")
ZEKE   = Symbol("Zeke", "BEL")