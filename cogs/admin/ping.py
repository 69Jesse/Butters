import discord
from discord.ext import commands

from utils import (
    Context,
    Emoji,
    Embed,
)

import random
import time

from typing import (
    Optional,
)

import logging


log = logging.getLogger(__name__)


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def embed_from_n(
        self,
        n: int,
        ws_latency: list[float],
        ping_readings: list[float],
        order: list[int],
    ) -> Embed:
        readings: list[str] = []
        for o in order:
            ball_pos = o-n
            if ball_pos >= 0:
                readings.append(
                    '> ' + Emoji(f'paddle_left') + Emoji('🥵') + ''.join(Emoji(None) for _ in range((ball_pos+1)*1)) + Emoji(f'ball')
                )
            else:
                readings.append(
                    '> ' + Emoji(None) + Emoji('🥱') + Emoji('paddle_right') + Emoji(None) + f' {ping_readings[o]:.2f}ms'
                )
        info = '\n'.join(readings)
        title = {
            0: 'Pong',
            1: 'Ping',
        }[n%2]
        avg = sum(ping_readings)/len(ping_readings) if len(ping_readings) > 0 else None
        ping = f'{avg:.2f}ms (± {max(abs(avg-p) for p in ping_readings):.2f}ms)' if avg is not None else '-'
        return Embed(
            title=f'**{title}**',
            description=f'''
Calculating round-trip time...

{info}

**Average Ping:** {ping}
**Websocket Latency:** {sum(ws_latency)/len(ws_latency):.2f}ms
''',
        )

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx: Context) -> None:
        readings = 5
        ws_latency: list[float] = []
        ping_readings: list[float] = []
        order: list[int] = random.sample(range(readings), k=readings)

        message: Optional[discord.Message] = None
        for n in range(readings+1):
            ws_latency.append(self.bot.latency*1000)
            start = time.perf_counter()
            embed = self.embed_from_n(n, ws_latency=ws_latency, ping_readings=ping_readings, order=order)
            if message is None:
                message = await ctx.send(embed=embed)
            else:
                await message.edit(embed=embed)
            end = time.perf_counter()
            ping_readings.append((end - start)*1000)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
