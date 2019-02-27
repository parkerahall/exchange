class Symbol:
    def __init__(self, actual, ticker):
        self.actual = actual
        self.ticker = ticker

    def serialize(self):
        return str(self)

    @classmethod
    def deserialize(cls, code):
        actual, ticker = code.split(" ")
        ticker = ticker[1:-1]
        return Symbol(actual, ticker)

    def __lt__(self, other):
        return self.ticker < other.ticker

    def __eq__(self, other):
        return self.ticker == other.ticker

    def __str__(self):
        return self.actual + " (" + self.ticker + ")"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

PARKER = Symbol("Parker", "PAH")
JAKE   = Symbol("Jake", "JJG")
ZEKE   = Symbol("Zeke", "BEL")
ALL_SYMBOLS = [PARKER, JAKE, ZEKE]

if __name__ == "__main__":
    for sym in [PARKER, JAKE, ZEKE]:
        assert Symbol.deserialize(sym.serialize()) == sym