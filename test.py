import tkinter as tk
from typing import List
import random
import math


class Player():
    def __init__(self, name, rating):
        self.name = name
        self.rating = rating
        self.previously_played = []

    def __str__(self):
        return f"{self.name}, {self.rating}, {list(map(lambda x: x.name, self.previously_played))}"


class MatchMaker:
    def __init__(self):
        self.known_players = {}

    def players_with_known(self, players):
        players_with_known = []
        for player in players:
            known_player = self.known_players.get(player.name)
            if known_player is None:
                known_player = player
            players_with_known.append(known_player)
        return players_with_known

    def get_matches(self, players: List[Player]):
        players_with_known = self.players_with_known(players)
        pairings = []
        while len(players_with_known) > 1:
            current = random.choice(players_with_known)
            players_with_known.remove(current)
            rating_differences = list(map(lambda x: abs(x.rating - current.rating), players_with_known))
            weightings = list(map(lambda x: min(max(10 * math.e ** (-(x / 800) ** 2), 1), 10), rating_differences))
            opponent = random.choices(players_with_known, weights=weightings, k=1)[0]
            i = 0
            while opponent.name in current.previously_played and i < 10:
                opponent = random.choices(players_with_known, weights=weightings, k=1)[0]
                i += 1
            if opponent.name in list(map(lambda x: x.name, current.previously_played)):
                not_played = list(set(players_with_known) - set(current.previously_played))
                if len(not_played) > 0:
                    opponent = random.choice(not_played)
            if opponent.name in list(map(lambda x: x.name, current.previously_played)):
                print(f"DUPLICATE MATCH {current.name} vs {opponent.name}")
            current.previously_played.append(opponent)
            opponent.previously_played.append(current)
            players_with_known.remove(opponent)
            self.known_players.update({current.name: current, opponent.name: opponent})
            pairings.append([current, opponent])

        if len(players_with_known) == 1:
            pairings.append([players_with_known[0], Player("Oversidder", 0)])
        return pairings


players = [Player("Lars", 1200),
           Player("Anders", 800),
           Player("Kasper", 1300),
           Player("Mads", 500),
           Player("Jonas", 2000),
           Player("Christoffer", 1700),
           Player("Emma", 850),
           Player("Nanna", 1200),
           Player("Emil", 1500),
           Player("Holger", 900),
           Player("Thomas", 200),
           Player("Louise", 300),
           Player("Søren", 900),
           Player("Helene", 1600),
           Player("Klara", 1700),
           Player("Esben", 1500),
           Player("Silvia", 1400),
           Player("Sigurt", 1400),
           Player("Troels", 1200),
           Player("Mia", 1200)]
matchmaker = MatchMaker()
i = 0
while i < 10:
    print(f"Round {i}")
    matches = matchmaker.get_matches(players)
    for pair in matches:
        print(f"{pair[0].name} vs {pair[1].name}")
    i += 1
    print("")
