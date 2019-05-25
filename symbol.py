TICKER_TO_ACTUAL = {"PAH": "Parker",
                    "JJG": "Jake",
                    "BEL": "Zeke",
                    "NCW": "Nate",
                    "MAK": "Mike"}

class Symbol:
    def __init__(self, actual, ticker):
        self.actual = actual
        self.ticker = ticker

    def serialize(self):
        return self.ticker

    @classmethod
    def from_ticker(cls, ticker):
        return Symbol(TICKER_TO_ACTUAL[ticker], ticker)

    @classmethod
    def deserialize(cls, code):
        return Symbol.from_ticker(code)

    def __lt__(self, other):
        return self.ticker < other.ticker

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return self.ticker == other.ticker

    def __str__(self):
        return f"{self.actual} ({self.ticker})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

PARKER = Symbol("Parker", "PAH")
JAKE   = Symbol("Jake", "JJG")
ZEKE   = Symbol("Zeke", "BEL")
NATE   = Symbol("Nate", "NCW")
MIKE   = Symbol("Mike", "MAK")
ALL_SYMBOLS = [PARKER, JAKE, ZEKE, NATE, MIKE]

if __name__ == "__main__":
    for sym in ALL_SYMBOLS:
        assert Symbol.deserialize(sym.serialize()) == sym