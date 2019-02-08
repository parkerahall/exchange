class LinkedListNode:
    def __init__(self, key, value, prev=None, nxt=None):
        self.key = key
        self.value = value
        self.prev = prev
        self.next = nxt

    def __str__(self):
        return "LinkedListNode(key=" + str(self.key) + ", value=" + str(self.value)

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def add_before(self, new_node, old_node):
        # case where adding to empty list
        if old_node == None:
            self.head = new_node
            self.tail = new_node

            new_node.prev = None
            new_node.next = None

        else:
            new_node.next = old_node
            new_node.prev = old_node.prev

            if old_node.prev != None:
                old_node.prev.next = new_node
            else:
                self.head = new_node

            old_node.prev = new_node

        self.length += 1

    def add_behind(self, new_node, old_node):
        # case where adding to empty list
        if old_node == None:
            self.head = new_node
            self.tail = new_node

            new_node.prev = None
            new_node.next = None

        else:
            new_node.prev = old_node
            new_node.next = old_node.next

            if old_node.next != None:
                old_node.next.prev = new_node
            else:
                self.tail = new_node

            old_node.next = new_node

        self.length += 1

    def append_front(self, new_node):
        self.add_before(new_node, self.head)

    def append_back(self, new_node):
        self.add_behind(new_node, self.tail)

    def remove(self, node):
        if node.next != None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        if node.prev != None:
            node.prev.next = node.next
        else:
            self.head = node.next

        self.length -= 1

    def __len__(self):
        return self.length