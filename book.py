import symbol

from order import *

from linked_list import *

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

        return self.match(order.side)

    def remove(self, order_id):
        if order_id not in self.open_orders:
            raise ValueError("ORDER NO LONGER OPEN")

        order_node_to_remove = self.open_orders[order_id]

        if order_node_to_remove.value.side == BUY:
            self.bids.remove(order_node_to_remove)
        elif order_node_to_remove.value.side == SELL:
            self.asks.remove(order_node_to_remove)
        else:
            raise ValueError("INVALID ORDER SIDE")

        del self.open_orders[order_id]

    def match(self, side):
        best_bid = self.bids.head
        best_ask = self.asks.head

        if best_bid == None or best_ask == None:
            return []

        best_bid_order = best_bid.value
        best_ask_order = best_ask.value

        filled_orders = []
        while best_bid_order.price >= best_ask_order.price:
            if side == BUY:
                strike_price = best_bid_order.price
            elif side == SELL:
                strike_price = best_ask_order.price
            else:
                raise ValueError("INVALID ORDER SIDE")

            fill_size = min(best_bid_order.amount, best_ask_order.amount)
            
            filled_bid = Order(best_bid_order.symbol, BUY, strike_price, fill_size)
            filled_orders.append((best_bid.key, best_bid_order.copy(), filled_bid))
            
            filled_ask = Order(best_ask_order.symbol, SELL, strike_price, fill_size)
            filled_orders.append((best_ask.key, best_ask_order.copy(), filled_ask))
            
            should_break = False
            if best_bid_order.amount > fill_size:
                best_bid_order.amount -= fill_size
            else:
                self.remove(best_bid.key)
                best_bid = self.bids.head
                # the list may now be empty
                if best_bid == None:
                    should_break = True
                else:
                    best_bid_order = best_bid.value

            if best_ask_order.amount > fill_size:
                best_ask_order.amount -= fill_size
            else:
                self.remove(best_ask.key)
                best_ask = self.asks.head
                # the list may now be empty
                if best_ask == None:
                    should_break = True
                else:
                    best_ask_order = best_ask.value
            if should_break:
                break

        return filled_orders

    def get_open_order(self, order_id):
        return self.open_orders[order_id].value

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

    def __repr__(self):
        return str(self)

if __name__ == "__main__":
    # bid_1 = Order(symbol.PARKER, BUY, 5, 20)
    # bid_2 = Order(symbol.PARKER, BUY, 4.95, 25)
    # bid_3 = Order(symbol.PARKER, BUY, 5.50, 25)

    # ask_1 = Order(symbol.PARKER, SELL, 5.1, 15)
    # ask_2 = Order(symbol.PARKER, SELL, 5.50, 7)

    bid = Order(symbol.PARKER, BUY, 20, 10)
    ask = Order(symbol.PARKER, SELL, 20, 10)
    orders = [bid, ask]

    book = Book(symbol.PARKER)
    for i in range(len(orders)):
        filled = book.add(orders[i], i)
        print(filled)
        print(book)