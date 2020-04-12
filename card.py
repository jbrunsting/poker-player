SUIT_INDICES = "dhsc"
MIN_CARD = 2
MAX_CARD = 14
NUM_SUITS = 4


class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val

    def __str__(self):
        return str(self.val) + SUIT_INDICES[self.suit]

    def __eq__(self, other):
        return self.suit == other.suit and self.val == other.val

    def __lt__(self, other):
        if self.val < other.val:
            return True
        if self.val > other.val:
            return False
        return self.suit < other.suit
