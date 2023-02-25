import discord
import datetime

from typing import (
    Optional,
    Union,
    Any,
)


__all__ = (
    'Embed',
)


class Embed(discord.Embed):
    def __init__(
        self,
        *args,
        color: Optional[Union[int, discord.Color]] = None,
        title: Optional[Any] = None,
        url: Optional[Any] = None,
        description: Optional[Any] = None,
        timestamp: Optional[datetime.datetime] = None,
    ) -> None:
        assert len(args) <= 1, 'Embed takes at most 1 positional argument (description)'
        description = args[0] if len(args) > 0 else description
        if isinstance(title, str):
            if not title.startswith('**') and not title.endswith('**'):
                title = f'**{title}**'
        color = color or 0x2B2D31
        super().__init__(
            title=title,
            description=description,
            color=color,
            url=url,
            timestamp=timestamp,
        )
