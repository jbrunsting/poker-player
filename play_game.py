#!/usr/bin/python3

import random

import card
import scorer

CARD_FORMAT_MSG = "Card format is [shdc][1-10,jqka]"
CARDS_IN_HAND = 2
CARDS_IN_RIVER = 5


def card_str(cards):
    return " ".join([str(c) for c in cards])


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
    print("Hand: {}".format(card_str(hand)))

    deck = cards_diff(get_deck(), hand)
    random.shuffle(deck)

    river = [deck.pop() for i in range(CARDS_IN_RIVER)]
    player_hands = [[deck.pop() for i in range(CARDS_IN_HAND)]
                    for i in range(players)]

    print("River: {}".format(card_str(river)))
    print("Players: [{} ]".format(" , ".join(
        [card_str(h) for h in player_hands])))

    your_score = scorer.score(hand + river)
    player_scores = [scorer.score(hand + river) for hand in player_hands]

    print("Your score is {}".format(your_score))
    for i, score in enumerate(player_scores):
        print("Player {} score is {}".format(i + 1, score))

    max_player = max(player_scores)
    if your_score == max_player:
        print("Tie!")
    elif your_score > max_player:
        print("You win")
    elif your_score < max_player:
        print("You lose!")
    else:
        print("Something broke!")


while True:
    try:
        players = int(input("Number of players: "))
        print("Enter your hand: ")
        hand = [card_input() for i in range(CARDS_IN_HAND)]
        simulate_game(players, hand)
    except ValueError:
        pass
