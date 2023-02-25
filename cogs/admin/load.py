from discord.ext import commands
from bot import Butters
from utils import (
    Context,
    Embed,
)

from typing import (
    Optional,
)

import logging


log = logging.getLogger(__name__)


class Reload(commands.Cog):
    def __init__(self, bot: Butters) -> None:
        self.bot = bot

    @commands.command(name='reload', aliases=['load'])
    @commands.is_owner()
    async def reload(self, ctx: Context, *, name: Optional[str] = None) -> None:
        try:
            if name is None:
                title = await self.bot.setup_cogs()
            else:
                await self.bot.load_cog(name)
                title = f'Successfully (re)loaded {name}.'
        except Exception as e:
            title = f'{e.__class__.__name__}: {e}'
            log.exception(e)
        await ctx.send(embed=Embed(title=title))

    @commands.command(name='unload')
    @commands.is_owner()
    async def unload(self, ctx: Context, *, name: str) -> None:
        try:
            await self.bot.unload_cog(name)
            title = f'Successfully unloaded {name}.'
        except Exception as e:
            title = f'{e.__class__.__name__}: {e}'
        await ctx.send(embed=Embed(title=title))


async def setup(bot: Butters) -> None:
    await bot.add_cog(Reload(bot))
