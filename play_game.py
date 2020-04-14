#!/usr/bin/python3

import enum
import random
from multiprocessing import Manager, Process

import card
import command
import scorer

CARD_FORMAT_MSG = "Card format is [shdc][1-10,jqka]"
CARDS_IN_HAND = 2
CARDS_IN_RIVER = 5
NUM_ITERS = 25000
NUM_THREADS = 10


def cards_str(cards):
    return " ".join(str(c) for c in cards) + " "


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
        self.deck[i], self.deck[self.len - 1] = self.deck[self.len
                                                          - 1], self.deck[i]
        self.len -= 1
        return self.deck[self.len]


def simulate_game(players, deck, hand, table):
    hand += [deck.pop() for i in range(CARDS_IN_HAND - len(hand))]
    table += [deck.pop() for i in range(CARDS_IN_RIVER - len(table))]
    player_hands = [[deck.pop() for i in range(CARDS_IN_HAND)]
                    for i in range(players - 1)]
    your_score = scorer.score(hand + table)
    player_scores = [scorer.score(h + table) for h in player_hands]

    if not player_scores:
        return GameOutcome.WIN

    max_player = max(player_scores)
    if your_score < max_player:
        return GameOutcome.LOSS
    elif your_score > max_player:
        return GameOutcome.WIN
    return GameOutcome.TIE


def simulate_games(players, hand, table, num_games, results_map):
    deck = Deck(hand + table)
    for i in range(num_games):
        deck.reset()
        results_map[simulate_game(players, deck, hand + [], table + [])] += 1


g_players = 1
g_hand = []
g_flop = []
g_turn = []
g_river = []
g_commands = []


def print_river():
    print("River is {} ".format(", ".join(
        [str(c) for c in g_flop + g_turn + g_river])))


def set_players(params):
    global g_players
    g_players = params[0]
    print("Set the number of player to {}".format(g_players))


def set_hand(params):
    g_hand = params
    print("Set hand to {} ".format(cards_str(params)))


def set_flop(params):
    global g_flop
    g_flop = params
    print_river()


def set_turn(params):
    global g_turn
    g_turn = params
    print_river()


def set_river(params):
    global g_river
    g_river = params
    print_river()


def reset(params):
    global g_players
    global g_hand
    global g_flop
    global g_turn
    global g_river
    g_players = 1
    g_hand = []
    g_flop = []
    g_turn = []
    g_river = []


def make_prediction(params):
    table = g_flop + g_turn + g_river

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
            args=(g_players, g_hand, table, int(NUM_ITERS / NUM_THREADS),
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
    print("Outcomes for hand [{}], table [{}] are {}".format(
        cards_str(g_hand), cards_str(table), percentage_strings))


def command_help(params):
    g_players = 4
    print("Commands are [{}]".format(", ".join([c.name for c in g_commands])))


g_commands.append(
    command.Command("players", [command.Param.NUMBER], set_players))
g_commands.append(
    command.Command("hand", [command.Param.CARD, command.Param.CARD],
                    set_hand))
g_commands.append(
    command.Command(
        "flop", [command.Param.CARD, command.Param.CARD, command.Param.CARD],
        set_hand))
g_commands.append(command.Command("turn", [command.Param.CARD], set_river))
g_commands.append(
    command.Command("river", [command.Param.CARD], make_prediction))
g_commands.append(command.Command("reset", [], reset))
g_commands.append(command.Command("predict", [], make_prediction))
g_commands.append(command.Command("help", [], command_help))

while True:
    i = input("> ")
    if i == "quit":
        break
    foundCommand = False
    for c in g_commands:
        params = c.parse(i)
