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


def tiebreaker_lt(cards_a, a_ace_hi, cards_b, b_ace_hi):
    cards = [cards_a, cards_b]
    ace_hi = [a_ace_hi, b_ace_hi]
    rankings = [[c.val for c in cs] for cs in cards]
    for i in range(len(rankings)):
        if not ace_hi[i]:
            rankings[i] = [1 if r == 14 else r for r in rankings[i]]
        rankings[i].sort(reverse=True)

    for i in range(min([len(r) for r in rankings])):
        if rankings[0][i] < rankings[1][i]:
            return True
        elif rankings[0][i] > rankings[1][i]:
            return False

    if len(rankings[0]) < len(rankings[1]):
        return True
    elif len(rankings[0]) > len(rankings[1]):
        return False

    return None


class Score:
    def __init__(self, hand_type, hand_cards, cards):
        self.hand_type = hand_type
        self.hand_cards = hand_cards
        self.cards = cards
        self.cards.sort()
        self.non_hand_cards = [
            c for c in self.cards if c not in self.hand_cards
        ]

    def __str__(self):
        return "{ hand=" + HAND_NAMES[self.
                                      hand_type] + " hand_cards=" + " ".join([
                                          str(c) for c in self.hand_cards
                                      ]) + " cards=" + " ".join(
                                          [str(c) for c in self.cards]) + " }"

    def __eq__(self, other):
        return not self < other and not self > other

    def __lt__(self, other):
        if self.hand_type != other.hand_type:
            return self.hand_type < other.hand_type

        # Tiebreaker
        self_ace_hi = True
        other_ace_hi = True
        # Ace is low iff we have a straight with the ace at the bottom (no
        # king in the straight)
        hand_vals = [c.val for c in self.hand_cards]
        if self.hand_type == HandType.STRAIGHT and 13 not in hand_vals:
            self_ace_hi = False
        if other.hand_type == HandType.STRAIGHT and 13 not in hand_vals:
            other_ace_hi = False

        hand_tiebreaker = tiebreaker_lt(self.hand_cards, self_ace_hi,
                                        other.hand_cards, other_ace_hi)
        if hand_tiebreaker is not None:
            return hand_tiebreaker

        hand_size = len(self.hand_cards)
        if hand_size == 5:
            return False

        return not not tiebreaker_lt(self.non_hand_cards[-(5 - hand_size):],
                                     False, other.cards, False)


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
# CARDS MUST BE SORTED
def find_hand(cards, hand):
    assert len(cards) <= 1 or (cards[0].val <= cards[1].val
                               and cards[-2].val <= cards[-1].val
                               ), "Cards passed to find_hand must be sorted"

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
            return [card.Card(cards[-1].suit, 14)] + cards[0:4]
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


# Returns a score object if the hand can be formed, none otherwise
def try_hand(cards, hand):
    h = find_hand(cards, hand)
    if h is not None:
        return Score(hand, h, cards)


class EvalNode:
    def __init__(self, hand):
        self.hand = hand
        self.children = []
        self.best_branch_hand = None


eval_nodes = {h: EvalNode(h) for h in HandType}
eval_root = eval_nodes[HandType.HIGH_CARD]


def _link(ph, ch):
    eval_nodes[ph].children.append(eval_nodes[ch])


def best_branch_hand(eval_node):
    return max(
        [eval_node.hand] + [best_branch_hand(c) for c in eval_node.children])


_link(HandType.HIGH_CARD, HandType.FLUSH)
_link(HandType.FLUSH, HandType.STRAIGHT_FLUSH)
_link(HandType.STRAIGHT_FLUSH, HandType.ROYAL_FLUSH)
_link(HandType.HIGH_CARD, HandType.PAIR)
_link(HandType.PAIR, HandType.THREE_KIND)
_link(HandType.THREE_KIND, HandType.FOUR_KIND)
_link(HandType.THREE_KIND, HandType.FULL_HOUSE)
_link(HandType.PAIR, HandType.TWO_PAIR)
_link(HandType.HIGH_CARD, HandType.STRAIGHT)

for h in HandType:
    eval_nodes[h].best_branch_hand = best_branch_hand(eval_nodes[h])


def score(cards):
    cards.sort()
    assert len(cards) >= CARDS_TO_USE, "Must have {} cards to score".format(
        CARDS_TO_USE)

    to_expand = [eval_root]
    best_score = None
    while to_expand:
        cur = to_expand.pop()
        if best_score is None or cur.best_branch_hand > best_score.hand_type:
            to_expand.extend(cur.children)
            hand_cards = find_hand(cards, cur.hand)
            if hand_cards is not None and (best_score is None
                                           or cur.hand > best_score.hand_type):
                best_score = Score(cur.hand, hand_cards, cards)

    if best_score is not None:
        return best_score
    raise "No valid hand found"
