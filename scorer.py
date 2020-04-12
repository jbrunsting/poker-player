import enum

import card

CARDS_TO_USE = 5


class HandType(enum.IntEnum):  # Must be ordered by priority descending
    ROYAL_FLUSH = 10
    STRAIGHT_FLUSH = 9
    FOUR_KIND = 8
    FULL_HOUSE = 7
    FLUSH = 6
    STRAIGHT = 5
    THREE_KIND = 4
    TWO_PAIR = 3
    PAIR = 2
    HIGH_CARD = 1


HAND_NAMES = {
    HandType.ROYAL_FLUSH: "royal_flush ",
    HandType.STRAIGHT_FLUSH: "straight_flush",
    HandType.FOUR_KIND: "four_kind",
    HandType.FULL_HOUSE: "full_house",
    HandType.FLUSH: "flush",
    HandType.STRAIGHT: "straight",
    HandType.THREE_KIND: "three_kind",
    HandType.TWO_PAIR: "two_pair",
    HandType.PAIR: "pair",
    HandType.HIGH_CARD: "high_card",
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


def has_hand(cards, hand):
    return True


def score(cards):
    assert len(cards) >= CARDS_TO_USE, "Must have {} cards to score".format(
        CARDS_TO_USE)
    for hand in HandType:
        if has_hand(cards, hand):
            return Score(hand, cards[:CARDS_TO_USE])
    raise "No valid hand found"
