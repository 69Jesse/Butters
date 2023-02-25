from discord.ext import commands
from bot import Butters
from utils import (
    Context,
)

from .view import RobbieView

import logging


log = logging.getLogger(__name__)


class Robbie(commands.Cog):
    def __init__(self, bot: Butters):
        self.bot = bot

    @commands.hybrid_command(name='robbie', description='nostalgie')
    async def robbie(
        self,
        ctx: Context[Butters],
        thomas: bool = True,
    ) -> None:
        view = RobbieView(bot=self.bot, ctx=ctx)
        view.game.thomas = thomas  # type: ignore
        await ctx.send(view=view, **view.embed_and_file())


async def setup(bot: Butters) -> None:
    await bot.add_cog(Robbie(bot))
