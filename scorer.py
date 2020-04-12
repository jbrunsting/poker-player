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
    def __init__(self, hand_type, hand_cards, cards):
        self.hand_type = hand_type
        self.hand_cards = hand_cards
        self.cards = cards

    def __str__(self):
        return "{ hand=" + HAND_NAMES[self.hand_type] + " hand_cards=" + str([
            str(c) for c in self.hand_cards
        ]) + " cards=" + str([str(c) for c in self.cards]) + " }"

    def __eq__(self, other):
        return not self < other and not self > other

    def __lt__(self, other):
        if self.hand_type != other.hand_type:
            return self.hand_type < other.hand_type
        # TODO: Proper tiebreaker
        return max(self.cards).val < max(other.cards).val


def find_n_kind(cards, n):
    num_sequential = 1
    for i in reversed(range(len(cards) - 1)):
        if cards[i].val == cards[i + 1].val:
            num_sequential += 1
        else:
            num_sequential = 1
        if num_sequential == n:
            return cards[i:i + n]
    return None


# Returns the cards making up the hand, or None of the hand does not exist
def find_hand(cards, hand):
    cards.sort()
    if hand == HandType.ROYAL_FLUSH:
        # We have a royal flush iff we have a straight flush with only cards
        # >= 10
        return find_hand([c for c in cards if c.val >= 10],
                         HandType.STRAIGHT_FLUSH)
    elif hand == HandType.STRAIGHT_FLUSH:
        # We do this whole best_straight thing to account for cases where we
        # have 10 cards or more, since in those cases we could have multiple
        # suits with a straight flush and we should pick the best one
        best_straight = None
        for suit in range(card.NUM_SUITS):
            straight = find_hand([c for c in cards if c.suit == suit],
                                 HandType.STRAIGHT)
            if straight and (best_straight is None
                             or straight[-1].val > best_straight[-1].val):
                best_straight = straight
        return best_straight
    elif hand == HandType.FOUR_KIND:
        return find_n_kind(cards, 4)
    elif hand == HandType.FULL_HOUSE:
        three_kind = find_hand(cards, HandType.THREE_KIND)
        if three_kind is not None:
            pair = find_hand([c for c in cards if c not in three_kind],
                             HandType.PAIR)
            if pair is not None:
                return pair + three_kind
        return None
    elif hand == HandType.FLUSH:
        best_flush = None
        for suit in range(card.NUM_SUITS):
            suit_cards = [c for c in cards if c.suit == suit]
            if len(suit_cards) >= 5 and (
                    best_flush is None
                    or suit_cards[-1].val > best_flush[-1].val):
                best_flush = suit_cards[len(suit_cards) - 5:]
    elif hand == HandType.STRAIGHT:
        if len(cards) < 5:
            return None
        num_sequential = 1
        for i in reversed(range(len(cards) - 1)):
            if cards[i].val + 1 == cards[i + 1].val:
                num_sequential += 1
            elif cards[i].val != cards[i + 1].val:
                num_sequential = 1
            if num_sequential == 5:
                return cards[i:i + 5]
        if num_sequential == 4 and cards[0].val == 2 and cards[-1].val == 14:
            return [14] + cards[0:4]
        return None
    elif hand == HandType.THREE_KIND:
        return find_n_kind(cards, 3)
    elif hand == HandType.TWO_PAIR:
        pair_1 = find_hand(cards, HandType.PAIR)
        if pair_1 is not None:
            pair_2 = find_hand([c for c in cards if c not in pair_1],
                               HandType.PAIR)
            if pair_2 is not None:
                return pair_1 + pair_2
        return None
    elif hand == HandType.PAIR:
        return find_n_kind(cards, 2)
    elif hand == HandType.HIGH_CARD:
        return [max(cards)]


def score(cards):
    assert len(cards) >= CARDS_TO_USE, "Must have {} cards to score".format(
        CARDS_TO_USE)
    for hand in HandType:
        hand_cards = find_hand(cards, hand)
        if hand_cards is not None:
            return Score(hand, hand_cards, cards)
    raise "No valid hand found"
