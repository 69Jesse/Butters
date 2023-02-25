import discord
from bot import Butters
from utils import (
    View,
    MultiplayerGame,
    Context,
    Embed,
    Emoji,
    rig,
)
from .cards import (
    Card,
    NumberCard,
    ReverseCard,
    SkipCard,
    Draw2Card,
    Draw4Card,
    WildCard,
)
from .selects import (
    ColorSelect,
    CardSelect,
)
from .other import (
    Color,
    Direction,
    UnoTracker,
)

import random
import time
import os

from typing import (
    Optional,
)
from typing_extensions import (
    Self,
)


filler: str = ' '


class UnoView(MultiplayerGame, View, max_players=8, min_players=2, name='Uno', title='Uno'):
    color_to_emoji: dict[Optional[Color], str] = {
        Color.red: Emoji('🟥'),
        Color.blue: Emoji('🟦'),
        Color.yellow: Emoji('🟨'),
        Color.green: Emoji('🟩'),
        None: Emoji('🟪'),
    }
    color_to_name: dict[Optional[Color], str] = {
        Color.red: 'red',
        Color.blue: 'blue',
        Color.yellow: 'yellow',
        Color.green: 'green',
        None: 'purple',
    }
    def __init__(self, ctx: Context, bot: Butters, starting_cards: int, allow_stacking: bool, end_special_card: bool) -> None:
        super().__init__(bot=bot, ctx=ctx, timeout=300.0)
        self.starting_cards = starting_cards
        self.allow_stacking = allow_stacking
        self.end_special_card = end_special_card

        self.subviews: list[View] = []
        self.id_to_card: dict[str, Card] = {}

    async def on_game_start(self, interaction: discord.Interaction, players: list[discord.User | discord.Member]) -> None:
        self.players = random.sample(players, k=len(players))
        self.turn_index = 0
        self.deck: list[Card] = [
            *[
                NumberCard(view=self, value=value, color=color) for color in Color for value in list(range(0, 9+1))+list(range(1, 9+1))
            ],
            *[
                card for _ in range(2) for color in Color for card in [
                    SkipCard(view=self, value=None, color=color),
                    ReverseCard(view=self, value=None, color=color),
                    Draw2Card(view=self, value=None, color=color),
                ]
            ],
            *[
                card for _ in range(4) for card in [
                    WildCard(view=self, value=None, color=None),
                    Draw4Card(view=self, value=None, color=None),
                ]
            ]
        ]
        random.shuffle(self.deck)

        self.emojis: dict[discord.User | discord.Member, str] = {player: emoji for player, emoji in zip(self.players, random.sample([
            Emoji('🔴'),
            Emoji('🟠'),
            Emoji('🟡'),
            Emoji('🟢'),
            Emoji('🔵'),
            Emoji('🟣'),
            Emoji('🟤'),
            Emoji('⚪'),
        ], k=len(self.players)))}

        starting_card = random.choice([card for card in self.deck if isinstance(card.value, int)])
        self.used: list[Card] = [starting_card]
        self.deck.remove(starting_card)
        self.current_color: Optional[Color] = starting_card.color
        assert self.current_color is not None
        self.stacked = 0
        self.direction = Direction.clockwise
        self.uno_tracker = UnoTracker(view=self)
        self.hands: dict[discord.User | discord.Member, list[Card]] = {player: [] for player in self.players}
        for player in self.players:
            self.draw_cards(player=player, amount=self.starting_cards)
        assert all(len(self.hands[player]) > 1 for player in self.players)

        self.started = int(time.time())
        self.last_move: Optional[int] = None
        self.total_moves = 0
        self.cards_per_row: dict[discord.User | discord.Member, int] = {
            player: 5 for player in self.players
        }
        self.drawn_card: Optional[Card] = None
        self.winner: Optional[discord.User | discord.Member] = None

        self.update_components()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @property
    def top_card(self) -> Card:
        """Returns the top card of the deck."""
        return self.used[-1]

    def get_card_emojis(self, card: Card) -> list[list[str]]:
        """
        Returns a list (length 3) of lists (all length 2) of emojis that represent the card.
        
        Example: [[x, x], [x, x], [x, x]]
        """

        background_emoji = self.color_to_emoji[card.color]
        name = f'border_{self.color_to_name[card.color]}_'

        emojis = [[background_emoji for _ in range(2)] for _ in range(3)]

        if isinstance(card.value, int):
            emojis[0][0] = Emoji(f'{name}{card.value}')
            emojis[-1][-1] = Emoji(f'{name}{card.value}')
        elif isinstance(card, ReverseCard):
            emojis[1] = [Emoji(f'{name}arrows_clockwise') for _ in range(2)]
        elif isinstance(card, SkipCard):
            emojis[1] = [Emoji(f'{name}skip') for _ in range(2)]
        elif isinstance(card, Draw2Card) or isinstance(card, Draw4Card):
            emojis[1] = [Emoji(f'{name}plus'), Emoji(name+{Draw2Card: '2', Draw4Card: '4'}[type(card)])]
        elif isinstance(card, WildCard):
            emojis[0] = [Emoji('🟥'), Emoji('🟦')]
            emojis[-1] = [Emoji('🟨'), Emoji('🟩')]
        return emojis

    def top_card_str(self, expand: int | bool = False) -> str:
        """
        Returns a string representation of the top card.
        `expand` can be an integer or `False`,
        if not `False` it will get `expand` times as wide and high
        """
        card = self.top_card
        emojis = self.get_card_emojis(card=card)
        color = self.color_to_emoji[self.current_color]
        emojis[1].extend([Emoji(None), color])

        if expand is not False:
            emojis = [[emoji for emoji in row for _ in range(expand)] for row in emojis for _ in range(expand)]

        return '\n'.join(''.join(row) for row in emojis)

    def players_field(self) -> dict[str, str | bool]:
        """Looks very messy here, but looks good on Discord."""
        return {
            'name': 'Players '+(Emoji('👇') if self.direction == Direction.clockwise else Emoji('👆')),
            'value': '\n'.join(
                f'''{self.emojis[player]} Player **#{i+1}**: {player.mention} {
    (
        f'**{Emoji("⬅️")} TURN**' if i == self.turn_index else 'Up next!' if i == self.add_turn_index() else ''
    ) if not self.is_finished() else (
        f'**{Emoji("🏆")} WINNER**' if player == self.winner else ''
    )
}
Cards: **{len(self.hands[player])}** {
    f'**{Emoji("red_1")} UNO**' if player in self.uno_tracker else ''
}''' for i, player in enumerate(self.players)
            ) + f'\n{Emoji(None)}',
            'inline': False,
        }

    def stacked_str(self) -> str:
        return f'Stacked: **+{self.stacked}**\n' if self.stacked else ''

    @property
    def embed(self) -> Embed:
        embed = Embed(
            title = '**Uno**',
            description = f'''
{Emoji(None)}
{self.top_card_str(expand=2)}
{Emoji(None)}
''',
        )
        embed.add_field(**self.players_field())
        embed.add_field(
            name = 'Extra Info',
            value = f'''
Started <t:{self.started}:R>
Last move: {f'<t:{self.last_move}:R>' if self.last_move is not None else '-'}
{self.stacked_str()}Turn: **#{self.turn_index+1}** {self.turn.mention}
''',
        )
        return embed

    def sort_hand(self, player: discord.User | discord.Member) -> None:
        self.hands[player] = sorted(
            self.hands[player],
            key=lambda card: (
                not card.can_play(),
                card.color.value if card.color is not None else -1,
                card.value if card.value is not None else -1,
                card.__class__.__name__,
            ),
        )

    def draw_cards(self, player: discord.User | discord.Member, amount: int) -> Optional[Card]:
        """Returns the last card drawn (if any)"""
        card = None
        for _ in range(amount):
            # 25 card limit because of Discord limitations.
            # The chance of not being able to play a single
            # card with 25 cards is so low that this does not matter.
            if len(self.hands[player]) >= 25:
                break

            if not hasattr(self, 'deck_copy') or len(self.deck_copy) == 0:
                self.deck_copy = random.sample([card.copy() for card in self.deck], k=len(self.deck))
            card = self.deck_copy.pop()
            self.hands[player].append(card)

        self.sort_hand(player=player)
        return card

    @property
    def empty_button(self) -> discord.ui.Button:
        return discord.ui.Button(label=' ', disabled=True)

    def update_components(self) -> None:
        self.clear_items()

        components: list[list[discord.ui.Button[Self] | discord.ui.Select[Self]]] = [
            [
                discord.ui.Button(label=filler*21+'Info'+filler*22, emoji=None, style=discord.ButtonStyle.green, custom_id='info', disabled=False),
                discord.ui.Button(label=filler*18+'UNO'+filler*18, emoji=None, style=discord.ButtonStyle.red, custom_id='uno', disabled=False),
            ],
        ]

        components.insert(0, [
            discord.ui.Button(label=filler*6+'Play Card'+filler*6, emoji=None, style=discord.ButtonStyle.red, custom_id='play', disabled=False),
            discord.ui.Button(label=filler*2+'Draw Card'+filler*3, emoji=None, style=discord.ButtonStyle.blurple, custom_id='draw', disabled=False),
        ])
        if self.stacked > 0:
            components[0][1] = discord.ui.Button(label=filler*1+'Take Cards'+filler*2, emoji=None, style=discord.ButtonStyle.green, custom_id='take')
        elif self.drawn_card is not None:
            components[0][1] = discord.ui.Button(label=filler*4+'Next Turn'+filler*5, emoji=None, style=discord.ButtonStyle.green, custom_id='next')

        for i, row in enumerate(components):
            for component in row:
                component.row = i
                component.callback = self.callback
                if self.is_finished():
                    component.disabled = True  # type: ignore
                self.add_item(component)

    def add_turn_index(self, add: int = 1) -> int:
        return (self.turn_index+add*self.direction.value) % len(self.players)

    def next_turn(self) -> None:
        self.turn_index = self.add_turn_index(add=1)
        self.total_moves += 1
        self.last_move = int(time.time())
        self.drawn_card = None
        self.uno_tracker.update()
        self.check_win()

    def check_win(self) -> None:
        for player in self.players:
            assert player is not None and player in self.hands
            if len(self.hands[player]) <= 0:
                self.winner = player
                self.stop()
                break

    @property
    def turn(self) -> discord.User | discord.Member:
        return self.players[self.turn_index]

    async def callback(self, interaction: discord.Interaction) -> None:
        """Callback for all the components of the view (buttons, selects etc.)."""
        assert interaction.data is not None
        custom_id = interaction.data.get('custom_id')

        match custom_id:
            case 'play':
                self.sort_hand(player=interaction.user)
                view = CardsView(view=self, player=interaction.user)
                return await interaction.response.send_message(embed=view.embed, view=view, ephemeral=True)

            case 'draw':
                self.drawn_card = self.draw_cards(player=self.turn, amount=1)
                if self.drawn_card is not None:
                    self.drawn_card.total_moves_at_draw = self.total_moves
                    if self.drawn_card.can_play() and interaction.user == self.turn:
                        view = CardsView(view=self, player=interaction.user)
                        await interaction.response.send_message(embed=view.embed, view=view, ephemeral=True)
                        self.update_components()
                        await interaction.followup.edit_message(message_id=self.message.id, embed=self.embed, view=self)
                        return
                self.next_turn()

            case 'take':
                self.draw_cards(player=self.turn, amount=self.stacked)
                self.stacked = 0
                self.next_turn()
            
            case 'next':
                self.next_turn()

            case 'uno':
                if len(self.hands[interaction.user]) == 1:
                    if interaction.user not in self.uno_tracker:
                        self.uno_tracker.append(interaction.user)
                    else:
                        return await interaction.response.send_message(f'You already called uno!', ephemeral=True)
                else:
                    return await interaction.response.send_message(f'You have **{len(self.hands[interaction.user])}** cards left, that is not uno..', ephemeral=True)

        self.update_components()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @rig
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        assert interaction.data is not None

        if interaction.user not in self.players:
            await interaction.response.send_message('Start your own game ;-;', ephemeral=True)
            return False

        custom_id = interaction.data.get('custom_id')
        if custom_id in ('play', 'uno', 'info'):
            return True

        elif interaction.user != self.turn:
            await interaction.response.send_message('It is not your turn.', ephemeral=True)
            return False

        return True

    async def on_timeout(self) -> None:
        return await super().on_timeout(stop_subviews=False)


class CardsView(View):
    def __init__(self, view: 'UnoView', player: discord.User | discord.Member) -> None:
        super().__init__(bot=view.bot, ctx=view.ctx, timeout=300.0)
        self.view = view
        self.view.subviews.append(self)
        self.player = player
        self.color_select: Optional[ColorSelect] = None
        self.min_cards_per_row = 3
        self.max_cards_per_row = 5
        self.selected_impossible = False
        self.update_components()

    @property
    def embed(self) -> Embed:
        embed = Embed(title=None, description=f'''
Last refresh: <t:{int(time.time())}:R>
Turn: {self.view.turn.mention} {"**YOU**" if self.view.turn == self.player else ""}
{self.view.stacked_str()}
**Top Card:** (Not in your hand)

{self.view.top_card_str()}
{Emoji(None)}
''')
        cards = self.cards()
        cards_per_row = self.view.cards_per_row[self.player]
        for i, value in enumerate(
            '\n'.join(Emoji(None).join(''.join(line) for line in row) for row in zip(*map(self.view.get_card_emojis, cards[i:i+cards_per_row])))
            for i in range(0, len(self.cards()), cards_per_row)
        ):
            embed.add_field(
                name='** **' if i != 0 else f'**Your Cards:** ({len(cards)})' if self.drawn_card is None else f'**Your Drawn Card:**',
                value=(f'{Emoji(None)}\n' if i == 0 else '')+value, inline=False
            )

        if self.drawn_card is not None:
            embed.add_field(
                name = '** **',
                value = f'''
If for some reason you do not wish to play this card,
click **Next Turn** on the **Main Message**.
'''
            )

        return embed

    @property
    def drawn_card(self) -> Optional[Card]:
        return self.view.drawn_card if self.is_turn() else None
    
    @drawn_card.setter
    def drawn_card(self, value: Optional[Card]) -> None:
        if self.view.players[self.view.turn_index] == self.player:
            self.view.drawn_card = value

    def cards(self) -> list[Card]:
        return self.view.hands[self.player] if self.drawn_card is None else [self.drawn_card]

    def update_components(self) -> None:
        self.clear_items()

        components: list[discord.ui.Button[Self] | discord.ui.Select[Self]] = [
            discord.ui.Button(label='Refresh', emoji=None, style=discord.ButtonStyle.red, custom_id='refresh'),
            discord.ui.Button(label='Main Message', url=self.view.message.jump_url),
        ]
        if self.drawn_card is None:
            components.extend([
                discord.ui.Button(label=None, emoji=Emoji('⬅️'), style=discord.ButtonStyle.blurple, custom_id='cards_per_row_down', disabled=self.view.cards_per_row[self.player] <= self.min_cards_per_row),
                discord.ui.Button(label=None, emoji=Emoji('➡️'), style=discord.ButtonStyle.blurple, custom_id='cards_per_row_up', disabled=self.view.cards_per_row[self.player] >= self.max_cards_per_row),
            ])

        is_turn = self.view.players[self.view.turn_index] == self.player
        placeholder = (f'+{self.view.stacked} STACKED! ' if self.view.stacked > 0 else '') + ((
            'It is currently not your turn, refresh if it is.'
        ) if not is_turn else (
            'Select a card to play HERE.'
        ) if not self.selected_impossible else (
            'That card is not possible.. Can you not read?'
        ))
        if self.selected_impossible:
            self.selected_impossible = False
        components.append(
            CardSelect(
                placeholder=placeholder,
                options=[
                    discord.SelectOption(
                        label=str(card),
                        emoji=self.view.color_to_emoji[card.color],
                        value=card.id,
                        description=('POSSIBLE' if card.can_play() else 'NOT POSSIBLE'),
                    ) for card in self.cards()
                ],
                disabled=not is_turn,
                custom_id='play',
            )
        )

        if self.color_select is not None:
            if self.check_color_select():
                card_select = components[-1]
                assert isinstance(card_select, CardSelect)
                card_select.placeholder = 'Click below me or choose a different card.'
                components.append(self.color_select)
            else:
                self.color_select = None

        for component in components:
            if component.custom_id is not None:
                component.custom_id += self.ignore()
            component.callback = self.callback
            self.add_item(component)

    def is_turn(self) -> bool:
        return self.player == self.view.players[self.view.turn_index]

    def check_color_select(self) -> bool:
        return (
            self.color_select is not None
            and self.color_select.total_moves == self.view.total_moves
            and self.is_turn()
            and self.color_select.card in self.cards()
            and self.color_select.card.can_play()
        )

    def ignore(self) -> str:
        """`str` to add to the `custom_id` of components to prevent Discord from merging views together.
        If this is not done, it will result in a bunch of exploits because of Discord's attempt at saving resources."""
        return f'___{os.urandom(16).hex()}'

    def play(self, card: Card) -> bool:
        """Method that will try to play a card, if this is not possible, return False, else return True."""
        if hasattr(card, 'color_select') and (self.color_select is None or self.color_select.card.id != card.id):
            self.color_select = card.color_select(player=self.player)  # type: ignore
            return False
        if len(self.cards()) == 1 and not self.view.end_special_card:
            self.view.draw_cards(player=self.player, amount=1)
        card.on_play(player=self.player)
        return True

    def allowed_to_play(self, card: Card) -> bool:
        return (
            self.is_turn()
            and card in self.cards()
            and card.can_play()
        )

    async def update(self, interaction: discord.Interaction) -> None:
        """Update the view and edit the message."""
        self.view.sort_hand(player=self.player)
        self.update_components()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    def check_drawn_card(self) -> bool:
        return self.drawn_card is not None and self.drawn_card.total_moves_at_draw != self.view.total_moves

    def ended_embed(self) -> Embed:
        return Embed(
            title=None,
            description=f'''
**[Main Message]({self.view.message.jump_url} "Jump to Main Message")**

Your game of **Uno** has ended!
Feel free to dismiss this.
Or not, I don't care..
'''
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Callback for all the components of the view (buttons, selects etc.)."""
        if self.view.is_finished():
            return await interaction.response.edit_message(embed=self.ended_embed(), view=None)
        elif self.check_drawn_card():
            self.drawn_card = None
            return await self.update(interaction=interaction)

        assert interaction.data is not None
        custom_id = interaction.data.get('custom_id', '').split('___')[0]
        played_a_card: bool = False

        match custom_id:
            case 'refresh':
                pass

            case 'play':
                select = next(item for item in self.children if isinstance(item, CardSelect) and item.custom_id == interaction.data.get('custom_id'))
                card = self.view.id_to_card[select.values[0]]
                if self.allowed_to_play(card=card):
                    played_a_card = self.play(card=card)
                else:
                    self.selected_impossible = True

            case 'color_select':
                if self.check_color_select():
                    select = next(item for item in self.children if isinstance(item, ColorSelect) and item.custom_id == interaction.data.get('custom_id'))
                    card = select.card
                    if self.allowed_to_play(card=card):
                        played_a_card = self.play(card=card)
                        self.view.current_color = Color(int(select.values[0]))

            case 'cards_per_row_up' | 'cards_per_row_down':
                add = {
                    'cards_per_row_up': 1,
                    'cards_per_row_down': -1,
                }[custom_id]

                self.view.cards_per_row[self.player] = max(self.min_cards_per_row, min(self.max_cards_per_row, self.view.cards_per_row[self.player] + add))

        if self.view.is_finished():
            self.view.update_components()
            await self.view.message.edit(embed=self.view.embed, view=self.view)
            return await interaction.response.edit_message(embed=self.ended_embed(), view=None)

        if self.check_drawn_card():
            self.drawn_card = None
        await self.update(interaction=interaction)

        if played_a_card:
            self.view.update_components()
            await self.view.message.edit(embed=self.view.embed, view=self.view)
