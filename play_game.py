#!/usr/bin/python3

import enum
import random
from multiprocessing import Manager, Process

import card
import scorer

CARD_FORMAT_MSG = "Card format is [shdc][1-10,jqka]"
CARDS_IN_HAND = 2
CARDS_IN_RIVER = 5
NUM_ITERS = 25000
NUM_THREADS = 10


class GameOutcome(enum.IntEnum):
    TIE = 1
    WIN = 2
    LOSS = 3


def card_str(cards):
    return " ".join([str(c) for c in cards])


def cards_diff(cards, to_remove):
    return [c for c in cards if c not in to_remove]


class Deck:
    def __init__(self, to_exclude):
        self.deck = []
        for s in range(len(card.SUIT_INDICES)):
            for i in range(card.MIN_CARD, card.MAX_CARD + 1):
                exclude = False
                for c in to_exclude:
                    if c.suit == s and c.val == i:
                        exclude = True
                        break
                if not exclude:
                    self.deck.append(card.Card(s, i))
        self.len = len(self.deck)

    def reset(self):
        self.len = len(self.deck)

    def pop(self):
        i = random.randint(0, self.len - 1)
        self.deck[i], self.deck[-1] = self.deck[-1], self.deck[i]
        self.len -= 1
        return self.deck[self.len]


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


def simulate_game(players, deck, hand):
    river = [deck.pop() for i in range(CARDS_IN_RIVER)]
    player_hands = [[deck.pop() for i in range(CARDS_IN_HAND)]
                    for i in range(players - 1)]

    your_score = scorer.score(hand + river)
    player_scores = [scorer.score(hand + river) for hand in player_hands]

    max_player = max(player_scores)
    if your_score < max_player:
        return GameOutcome.LOSS
    elif your_score > max_player:
        return GameOutcome.WIN
    return GameOutcome.TIE


def simulate_games(players, hand, num_games, results_map):
    deck = Deck(hand)
    for i in range(num_games):
        deck.reset()
        results_map[simulate_game(players, deck, hand)] += 1


while True:
    try:
        players = int(input("Number of players: "))
        print("Enter your hand: ")
        hand = [card_input() for i in range(CARDS_IN_HAND)]
        counts = {g: 0 for g in GameOutcome}

        manager = Manager()
        thread_counts = [manager.dict() for i in range(NUM_THREADS)]
        for i in range(NUM_THREADS):
            for g in GameOutcome:
                thread_counts[i][g] = 0

        threads = []
        for i in range(NUM_THREADS):
            p = Process(
                target=simulate_games,
                args=(players, hand, int(NUM_ITERS / NUM_THREADS),
                      thread_counts[i]))
            threads.append(p)
            p.start()
        for i in range(NUM_THREADS):
            p.join()

        counts = {g: sum(cs[g] for cs in thread_counts) for g in GameOutcome}

        percentages = {g: c / NUM_ITERS for g, c in counts.items()}
        o_strings = {
            GameOutcome.TIE: "tie",
            GameOutcome.WIN: "win",
            GameOutcome.LOSS: "loss"
        }
        percentage_strings = {o_strings[o]: c for o, c in percentages.items()}
        print("Outcomes for hand {}  are {}".format(" ".join(
            [str(c) for c in hand]), percentage_strings))
    except ValueError:
        pass
