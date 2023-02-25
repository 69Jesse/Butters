import discord
from discord.ext import commands
from bot import Butters
from utils import (
    Context,
    valid,
)

from .views import (
    UnoView,
)

import logging

from typing import (
    Optional,
)


log = logging.getLogger(__name__)

min_starting_cards = 4
max_starting_cards = 10
default_starting_cards = 7


class Uno(commands.Cog):
    def __init__(self, bot: Butters) -> None:
        self.bot = bot

    @commands.hybrid_command(name='uno', description=f'I don\'t speak Spanish.', aliases=[])
    @discord.app_commands.describe(
        starting_cards = f'Change the amount of cards you start with, default is {default_starting_cards}.',
        allow_stacking = f'Allow stacking of draw cards (+2, +4), default is True.',
        end_special_card = f'Whether people can end the game with a special card, if False, they will draw 1, default is False.',
    )
    @discord.app_commands.choices(
        starting_cards = [
            discord.app_commands.Choice(name=str(num) if num != default_starting_cards else f'{num} (Default)', value=str(num)) for num in range(min_starting_cards, max_starting_cards+1)
        ],
        allow_stacking = [
            discord.app_commands.Choice(name='True (Default)', value='1'),
            discord.app_commands.Choice(name='False', value='0'),
        ],
        end_special_card = [
            discord.app_commands.Choice(name='True', value='1'),
            discord.app_commands.Choice(name='False (Default)', value='0'),
        ]
    )
    async def uno(
        self,
        ctx: Context[Butters],
        starting_cards: Optional[str] = None,
        allow_stacking: Optional[str] = None,
        end_special_card: Optional[str] = None,
    ) -> None:
        starting_cards = starting_cards or str(default_starting_cards)
        allow_stacking = allow_stacking or '1'
        end_special_card = end_special_card or '0'

        view = UnoView(
            bot=self.bot,
            ctx=ctx,
            starting_cards=valid(int, starting_cards, contains=range(min_starting_cards, max_starting_cards+1), name='starting_cards'),
            allow_stacking=valid(bool, allow_stacking, name='allow_stacking'),
            end_special_card=valid(bool, end_special_card, name='end_special_card'),
        )
        await view.send_initial_message()


async def setup(bot: Butters) -> None:
    await bot.add_cog(Uno(bot))
