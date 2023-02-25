import discord
from enum import Enum

from typing import (
    Any,
    Generator,
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from .views import (
        UnoView,
    )


class Color(Enum):
    red = 0
    blue = 1
    yellow = 2
    green = 3


class Direction(Enum):
    clockwise = 1
    anticlockwise = -1


class UnoTracker:
    def __init__(self, view: 'UnoView') -> None:
        self.view = view
        self.players: dict[discord.User | discord.Member, dict[str, Any]] = {}
        self.moves_to_call_uno = 1
    
    def check_uno(self, player: discord.User | discord.Member) -> None:
        if len(self.view.hands[player]) == 1:
            self.players[player] = {
                'total_moves': self.view.total_moves,
                'called': False,
            }

    def called(self, player: discord.User | discord.Member) -> None:
        self.players[player]['called'] = True

    def append(self, player: discord.User | discord.Member, /) -> None:
        self.called(player=player)
    
    def __iter__(self) -> Generator[discord.User | discord.Member, None, None]:
        for player, data in self.players.items():
            if data.get('called') is True:
                yield player
    
    def update(self) -> None:
        for player in self.view.players:
            card_count = len(self.view.hands[player])
            if card_count == 0:
                if player in self.players:
                    del self.players[player]
                continue

            if player in self.players:
                data = self.players[player]
                if card_count > 1:
                    del self.players[player]
                    continue
                elif data.get('called') is False and self.view.total_moves - data.get('total_moves', 0) >= self.moves_to_call_uno:
                    self.view.draw_cards(player=player, amount=2)
                    del self.players[player]
                    continue

            else:
                self.check_uno(player=player)
