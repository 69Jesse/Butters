import discord

from utils.emoji import (
    Emoji,
    emoji_width,
)
from utils.embed import (
    Embed,
)
from utils.view import (
    View,
)
from typing import (
    TYPE_CHECKING,
    ParamSpec,
    Awaitable,
    Optional,
    Callable,
    Any,
)
if TYPE_CHECKING:
    from bot import Butters


__all__ = (
    'MultiplayerGame',
    'rig',
    '_Player',
)


I = ParamSpec('I')  # Any args or kwargs but one of these must be `discord.Interaction`.
AsyncWithInteraction = Callable[I, Awaitable[bool]]


def rig(check: AsyncWithInteraction) -> AsyncWithInteraction:
    def is_owner(*args: I.args, **kwargs: I.kwargs) -> bool:
        interaction: discord.Interaction = next(value for value in (*args, *kwargs.values()) if isinstance(value, discord.Interaction))
        if TYPE_CHECKING:
            assert isinstance(interaction.client, 'Butters')
        if interaction.user == interaction.client.owner:
            return True
        return False

    async def wrapper(*args: I.args, **kwargs: I.kwargs) -> bool:
        if is_owner(*args, **kwargs):
            return True
        return await check(*args, **kwargs)

    return wrapper


class MultiplayerSetup:
    def __init__(self, *, view: 'View', max_players: int, min_players: Optional[int], name: Optional[str], title: Optional[str], bot_allowed: bool) -> None:
        min_players = min_players or 2
        assert any(isinstance(v, str) for v in (name, title))
        assert min_players <= max_players
        self.view = view
        self.max_players = max_players
        self.min_players = min_players
        self.name = name or title
        self.title = title or name
        assert isinstance(self.name, str) and isinstance(self.title, str), 'name or title must be `str`'
        self.bot_allowed = bot_allowed

        self.me = view.bot.user
        self.players: list[discord.User | discord.Member] = [self.view.ctx.author]
        self.required_player_count = self.min_players
        self.ready: list[discord.User | discord.Member] = []
        self.kick_enabled = False
        self.kick_index = 1
        self.banned: list[discord.User | discord.Member] = []
        self.enable_menu()
        self.update_components()

    async def send(self) -> discord.Message:
        return await self.view.ctx.send(embed=self.embed, view=self.view)

    def enable_menu(self) -> None:
        self.methods_enabled: tuple[str, ...] = (
            'interaction_check',
            'on_timeout',
        )

        for attr in self.methods_enabled:
            setattr(self, f'main_{attr}', getattr(self.view, attr, None))
            setattr(self.view, attr, getattr(self, attr))

    def disable_menu(self) -> None:
        for attr in self.methods_enabled:
            setattr(self.view, attr, getattr(self, f'main_{attr}'))

    def empty_button(self, label: str = ' ', emoji: Optional[str] = None, custom_id: Optional[str] = None, style: discord.ButtonStyle = discord.ButtonStyle.grey, disabled: bool = True) -> discord.ui.Button:
        return discord.ui.Button(label=label, emoji=emoji, custom_id=custom_id, style=style, disabled=disabled)

    def update_components(self) -> None:
        self.view.clear_items()

        buttons = [
            [
                discord.ui.Button(label='Join Game', emoji=None, custom_id='join', style=discord.ButtonStyle.red, disabled=False),
                discord.ui.Button(label='Ready Up', emoji=None, custom_id='ready', style=discord.ButtonStyle.green, disabled=False),
            ],
            [
                discord.ui.Button(label=None, emoji=Emoji('⏫'), custom_id='players_up', style=discord.ButtonStyle.blurple, disabled=self.required_player_count >= self.max_players),
                (discord.ui.Button(label=None, emoji=Emoji('⏬'), custom_id='players_down', style=discord.ButtonStyle.blurple, disabled=self.required_player_count <= 2)
                if not self.bot_allowed_now() else
                discord.ui.Button(label='AI', emoji=None, custom_id='me', style=discord.ButtonStyle.blurple, disabled=False)),
                discord.ui.Button(label=None, emoji=Emoji('👞'), custom_id='kick_mode', style=discord.ButtonStyle.green, disabled=False),
            ],
        ]

        if self.kick_enabled:
            kick_ban_disabled = (not 0 < self.kick_index < len(self.players) or self.players[self.kick_index] == self.me)
            buttons.append([
                discord.ui.Button(label='Kick', emoji=None, custom_id='kick', style=discord.ButtonStyle.red, disabled=kick_ban_disabled),
                discord.ui.Button(label='Ban', emoji=None, custom_id='ban', style=discord.ButtonStyle.red, disabled=kick_ban_disabled),
                discord.ui.Button(label=None, emoji=Emoji(self.kick_index+1), custom_id='kick_mode_index', style=discord.ButtonStyle.blurple, disabled=False),
            ])
            if self.required_player_count > 2:
                buttons[-2].append(discord.ui.Button(label=None, emoji=Emoji('👆'), custom_id='kick_mode_up', style=discord.ButtonStyle.green, disabled=self.required_player_count <= 2))
                buttons[-1].append(discord.ui.Button(label=None, emoji=Emoji('👇'), custom_id='kick_mode_down', style=discord.ButtonStyle.green, disabled=self.required_player_count <= 2))

        for i, row in enumerate(buttons):
            for button in row:
                button.row = i
                button.callback = self.callback
                self.view.add_item(button)

    def players_visualized(self) -> str:
        lines: list[str] = []

        for i in range(self.required_player_count):
            line = '> '
            if self.kick_enabled and self.kick_index == i:
                line += f'{Emoji("👞")} '
            line += f'Player **#{i+1}**: '
            if i < len(self.players):
                player = self.players[i]
                line += f'{player.mention} '
                if player in self.ready:
                    line += '**READY!!!**'
                else:
                    line += 'Not ready yet.'
            else:
                line += '-'
            lines.append(line)

        return '\n'.join(lines)

    def append_player(self, player: discord.User | discord.Member) -> None:
        self.players.append(player)

    def remove_player(self, player: discord.User | discord.Member) -> None:
        self.players.remove(player)
        if player in self.ready:
            self.ready.remove(player)

    @property
    def embed(self) -> discord.Embed:
        return Embed(
            title=f'**{self.title}**',
            description=(
                f'{self.view.ctx.author.mention} would like to play **{self.name}**!\n\n'
                'Click on the huge **Join Game** button to play with them!     \n\n'
                f'**Players:** ({len(self.players)}/{self.required_player_count})\n'
                f'{self.players_visualized()}\n\n'
                'When ready, don\'t forget to **Ready Up**!'
            ),
        )

    def check_ready(self, interaction: discord.Interaction) -> bool:
        """Checks if the game is ready to start"""
        assert interaction.data is not None
        custom_id = interaction.data.get('custom_id')
        if len(self.players) >= 2 and len(self.players) == self.required_player_count and all([player in self.ready for player in self.players]):
            return True
        elif len(self.players) == 1 and interaction.user == self.view.bot.owner and interaction.user in self.ready and custom_id == 'kick_mode_index':
            """Debug for owner"""
            self.players.append(interaction.user)
            return True
        return False

    def bot_allowed_now(self) -> bool:
        return (
            self.bot_allowed and
            self.required_player_count == 2 and
            (len(self.players) == 1 or self.me in self.players)
        )

    async def start_game(self, interaction: discord.Interaction) -> None:
        self.disable_menu()
        self.view.clear_items()
        assert isinstance(self.view, MultiplayerGame)
        return await self.view.on_game_start(interaction=interaction, players=self.players)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert interaction.data is not None
        custom_id = interaction.data.get('custom_id')

        match custom_id:
            case 'join' | 'ready':
                player = interaction.user
                if player in self.players:
                    if custom_id == 'join':
                        if player == self.view.ctx.author:
                            return await interaction.response.send_message(embed=Embed(f'You started this game, don\'t leave me!'), ephemeral=True)
                        elif player in self.ready:
                            return await interaction.response.send_message(embed=Embed(f'You cannot leave while ready!'), ephemeral=True)
                        self.remove_player(player=player)
                else:
                    if len(self.players) >= self.required_player_count:
                        return await interaction.response.send_message(embed=Embed(f'This game is full!'), ephemeral=True)
                    self.append_player(player=player)
                if custom_id == 'ready':
                    if player in self.ready:
                        self.ready.remove(player)
                    else:
                        self.ready.append(player)

            case 'players_up' | 'players_down':
                if custom_id == 'players_up':
                    self.required_player_count = min(self.max_players, self.required_player_count+1)
                elif custom_id == 'players_down':
                    self.required_player_count = max(self.min_players, self.required_player_count-1)
                self.players = self.players[:self.required_player_count]
                self.kick_index = min(self.kick_index, self.required_player_count-1)

            case 'kick_mode':
                self.kick_enabled = not self.kick_enabled

            case 'kick_mode_index':
                self.kick_index = 1

            case 'kick_mode_up' | 'kick_mode_down':
                add = {
                    'kick_mode_up': -1,
                    'kick_mode_down': 1,
                }[custom_id]
                self.kick_index = (self.kick_index+add-1) % (self.required_player_count-1) + 1

            case 'kick' | 'ban':
                if self.kick_index < len(self.players):
                    player = self.players[self.kick_index]
                    if player == self.view.ctx.author:
                        return
                    self.remove_player(player=player)
                    if custom_id == 'ban':
                        self.banned.append(player)

            case 'me':
                if self.bot_allowed_now():
                    if self.me not in self.players:
                        self.players.append(self.me)
                        self.ready.append(self.me)
                    else:
                        self.remove_player(player=self.me)

        if self.me in self.players and not self.bot_allowed_now():
            self.remove_player(player=self.me)

        if self.check_ready(interaction=interaction):
            return await self.start_game(interaction=interaction)

        self.update_components()
        return await interaction.response.edit_message(embed=self.embed, view=self.view)

    @rig
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user in self.banned:
            await interaction.response.send_message(embed=Embed(f'The host {self.view.ctx.author.mention} banned you from playing with them this time..'), ephemeral=True)
            return False

        assert interaction.data is not None
        custom_id = interaction.data.get('custom_id')

        if custom_id in ('join', 'ready'):
            return True
        elif interaction.user == self.view.ctx.author:
            return True
        else:
            await interaction.response.send_message(embed=Embed(f'Only our host {self.view.ctx.author.mention} can use this component.'), ephemeral=True)
            return False

    async def on_timeout(self) -> None:
        self.view.stop()
        for button in self.view.children:
            assert isinstance(button, discord.ui.Button)
            button.disabled = True

        await self.view.message.edit(
            embed=Embed(
                title=f'**{self.title}**',
                description=(
                    f'{self.view.ctx.author.mention} would have liked to play **{self.name}**!\n\n'
                    'But this message unfortunately has timed out...\n'
                    'You can always run my command again though!'
                ),
            ),
            view=self.view,
        )


class MultiplayerGame:
    _setup_kwargs: dict[str, Any]
    _setup: MultiplayerSetup
    _View: type[View]
    def __init_subclass__(
        cls,
        max_players: int,
        min_players: Optional[int] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        bot_allowed: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for base in cls.__bases__:
            if issubclass(base, View):
                cls._View = base
                break
        else:
            raise TypeError('MultiplayerGame must be a subclass of View!')
        assert any(isinstance(v, str) for v in (name, title)), 'You must provide a name and/or title for your game!'
        assert min_players is None or min_players <= max_players
        cls._setup_kwargs = {
            'max_players': max_players,
            'min_players': min_players,
            'name': name,
            'title': title,
            'bot_allowed': bot_allowed,
        }
        cls._View.__init_subclass__(*args, **kwargs)

    def __init__(self, *args, **kwargs) -> None:
        assert isinstance(self, View)
        self._View.__init__(self, *args, **kwargs)
        self._setup = MultiplayerSetup(view=self, **self._setup_kwargs)

    async def send_initial_message(self) -> None:
        self.message = await self._setup.send()

    async def on_game_start(self, interaction: discord.Interaction, players: list[discord.User | discord.Member]) -> None:
        """Coroutine that is called when the game starts."""
        await interaction.response.edit_message(embed=Embed('Game start not implemented.'))


class _Player(discord.user._UserTag):
    """
    A class that represents a player in a multiplayer game.
    
    This class is a subclass of discord.user._UserTag,
    so that discord.User == Player can return True.

    Meant to be subclassed and used with MultiplayerGame.
    """
    def __init__(self, member: discord.User | discord.Member) -> None:
        self.member = member

    def __getattr__(self, name: str) -> Any:
        """__getattr__ gets called when an attribute is not found in the class."""
        return getattr(self.member, name)

    def __eq__(self, other: Any) -> bool:
        return self.member == other

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return str(self.member)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.member!r})'
