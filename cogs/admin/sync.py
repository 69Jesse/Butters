from discord.ext import commands
from bot import Butters

from utils import (
    Context,
    Embed,
)

import logging


log = logging.getLogger(__name__)


class Sync(commands.Cog):
    def __init__(self, bot: Butters) -> None:
        self.bot = bot

    @commands.command(name='sync', description='Syncronizes my application commands.', aliases=[])
    @commands.is_owner()
    async def sync(self, ctx: Context) -> None:
        message = await ctx.send(embed=Embed(title='Syncing...', description='This could take some time.'))

        await self.bot.tree.sync()

        names: dict[str, int] = {}
        application_commands = self.bot.tree.get_commands()
        for command in application_commands:
            name = command.__class__.__name__
            names[name] = names.get(name, 0) + 1

        title = f'Successfully synced {len(application_commands)} application command{"s"*(len(application_commands) != 1)}.'
        log.info(title)

        description = '\n'.join(f'{value}x {key}' for key, value in names.items())
        await message.edit(embed=Embed(title=title, description=description))


async def setup(bot: Butters) -> None:
    await bot.add_cog(Sync(bot))
