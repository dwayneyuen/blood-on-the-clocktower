from typing import NamedTuple

MINIMUM_PLAYERS = 5


class Configuration(NamedTuple):
    players: int
    minions: int
    outsiders: int
    townsfolk: int
    demons: int


CONFIGURATIONS = [
    None,  # 0
    None,  # 1
    None,  # 2
    None,  # 3
    None,  # 4
    Configuration(players=5, minions=1, outsiders=0, townsfolk=3, demons=1),
    Configuration(players=6, minions=1, outsiders=1, townsfolk=3, demons=1),
    Configuration(players=7, minions=1, outsiders=0, townsfolk=5, demons=1),
    Configuration(players=8, minions=1, outsiders=1, townsfolk=5, demons=1),
    Configuration(players=9, minions=1, outsiders=2, townsfolk=5, demons=1),
    Configuration(players=10, minions=2, outsiders=0, townsfolk=7, demons=1),
    Configuration(players=11, minions=2, outsiders=1, townsfolk=7, demons=1),
    Configuration(players=12, minions=2, outsiders=2, townsfolk=7, demons=1),
    Configuration(players=13, minions=3, outsiders=0, townsfolk=9, demons=1),
    Configuration(players=14, minions=3, outsiders=1, townsfolk=9, demons=1),
    Configuration(players=15, minions=3, outsiders=2, townsfolk=9, demons=1),
]
