import discord
from .exceptions import (
    traceback,
)

from typing import (
    TYPE_CHECKING,
)
from typing_extensions import (
    Self,
)
if TYPE_CHECKING:
    from bot import Butters
    from utils import (
        Context,
    )


__all__ = (
    'View',
)


class View(discord.ui.View):
    bot: 'Butters'
    ctx: 'Context'
    message: discord.Message
    def __init__(self, bot: 'Butters', ctx: 'Context', *args, **kwargs) -> None:
        self.bot = bot
        self.ctx = ctx
        super().__init__(*args, **kwargs)

    async def _scheduled_task(self, item: discord.ui.Item[Self], interaction: discord.Interaction) -> None:
        if TYPE_CHECKING:
            assert isinstance(interaction.client, 'Butters')

        if interaction.user.id != interaction.client.owner.id and (
            interaction.user.id in interaction.client.blacklist
            or (
                interaction.guild is not None and
                interaction.guild.id in interaction.client.blacklist
            )
        ):
            await interaction.response.defer()
            return

        return await super()._scheduled_task(item, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item[Self]) -> None:
        if TYPE_CHECKING:
            assert isinstance(interaction.client, 'Butters')
        send = interaction.response.send_message if not interaction.response.is_done() else interaction.followup.send
        await send(traceback(error, snippet=True), ephemeral=True)
        raise error

    async def on_timeout(self, stop_subviews: bool = True) -> None:
        self.stop()

        if stop_subviews and hasattr(self, 'subviews'):
            self.subviews: list[View]
            for subview in self.subviews:
                if not subview.is_finished():
                    subview.stop()

        if hasattr(self, 'message'):
            for component in self.children:
                if hasattr(component, 'disabled'):
                    component.disabled = True  # type: ignore
            await self.message.edit(view=self)
