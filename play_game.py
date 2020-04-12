#!/usr/bin/python3

import random

import card
import scorer

CARD_FORMAT_MSG = "Card format is [shdc][1-10,jqka]"
CARDS_IN_HAND = 2
CARDS_IN_RIVER = 5


def print_cards(cards):
    print([str(c) for c in cards])


def cards_diff(cards, to_remove):
    return [c for c in cards if c not in to_remove]


def get_deck():
    deck = []
    for s in range(len(card.SUIT_INDICES)):
        for i in range(card.MIN_CARD, card.MAX_CARD + 1):
            deck.append(card.Card(s, i))
    return deck


def card_input():
    suit = -1
    print_fmt = False
    while True:
        c = input("> ")
        if len(c) == 2 or len(c) == 3 and c[-1] in card.SUIT_INDICES:
            suit = card.SUIT_INDICES.find(c[-1])
            if c[:-1] == "j":
                c = 11
            elif c[:-1] == "q":
                c = 12
            elif c[:-1] == "k":
                c = 13
            elif c[:-1] == "a":
                c = 14
            else:
                try:
                    c = int(c[:-1])
                except ValueError:
                    c = -1
            if 0 <= suit and suit < len(
                    card.SUIT_INDICES
            ) and card.MIN_CARD <= c and c <= card.MAX_CARD:
                return card.Card(suit, c)
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
    testscore = scorer.score([
        card.Card(0, 9),
        card.Card(1, 10),
        card.Card(3, 10),
        card.Card(0, 12),
        card.Card(0, 13),
        card.Card(1, 9),
        card.Card(0, 10),
    ])
    print("Test score is {}".format(testscore))


while True:
    try:
        players = int(input("Number of players: "))
        print("Enter your hand: ")
        hand = [card_input() for i in range(CARDS_IN_HAND)]
        simulate_game(players, hand)
    except ValueError:
        pass
