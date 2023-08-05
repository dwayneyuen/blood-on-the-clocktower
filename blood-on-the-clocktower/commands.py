from typing import List
from discord import Colour
from discord.ext.commands.context import Context
from prisma.models import Player

from .bot import bot
from .configurations import MINIMUM_PLAYERS
from .prisma import prisma_client
from .utils.message import send_message


def queue_string(players: List[Player]) -> str:
    if len(players) < MINIMUM_PLAYERS:
        return f"Current queue (**{len(players)}**) (_{MINIMUM_PLAYERS} required_): {', '.join([f'**{player.display_name}**' for player in players])}"
    else:
        return f"Current queue ({len(players)}): {', '.join([f'**{player.display_name}**' for player in players])}"


@bot.command()
async def add(ctx: Context):
    # TODO:
    # - Check if player is already queued
    # - Check if player is already in game
    player = await prisma_client.player.find_unique(
        where={
            "discord_id": str(ctx.message.author.id),
        }
    )
    queued_players = await prisma_client.player.find_many(where={"is_queued": True})
    if player.is_queued:
        await send_message(
            ctx.channel,
            embed_description=f"**{ctx.message.author.display_name}** is already in the queue!\n\n{queue_string(queued_players)}",
            colour=Colour.red(),
        )
        return

    await prisma_client.player.update(
        where={
            "discord_id": str(ctx.message.author.id),
        },
        data={"is_queued": True},
    )
    if len(queued_players) < MINIMUM_PLAYERS:
        await send_message(
            ctx.channel,
            embed_description=f"**{ctx.message.author.display_name}** added to queue\n\n{queue_string(queued_players)}",
            colour=Colour.green(),
        )
    else:
        await send_message(
            ctx.channel,
            embed_description=f"**{ctx.message.author.display_name}** added to queue\n\n{queue_string(queued_players)}",
            colour=Colour.green(),
        )


@bot.command()
async def start(ctx: Context):
    pass


@bot.command()
async def status(ctx: Context):
    queued_players = await prisma_client.player.find_many(where={"is_queued": True})
    await send_message(
        ctx.channel,
        embed_description=queue_string(queued_players),
        colour=Colour.green(),
    )
