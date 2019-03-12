from order import *
from symbol import *

ADD = "ADD"
REMOVE = "REMOVE"
BOOK = "BOOK"
ALL = "ALL"

HELP = "HELP"
MY_ORDERS = "MY ORDERS"

ALL_TYPES = set([ADD, REMOVE, BOOK, HELP, MY_ORDERS])

class Message:
    def __init__(self, typ, data):
        assert typ in ALL_TYPES
        self.type = typ
        self.data = data

    def serialize(self):
        type_string = self.type + "-"
        if isinstance(self.data, int):
            type_string += str(self.data)
        elif isinstance(self.data, Order):
            type_string += Order.serialize(self.data)
        elif isinstance(self.data, Symbol):
            type_string += Symbol.serialize(self.data)
        elif isinstance(self.data, str):
            type_string += self.data
        else:
            type_string = type_string[:-1]
        return type_string

    @classmethod
    def deserialize(cls, code):
        if code == HELP:
            return Message(HELP, None)
        elif code == MY_ORDERS:
            return Message(MY_ORDERS, None)
        
        typ, data = code.split("-")
        if typ == ADD:
            data = Order.deserialize(data)
        elif typ == REMOVE:
            data = int(data)
        elif typ == BOOK:
            if data != "ALL":
                data = Symbol.from_ticker(data)
        else:
            raise ValueError("INVALID MESSAGE TYPE")
        return Message(typ, data)

    def __eq__(self, other):
        return self.type == other.type and self.data == other.data

    def __str__(self):
        return self.serialize()

if __name__ == "__main__":
    msg_1 = Message(ADD, Order(PARKER, BUY, 5, 20))
    msg_2 = Message(REMOVE, 12)
    msg_3 = Message(BOOK, PARKER)
    msg_4 = Message(BOOK, ALL)
    for msg in [msg_1, msg_2, msg_3, msg_4]:
        assert Message.deserialize(msg.serialize()) == msg