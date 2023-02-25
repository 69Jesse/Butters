import discord
from discord.ext import commands

from db import Database
from utils import (
    ValueNotAllowed,
    Context,
    Config,
    Embed,
)

from pathlib import Path
import aiohttp
import time
import sys

from typing import (
    Optional,
    Literal,
)
from typing_extensions import (
    Self,
)

import logging


log = logging.getLogger(__name__)


class Butters(commands.Bot):
    user: discord.User
    def __init__(self) -> None:
        super().__init__(
            command_prefix=self.prefix,
            activity=discord.Activity(type=discord.ActivityType.competing, name='Monopoly'),
            # status=discord.Status.offline,
            help_command=None,
            strip_after_prefix=True,
            intents=discord.Intents.all(),
            owner_ids={
                476083615000821771,
            },
            case_insensitive=True,
        )

    async def prefix(self, bot: Self, message: discord.Message) -> list[str]:
        """Returns a list of prefixes that can be used to invoke a command with text."""
        base: list[str] = [f'<@{self.user.id}>', f'<@!{self.user.id}>']
        base.extend(['b!', 'B!'])
        if 'linux' in sys.platform:
            return base
        base.append('')
        return base

    @property
    def cogs_by_path(self) -> dict[str, commands.Cog]:
        if not hasattr(self, '_cogs_by_path'):
            self._cogs_by_path: dict[str, commands.Cog] = {}
        return self._cogs_by_path

    async def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        await super().load_extension(name, package=package)
        cog = list(self.cogs.values())[-1]
        assert cog is not None
        self.cogs_by_path[name] = cog

    async def reload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        await super().reload_extension(name, package=package)
        cog = list(self.cogs.values())[-1]
        assert cog is not None
        self.cogs_by_path[name] = cog

    async def unload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        await super().unload_extension(name, package=package)
        self.cogs_by_path.pop(name)

    async def load_cog(self, name: str) -> None:
        """(Re)loads a cog. Raises `commands.ExtensionNotFound`, `commands.NoEntroPointError` or `commands.ExtensionsFailed` respectively."""
        try:
            await self.load_extension(name)
        except commands.ExtensionAlreadyLoaded:
            await self.reload_extension(name)

    async def unload_cog(self, name: str) -> None:
        """Unloads a cog. Raises `commands.ExtensionNotFound` or `commands.ExtensionNotLoaded` respectively."""
        await self.unload_extension(name)

    async def setup_cogs(self) -> str:
        files = [
            *(
                file for folder in (
                    'admin',
                    'games',
                    'other',
                ) for file in map(str, (f if not f.is_dir() else f / 'main.py' for f in Path(f'cogs/{folder}').iterdir()))
                if file.endswith('.py')
                and '_' not in file
            ),
            'jishaku',
        ]

        for file in files:
            name = file.removesuffix('.py').replace('\\', '.').replace('/', '.')
            await self.load_cog(name)

        content = f'Successfully (re)loaded {len(self.cogs)} cogs.'
        log.info(content)
        return content

    async def create_db_pool(self) -> None:
        async with Database() as db:
            self.db = db

    async def setup_hook(self) -> None:
        await self.create_db_pool()
        self.session = aiohttp.ClientSession()
        await self.setup_cogs()

        self.app_info = await self.application_info()
        self.blacklist: Config[Literal[True]] = Config('blacklist.json')
        self.prefixes: Config[list[str]] = Config('prefixes.json')

        log.info(f'Logged in as {repr(str(self.user))}, version {discord.__version__}')

    async def add_to_blacklist(self, object_id: int) -> None:
        await self.blacklist.put(object_id, True)

    async def remove_from_blacklist(self, object_id: int) -> None:
        await self.blacklist.remove(object_id)

    @property
    def owner(self) -> discord.User:
        return self.app_info.owner

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is None:
            return
        elif message.author.id in self.blacklist:
            return
        elif message.guild is not None and message.guild.id in self.blacklist:
            return

        await self.invoke(ctx)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author != self.owner or time.time() - before.created_at.timestamp() > 30:
            return
        await self.process_commands(message=after)

    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        if ctx.error_handled:
            return
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueNotAllowed):
            """Parameter value not allowed."""
            await ctx.send(embed=Embed(str(error.original)))
            return
        elif ctx.author == self.owner:
            raise error
        else:
            if isinstance(error, (
                commands.NotOwner,
                commands.CheckFailure,
            )):
                return
            elif isinstance(error, commands.CommandNotFound):
                alias = ctx.invoked_with
                print(alias)
                return
            await ctx.send('An error occured.. Oh no!')

        raise error
