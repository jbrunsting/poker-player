SUIT_INDICES = "shdc"
MIN_CARD = 2
MAX_CARD = 14
NUM_SUITS = 4


class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val

    def __str__(self):
        unicode_card = ord('🂠')
        if self.val <= 10:
            unicode_card += self.val
        elif self.val == 11:
            unicode_card += 11
        elif self.val == 12:
            unicode_card += 13
        elif self.val == 13:
            unicode_card += 14
        elif self.val == 14:
            unicode_card += 1
        unicode_card += self.suit * 16
        return chr(unicode_card)

    def __eq__(self, other):
        return self.suit == other.suit and self.val == other.val

    def __lt__(self, other):
        if self.val < other.val:
            return True
        if self.val > other.val:
            return False
        return self.suit < other.suit
