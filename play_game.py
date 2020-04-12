#!/usr/bin/python3

import random
import scorer

CARDS_IN_HAND = 2
CARDS_IN_RIVER = 5
NUM_SUITS = 4
CARD_FORMAT_MSG = "Card format is [dhsc][1-13]"
SUIT_INDICES = "dhsc"
MIN_CARD = 1
MAX_CARD = 13


class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val

    def __str__(self):
        return SUIT_INDICES[self.suit] + str(self.val)

    def __eq__(self, other):
        return self.suit == other.suit and self.val == other.val

    def __lt__(self, other):
        if self.val < other.val:
            return True
        if self.val > other.val:
            return False
        return self.suit < other.suit


def print_cards(cards):
    print([str(c) for c in cards])


def cards_diff(cards, to_remove):
    return [c for c in cards if c not in to_remove]


def get_deck():
    deck = []
    for s in range(len(SUIT_INDICES)):
        for i in range(MIN_CARD, MAX_CARD + 1):
            deck.append(Card(s, i))
    return deck


def card_input():
    suit = -1
    print_fmt = False
    while True:
        card = input("> ")
        if len(card) == 2 or len(card) == 3 and card[0] in SUIT_INDICES:
            suit = SUIT_INDICES.find(card[0])
            card = int(card[1:])
            if MIN_CARD <= card and card <= MAX_CARD:
                return Card(suit, card)
        print(CARD_FORMAT_MSG)


def simulate_game(players, hand):
    print_cards(hand)

    deck = get_deck()

    print_cards(deck)

    deck = cards_diff(deck, hand)
    random.shuffle(deck)

    print_cards(deck)

    river = [deck.pop() for i in range(CARDS_IN_RIVER)]
    player_hands = [[deck.pop() for i in range(CARDS_IN_HAND)]
                    for i in range(players)]

    print("River:")
    print_cards(river)
    print("Players:")
    [print_cards(h) for h in player_hands]

    score1 = scorer.score(hand + river)
    score2 = scorer.score(player_hands[0] + river)
    print("Your score is {}".format(score1))
    print("Player 1 score is {}".format(score2))
    if score1 == score2:
        print("Tie!")
    elif score1 > score2:
        print("You win")
    elif score1 < score2:
        print("You lose!")
    else:
        print("Something broke!")


while True:
    players = int(input("Number of players: "))
    print("Enter your hand: ")
    hand = [card_input() for i in range(CARDS_IN_HAND)]
    simulate_game(players, hand)
