import enum

import card


def card_input(c):
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


class Param(enum.IntEnum):
    CARD = 1
    STRING = 2
    NUMBER = 3


class Command:
    def __init__(self, name, params, func):
        self.name = name
        self.params = params
        self.func = func

    def parse(self, command):
        components = command.split()
        if len(components) == 0 or components[0] != self.name:
            return None
        components = components[1:]

        results = []
        for p in self.params:
            if not components:
                return None

            if p == Param.CARD:
                c = card_input(components[0])
                if c is None:
                    break
                results.append(c)
            elif p == Param.STRING:
                results.append(components[0])
            elif p == Param.NUMBER:
                try:
                    results.append(int(components[0]))
                except ValueError:
                    return None
            components = components[1:]

        self.func(results)
