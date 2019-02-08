class LinkedListNode:
    def __init__(self, value, prev=None, nxt=None):
        self.value = value
        self.prev = prev
        self.next = nxt

class LinkedList:
    def __init__(self):
        self.head = None
        self.length = 0

    def add(self, node):
        node.prev = None
        node.next = self.head

        if self.head != None:
            self.head.prev = node
        self.head = node

        self.length += 1

    def remove(self, node):
        if node.next != None:
            node.next.prev = node.prev

        if node.prev != None:
            node.prev.next = node.next
        else:
            self.head = node.next

        self.length -= 1