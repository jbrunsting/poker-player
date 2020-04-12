import enum

CARDS_TO_USE = 5


class HandType(enum.IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


HAND_NAMES = {
    HandType.HIGH_CARD: "high_card",
    HandType.PAIR: "pair",
    HandType.TWO_PAIR: "two_pair",
    HandType.THREE_KIND: "three_kind",
    HandType.STRAIGHT: "straight",
    HandType.FLUSH: "flush",
    HandType.FULL_HOUSE: "full_house",
    HandType.FOUR_KIND: "four_kind",
    HandType.STRAIGHT_FLUSH: "straight_flush",
    HandType.ROYAL_FLUSH: "royal_flush ",
}


class Score:
    def __init__(self, hand_type, cards):
        self.hand_type = hand_type
        self.cards = cards

    def __str__(self):
        return "{" + HAND_NAMES[self.hand_type] + " " + str(
            [str(c) for c in self.cards]) + "}"

    def __eq__(self, other):
        return not self < other and not self > other

    def __lt__(self, other):
        if self.hand_type != other.hand_type:
            return self.hand_type < other.hand_type
        # TODO: Proper tiebreaker
        return max(self.cards).val < max(other.cards).val


def score(cards):
    assert len(cards) >= CARDS_TO_USE, "Must have {} cards to score".format(
        CARDS_TO_USE)
    return Score(HandType.HIGH_CARD, cards[:CARDS_TO_USE])
