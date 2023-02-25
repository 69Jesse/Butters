import discord
from main import Butters
from utils import (
    Context,
    Embed,
    Emoji,
    View,
)

from io import BytesIO
from enum import Enum
import random

from .game import Game
from .other import (
    STANDARD_LEVEL_LINES,
    Direction,
)

from typing import (
    Optional,
    Any,
)
from typing_extensions import (
    Self,
)


class Stage(Enum):
    start = 0
    playing = 1
    completed = 2
    retry = 3
    lost = 4
    won = 5


class RobbieView(View):
    def __init__(self, bot: Butters, ctx: Context) -> None:
        super().__init__(bot=bot, ctx=ctx, timeout=180.0)
        self.game = Game(lines=STANDARD_LEVEL_LINES)
        self.stage = Stage.start
        self.update_components()

    def update_components(self) -> None:
        self.clear_items()
        components: list[list[discord.ui.Item[Self]]] = []
        match self.stage:
            case Stage.start:
                components.append([
                    discord.ui.Button(label='Start Game', style=discord.ButtonStyle.red, custom_id='start'),
                    discord.ui.Button(emoji=Emoji('👈'), style=discord.ButtonStyle.blurple, custom_id='left'),
                    discord.ui.Button(emoji=Emoji('👉'), style=discord.ButtonStyle.blurple, custom_id='right'),
                    discord.ui.Button(label='Edit Level', style=discord.ButtonStyle.green, custom_id='edit', disabled=True),
                    discord.ui.Button(emoji=Emoji('🎲'), style=discord.ButtonStyle.blurple, custom_id='shuffle'),
                ])
            case Stage.playing:
                components.extend([
                    [
                        discord.ui.Button(emoji=Emoji('⬅️'), style=discord.ButtonStyle.gray, custom_id='max_left'),
                        discord.ui.Button(emoji=Emoji('👆'), style=discord.ButtonStyle.blurple, custom_id='up'),
                        discord.ui.Button(emoji=Emoji('⬆️'), style=discord.ButtonStyle.gray, custom_id='max_up'),
                    ],
                    [
                        discord.ui.Button(emoji=Emoji('👈'), style=discord.ButtonStyle.blurple, custom_id='left'),
                        discord.ui.Button(emoji=Emoji('🔃'), style=discord.ButtonStyle.red, custom_id='retry'),
                        discord.ui.Button(emoji=Emoji('👉'), style=discord.ButtonStyle.blurple, custom_id='right'),
                    ],
                    [
                        discord.ui.Button(emoji=Emoji('⬇️'), style=discord.ButtonStyle.gray, custom_id='max_down'),
                        discord.ui.Button(emoji=Emoji('👇'), style=discord.ButtonStyle.blurple, custom_id='down'),
                        discord.ui.Button(emoji=Emoji('➡️'), style=discord.ButtonStyle.gray, custom_id='max_right'),
                    ],
                ])
            case Stage.completed:
                components.append([
                    discord.ui.Button(label='Next Level', style=discord.ButtonStyle.green, custom_id='next'),
                ])
            case Stage.retry | Stage.lost:
                components.append([])
                if self.stage == Stage.retry:
                    if not self.game.level.failed:
                        components[0].append(
                            discord.ui.Button(label='Back', style=discord.ButtonStyle.blurple, custom_id='back')
                        )
                    components[0].append(
                        discord.ui.Button(label='Retry Level', style=discord.ButtonStyle.green, custom_id='retry_level')
                    )
                components[0].append(
                    discord.ui.Button(label='Retry Whole Game', style=discord.ButtonStyle.red, custom_id='retry_game'),
                )

        for i, row in enumerate(components):
            for component in row:
                component.row = i
                component.callback = self.callback
                self.add_item(component)

    def time(self, epoch: Optional[float]) -> str:
        return f'<t:{int(epoch)}:R>' if epoch else '**-**'

    @property
    def embed(self) -> Embed:
        embed = Embed(title='Robbie Speurhondenspel')
        description: str = ''
        match self.stage:
            case Stage.start:
                description = f'Level selected: **{self.game.level_index + 1} / {len(self.game.levels)}**'
            case _:
                description = (
                    f'Levels completed: **{sum(level.completed for level in self.game.levels)} / {len(self.game.levels)}**'
                    f'\nMoves: **{self.game.total_moves}**, first one {self.time(self.game.started)}'
                    f'\nMoves this level: **{self.game.level.moves}**, {self.time(self.game.level.started)}'
                    f'\nScore: **{self.game.score}**, Tries left: **{self.game.tries_left}**'
                )
        embed.description = description
        return embed

    def embed_and_file(self, as_attachments: bool = False) -> dict[str, Any]:
        image = self.game.level.image()
        buffer = BytesIO()
        image.save(buffer, format='png')
        buffer.seek(0)
        embed = self.embed
        embed.set_image(url='attachment://level.png')
        file = discord.File(buffer, filename='level.png')
        if as_attachments:
            return {'embed': embed, 'attachments': [file]}
        else:
            return {'embed': embed, 'file': file}

    async def callback(self, interaction: discord.Interaction) -> None:
        assert interaction.data is not None
        custom_id = interaction.data.get('custom_id')
        update_embed: bool = True
        match self.stage:
            case Stage.start:
                match custom_id:
                    case 'start':
                        self.stage = Stage.playing
                    case 'left' | 'right':
                        self.game.next_level(n=1 if custom_id == 'right' else -1)
                    case 'edit':
                        raise
                    case 'shuffle':
                        random.shuffle(self.game.levels)
            case Stage.playing:
                match custom_id:
                    case 'up' | 'down' | 'left' | 'right' | 'max_up' | 'max_down' | 'max_left' | 'max_right':
                        direction = Direction[custom_id.replace('max_', '')]
                        if custom_id.startswith('max_'):
                            while self.game.level.move(direction):
                                pass
                        else:
                            self.game.level.move(direction)
                        if self.game.level.completed:
                            if self.game.completed:
                                self.stage = Stage.won
                            else:
                                self.stage = Stage.completed
                        elif self.game.level.failed:
                            self.stage = Stage.retry
                            if self.game.tries_left == 0:
                                self.stage = Stage.lost
                    case 'retry':
                        self.stage = Stage.retry
                        update_embed = False
            case Stage.completed:
                match custom_id:
                    case 'next':
                        self.game.next_level()
                        self.stage = Stage.playing
            case Stage.retry:
                match custom_id:
                    case 'back':
                        assert not self.game.level.failed
                        self.stage = Stage.playing
                        update_embed = False
                    case 'retry_level':
                        self.game.level.retry()
                        self.stage = Stage.playing
                    case 'retry_game':
                        self.game.reset()
                        self.stage = Stage.playing
            case Stage.lost:
                match custom_id:
                    case 'retry_game':
                        self.game.reset()
                        self.stage = Stage.playing

        self.update_components()
        params: dict[str, Any] = {'view': self}
        if update_embed:
            params.update(self.embed_and_file(as_attachments=True))
        await interaction.response.edit_message(**params)
