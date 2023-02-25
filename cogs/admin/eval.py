import discord
from discord.ext import commands
from bot import Butters

from utils import (
    traceback,
    Context,
    Embed,
    View,
)

from contextlib import redirect_stdout
import import_expression
import importlib
import textwrap
import ast
import re
import io

from typing import (
    Awaitable,
    Callable,
    Optional,
    Any,
)

import logging


log = logging.getLogger(__name__)


class EditCodeModal(discord.ui.Modal):
    def __init__(self, view: 'EvalView') -> None:
        super().__init__(title='Edit Eval Code', custom_id='rerun', timeout=None)
        self.view = view
        self.lines = discord.ui.TextInput(label='Code Here', style=discord.TextStyle.paragraph, default=self.view.code or self.view.raw)
        self.add_item(self.lines)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.view.raw = self.lines.value
        return await self.view.callback(interaction=interaction)


class EvalView(View):
    def __init__(self, cog: 'Eval', bot: Butters, ctx: Context, raw: str) -> None:
        super().__init__(bot=bot, ctx=ctx, timeout=300.0)
        self.cog = cog
        self.ctx = ctx
        self.bot = bot
        self.raw = raw
        self.code: Optional[str] = None
        self.result: Optional[Any] = None
        self.update_components()

    def insert_return(self, body: list[ast.stmt]) -> list[ast.stmt]:
        if len(body) == 0:
            return body
        elif isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
        elif isinstance(body[-1], ast.If):
            self.insert_return(body[-1].body)
            self.insert_return(body[-1].orelse)
        elif isinstance(body[-1], ast.With):
            self.insert_return(body[-1].body)
        return body

    def cleanup(self, raw: str) -> str:
        if (raw.startswith('```py\n') or raw.startswith('```\n')) and raw.endswith('```'):
            raw = raw.removeprefix('```py\n').removeprefix('```\n').removesuffix('```')
        raw = raw.strip('` \n')
        return ast.unparse(
            self.insert_return(
                import_expression.parse(raw).body  # type: ignore
            )
        )

    async def run_code(self) -> None:
        env = {
            'bot': self.bot,
            'ctx': self.ctx,
            'message': self.ctx.message,
            'author': self.ctx.author,
            'channel': self.ctx.channel,
            'guild': self.ctx.guild,
            'raw': self.raw,
            '_': self.cog._latest_result,
            import_expression.constants.IMPORTER: lambda name: importlib.import_module(name),
        }
        env.update(globals())

        self.code = None
        self.result = None
        try:
            code = self.cleanup(self.raw)
            env['source'] = code
            to_compile = f'async def foo():\n{textwrap.indent(code, "  ")}'
            exec(to_compile, env)
        except Exception as e:
            self.result = traceback(e)
            return
        else:
            self.code = code

        stream = io.StringIO()
        func: Callable[[], Awaitable[Any]] = env['foo']
        try:
            with redirect_stdout(stream):
                ret = await func()
            value = stream.getvalue()
            if ret is None:
                if value:
                    self.result = value
            else:
                self.cog._latest_result = ret
                self.result = value + str(ret)
        except Exception as e:
            value = stream.getvalue()
            self.result = value + traceback(e)

    def update_components(self) -> None:
        self.clear_items()
        for button in (
            discord.ui.Button(
                label='Edit',
                emoji=None,
                style=discord.ButtonStyle.blurple,
                custom_id='edit',
            ),
            discord.ui.Button(
                label='Re-Run',
                emoji=None,
                style=discord.ButtonStyle.green,
                custom_id='rerun',
            ),
            discord.ui.Button(
                label='Result As File',
                emoji=None,
                style=discord.ButtonStyle.red,
                custom_id='file',
            )
        ):
            button.callback = self.callback
            self.add_item(button)

    async def send_result_file(self, interaction: discord.Interaction, ephemeral: bool = True) -> None:
        assert interaction.message is not None
        if len(interaction.message.attachments) == 0:
            file = discord.File(io.BytesIO(str(self.result).encode()), filename='result.txt')
        else:
            file = await interaction.message.attachments[0].to_file()

        kwargs = {
            'files': [file],
            'ephemeral': ephemeral,
        }
        if ephemeral:
            view = View(bot=self.bot, ctx=self.ctx, timeout=300.0)
            button = discord.ui.Button(label='Non Ephemeral', style=discord.ButtonStyle.blurple)
            view.add_item(button)
            button.callback = lambda interaction: self.send_result_file(interaction=interaction, ephemeral=False)
            kwargs['view'] = view
        return await interaction.response.send_message(**kwargs)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert interaction.data is not None
        custom_id = interaction.data.get('custom_id')

        match custom_id:
            case 'edit':
                return await interaction.response.send_modal(EditCodeModal(view=self))
            case 'rerun':
                await self.run_code()
            case 'file':
                return await self.send_result_file(interaction=interaction)

        self.update_components()
        await interaction.response.edit_message(embed=self.embed, view=self)

    def safe_length(self, text: str, n: int = 1000) -> str:
        margin = 50
        lines = text.splitlines()
        allowed: list[str] = []
        for line in lines:
            now = len('\n'.join(allowed))
            if now + len(line) > n - margin:
                if len(allowed) == 0: 
                    allowed.append(line[:n - margin - now])
                break
            allowed.append(line)
        return '\n'.join(allowed) + (f'\n... and {len(lines) - len(allowed)} more lines.' if len(lines) > len(allowed) else '')

    @property
    def embed(self) -> discord.Embed:
        embed = Embed(title='**Evaluation**')
        code = re.sub(import_expression.constants.IMPORTER + r"\('([a-zA-Z._]+)'\)", r'\1!', (self.code or self.raw))  # eh
        embed.add_field(name='**Code:**', value=f'```py\n{self.safe_length(code)}```', inline=False)
        # result = re.sub('(' + os.getcwd().split('\\')[0] + r'([/\\]{1,2}[a-zA-Z0-9_]+){1,3})', r'~', str(self.result))
        result = str(self.result)
        embed.add_field(name='**Result:**', value=f'```\n{self.safe_length(result)}```', inline=False)
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.ctx.author and interaction.user == self.bot.owner and interaction.user.id == 476083615000821771:
            return True
        else:
            await interaction.response.send_message('You cannot do that!', ephemeral=True)
            return False


default = r'''class HelloWorld:
    __str__ = lambda self: re!.sub(r'\B([A-Z])', r' \1', self.__class__.__name__ + '!')
HelloWorld()'''


class Eval(commands.Cog):
    def __init__(self, bot: Butters) -> None:
        self.bot = bot
        self._latest_result: Optional[Any] = None

    @commands.command(aliases=['py', 'python', 'e'])
    @commands.is_owner()
    async def eval(self, ctx: Context[Butters], *, code: str = default) -> None:
        view = EvalView(cog=self, bot=self.bot, ctx=ctx, raw=code)
        await view.run_code()
        view.message = await ctx.send(embed=view.embed, view=view)


async def setup(bot: Butters) -> None:
    await bot.add_cog(Eval(bot))
