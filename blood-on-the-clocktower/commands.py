from discord import Colour
from discord.ext.commands.context import Context

from .bot import bot
from .prisma import prisma_client
from .utils.message import send_message


@bot.command()
async def add(ctx: Context):
    # TODO:
    # - Check if player is already queued
    # - Check if player is already in game
    await prisma_client.player.update(
        where={
            "discord_id": str(ctx.message.author.id),
        },
        data={"is_queued": True},
    )
    queued_players = await prisma_client.player.find_many(where={"is_queued": True})
    await send_message(
        ctx.channel,
        embed_description=f"**{ctx.message.author.display_name}** added to queue\n\nCurrent queue ({len(queued_players)}): {', '.join([f'**{player.display_name}**' for player in queued_players])}",
        colour=Colour.green(),
    )


@bot.command()
async def start(ctx: Context):
    pass
