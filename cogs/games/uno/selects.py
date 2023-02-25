import discord
from typing import (
    TYPE_CHECKING,
)
if TYPE_CHECKING:
    from .cards import (
        Card,
    )


class ColorSelect(discord.ui.Select):
    def __init__(self, card: 'Card', total_moves: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.card = card
        self.total_moves = total_moves


class CardSelect(discord.ui.Select):
    pass
