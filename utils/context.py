"""Mostly stolen from Danny"""
import discord
from discord.ext import commands

import io

from typing import (
    Optional,
    TypeVar,
    Generic,
    Union,
    Any,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from bot import Butters


__all__ = (
    'Context',
)


BotT = TypeVar('BotT', bound='Butters')


class Context(commands.Context, Generic[BotT]):
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread, discord.DMChannel]
    prefix: str
    command: commands.Command[Any, ..., Any]
    bot: BotT
    def __init__(self, **attrs: Any) -> None:
        self.error_handled: bool = False
        super().__init__(**attrs)

    async def show_help(self, command: Optional[str] = None) -> None:
        cmd = self.bot.get_command('help')
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)  # type: ignore

    @discord.utils.cached_property
    def replied_message(self) -> Optional[discord.Message]:
        ref = self.message.reference
        if ref is not None and isinstance(ref.resolved, discord.Message):
            return ref.resolved
        return None

    async def safe_send(self, content: str, **kwargs) -> discord.Message:
        if len(content) > 2000:
            fp = io.BytesIO(content.encode())
            kwargs.pop('file', None)
            return await self.send(file=discord.File(fp, filename='message_too_long.txt'), **kwargs)
        else:
            return await self.send(content)
