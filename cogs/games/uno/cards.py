import discord
from utils import (
    Emoji,
)
from .selects import (
    ColorSelect,
)
from .other import (
    Direction,
    Color,
)
import os

from typing import (
    TYPE_CHECKING,
    Optional,
    Callable,
    final,
)
from typing_extensions import (
    Self,
)
if TYPE_CHECKING:
    from .views import (
        UnoView,
    )


class Card:
    total_moves_at_draw: int
    color_select: Callable[[discord.User | discord.Member], ColorSelect]
    def __init__(self, view: 'UnoView', value: Optional[int], color: Optional[Color]) -> None:
        self.view = view
        self.value = value
        self.color = color
        self.set_id()

    @property
    def id(self) -> str:
        return self._id

    def set_id(self) -> None:
        self._id = os.urandom(16).hex()
        self.view.id_to_card[self.id] = self

    def _check_color(self) -> bool:
        return self.color is not None and self.color == self.view.current_color
    
    def _same_type(self) -> bool:
        return type(self) == type(self.view.top_card) if type(self) != NumberCard else False

    def _check_value(self) -> bool:
        """
        Checks if the card can be played based on the value of the card

        Examples:
        Green 1, Blue 1: True,
        Yellow Reverse, Blue 1: False,
        Red Reverse, Green Reverse: True
        """
        return self.value == self.view.top_card.value if type(self) == NumberCard else self._same_type()

    def _can_play(self) -> bool:
        return self._check_color() or self._check_value()

    def _on_play(self, *args, **kwargs) -> None:
        pass

    def _play(self, player: discord.User | discord.Member) -> None:
        self.view.hands[player].remove(self)
        self.view.used.append(self)
        if self.color is not None:
            self.view.current_color = self.color
        self.view.next_turn()

    def _color_select(self, player: discord.User | discord.Member) -> ColorSelect:
        count: dict[int, int] = {
            color.value: sum(card.color == color for card in self.view.hands[player]) for color in Color
        }

        select = ColorSelect(
            card=self,
            total_moves=self.view.total_moves,
            placeholder=f'Select a color for {str(self)}',
            options=sorted([
                discord.SelectOption(label='Red', emoji=Emoji('🟥'), value=str(Color.red.value), description=f'{count[Color.red.value]} card{"s"*(count[Color.red.value] != 1)}'),
                discord.SelectOption(label='Blue', emoji=Emoji('🟦'), value=str(Color.blue.value), description=f'{count[Color.blue.value]} card{"s"*(count[Color.blue.value] != 1)}'),
                discord.SelectOption(label='Yellow', emoji=Emoji('🟨'), value=str(Color.yellow.value), description=f'{count[Color.yellow.value]} card{"s"*(count[Color.yellow.value] != 1)}'),
                discord.SelectOption(label='Green', emoji=Emoji('🟩'), value=str(Color.green.value), description=f'{count[Color.green.value]} card{"s"*(count[Color.green.value] != 1)}'),
            ], key=lambda option: count[int(option.value)], reverse=True),
            custom_id='color_select',
        )
        return select
    
    def copy(self) -> Self:
        return self.__class__(view=self.view, value=self.value, color=self.color)

    @final
    def can_play(self) -> bool:
        if self.view.stacked > 0:
            if isinstance(self, Draw2Card) or isinstance(self, Draw4Card):
                return True
            # if isinstance(self, Draw4Card):
            #     return True
            # elif isinstance(self, Draw2Card):
            #     return self._check_value()
            return False
        
        return self._can_play()

    @final
    def on_play(self, player: discord.User | discord.Member) -> None:
        self._on_play(player=player)
        return self._play(player=player)

    def __str__(self) -> str:
        assert self.color is not None
        return f'{self.value} {self.color.name}'.title()


class NumberCard(Card):
    def __str__(self) -> str:
        assert self.color is not None
        return f'{self.value} {self.color.name}'.title()


class ReverseCard(Card):
    def _on_play(self, player: discord.User | discord.Member) -> None:
        self.view.direction = Direction.anticlockwise if self.view.direction == Direction.clockwise else Direction.clockwise
        if len(self.view.players) == 2:
            self.view.turn_index = self.view.add_turn_index()
    
    def __str__(self) -> str:
        assert self.color is not None
        return f'Reverse {self.color.name}'.title()


class SkipCard(Card):
    def _on_play(self, player: discord.User | discord.Member) -> None:
        self.view.turn_index = self.view.add_turn_index()

    def __str__(self) -> str:
        assert self.color is not None
        return f'Skip {self.color.name}'.title()


class Draw2Card(Card):
    def _on_play(self, player: discord.User | discord.Member) -> None:
        amount = 2
        if not self.view.allow_stacking:
            self.view.turn_index = self.view.add_turn_index()
            self.view.draw_cards(player=self.view.players[self.view.turn_index], amount=amount)
        else:
            self.view.stacked += amount
    
    def __str__(self) -> str:
        assert self.color is not None
        return f'+2 {self.color.name}'.title()


class Draw4Card(Card):
    def _can_play(self) -> bool:
        return True

    def _on_play(self, player: discord.User | discord.Member) -> None:
        amount = 4
        if not self.view.allow_stacking:
            self.view.turn_index = self.view.add_turn_index()
            self.view.draw_cards(player=self.view.players[self.view.turn_index], amount=amount)
        else:
            self.view.stacked += amount
    
    def color_select(self, player: discord.User | discord.Member) -> ColorSelect:
        return self._color_select(player=player)
    
    def __str__(self) -> str:
        return f'+4 Wild'


class WildCard(Card):
    def _can_play(self) -> bool:
        return True

    def color_select(self, player: discord.User | discord.Member) -> ColorSelect:
        return self._color_select(player=player)
    
    def __str__(self) -> str:
        return f'Wild Card'
