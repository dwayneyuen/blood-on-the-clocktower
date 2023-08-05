from typing import List
from uuid import uuid4
from discord import Colour
from discord.ext.commands.context import Context
from faker import Faker
from prisma.enums import (
    DemonRole,
    GamePhase,
    GameStatus,
    MinionRole,
    OutsiderRole,
    TownsfolkRole,
)
from prisma.models import Player
from random import choice, sample, shuffle

from .bot import bot
from .config import DEBUG
from .configurations import MINIMUM_PLAYERS, CONFIGURATIONS
from .prisma import prisma_client
from .strings import INTRO_LINES
from .utils.message import send_message


def queue_string(players: List[Player]) -> str:
    if len(players) < MINIMUM_PLAYERS:
        return f"Current queue (**{len(players)}**) (_{MINIMUM_PLAYERS} required_): {', '.join([f'**{player.display_name}**' for player in players])}"
    else:
        return f"Current queue ({len(players)}): {', '.join([f'**{player.display_name}**' for player in players])}"


@bot.command()
async def add(ctx: Context):
    # TODO:
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
    await send_message(
        ctx.channel,
        embed_description=f"**{ctx.message.author.display_name}** added to queue\n\n{queue_string(queued_players)}",
        colour=Colour.green(),
    )


@bot.command()
async def addfakeplayers(ctx: Context, count: int):
    if count <= 0 or count > 20:
        await send_message(
            ctx.channel,
            embed_description="Count must be between than 1 and 20",
            colour=Colour.red(),
        )
        return

    faker = Faker()
    await prisma_client.player.create_many(
        data=[
            {
                "discord_id": str(uuid4()),
                "display_name": faker.name(),
                "name": faker.name(),
                "is_fake": True,
                "is_queued": True,
            }
            for _ in range(count)
        ]
    )
    queued_players = await prisma_client.player.find_many(where={"is_queued": True})
    await send_message(
        ctx.channel,
        embed_description=queue_string(queued_players),
        colour=Colour.green(),
    )


@bot.command()
async def clearqueue(ctx: Context):
    await prisma_client.player.update_many(
        where={"is_queued": True},
        data={"is_queued": False},
    )
    await send_message(
        ctx.channel,
        embed_description=f"Queue cleared!",
        colour=Colour.blue(),
    )


@bot.command()
async def start(ctx: Context):
    queued_players = await prisma_client.player.find_many(where={"is_queued": True})
    configuration = CONFIGURATIONS[len(queued_players)]
    if not configuration:
        await send_message(
            ctx.channel,
            embed_description=f"**{MINIMUM_PLAYERS}** players required to start! Current queue size: **{len(queued_players)}**",
            colour=Colour.red(),
        )
        return

    demon_roles = sample(list(DemonRole), configuration.demons)
    minion_roles = sample(list(MinionRole), configuration.minions)
    outsider_roles = sample(list(OutsiderRole), configuration.outsiders)
    townsfolk_roles = sample(list(TownsfolkRole), configuration.townsfolk)
    roles = townsfolk_roles + outsider_roles + minion_roles + demon_roles

    if len(queued_players) != len(roles):
        await send_message(
            ctx.channel,
            embed_description=f"**ConfigurationError:** The number of roles does not match the number of players",
            colour=Colour.red(),
        )
        return

    game = await prisma_client.game.create(
        data={"phase": GamePhase.NIGHT, "status": GameStatus.IN_PROGRESS}
    )

    shuffle(queued_players)
    for role in demon_roles:
        player = queued_players.pop()
        await prisma_client.gameplayer.create(
            data={
                "demon_role": role,
                "game_id": game.id,
                "player_id": player.id,
            }
        )
    for role in minion_roles:
        player = queued_players.pop()
        await prisma_client.gameplayer.create(
            data={
                "minion_role": role,
                "game_id": game.id,
                "player_id": player.id,
            }
        )
    for role in outsider_roles:
        player = queued_players.pop()
        await prisma_client.gameplayer.create(
            data={
                "outsider_role": role,
                "game_id": game.id,
                "player_id": player.id,
            }
        )
    for role in townsfolk_roles:
        player = queued_players.pop()
        await prisma_client.gameplayer.create(
            data={
                "townsfolk_role": role,
                "game_id": game.id,
                "player_id": player.id,
            }
        )

    message: List[str] = []
    message.append(f"Game started with **{len(roles)}** players!")
    message.append(f"**demons: {configuration.demons}**")
    message.append(f"**Minions: {configuration.minions}**")
    message.append(f"**Outsiders: {configuration.outsiders}**")
    message.append(f"**Townsfolk: {configuration.townsfolk}**")
    message.append("\n")
    message.append(f"_{choice(INTRO_LINES)}_")

    await send_message(
        ctx.channel,
        embed_description="\n".join(message),
        colour=Colour.green(),
    )


@bot.command()
async def queue(ctx: Context):
    queued_players = await prisma_client.player.find_many(where={"is_queued": True})
    await send_message(
        ctx.channel,
        embed_description=queue_string(queued_players),
        colour=Colour.green(),
    )


@bot.command()
async def status(ctx: Context):
    in_progress_game = await prisma_client.game.find_first(
        where={"status": GameStatus.IN_PROGRESS}
    )
    if not in_progress_game:
        await send_message(
            ctx.channel,
            embed_description="No game in progress",
            colour=Colour.blue(),
        )
        return

    game_players = await prisma_client.gameplayer.find_many(
        where={"game_id": in_progress_game.id}, include={"player": True}
    )
    configuration = CONFIGURATIONS[len(game_players)]

    living_players = list(
        filter(lambda game_player: game_player.is_alive, game_players)
    )
    dead_players = list(
        filter(lambda game_player: not game_player.is_alive, game_players)
    )

    message: List[str] = []
    living_players_string = ", ".join(
        map(lambda gp: gp.player.display_name, living_players)
    )
    dead_players_string = ", ".join(
        map(lambda gp: gp.player.display_name, dead_players)
    )
    message.append(f"**Game ID _(DEBUG)_:** {in_progress_game.id}")
    message.append(f"")
    if configuration:
        message.append(f"**Demons:** {configuration.demons}")
        message.append(f"**Minions:** {configuration.minions}")
        message.append(f"**Outsiders:** {configuration.outsiders}")
        message.append(f"**Townsfolk:** {configuration.townsfolk}")
        message.append(f"")
    message.append(f"**Living ({len(living_players)}):** {living_players_string}")
    message.append(f"**Dead ({len(dead_players)}):** {dead_players_string}")
    message.append(f"")

    if DEBUG:
        demons = list(
            filter(
                lambda game_player: game_player.demon_role is not None,
                game_players,
            )
        )
        minions = list(
            filter(
                lambda game_player: game_player.minion_role is not None,
                game_players,
            )
        )
        townsfolk = list(
            filter(
                lambda game_player: game_player.townsfolk_role is not None,
                game_players,
            )
        )
        outsiders = list(
            filter(
                lambda game_player: game_player.outsider_role is not None,
                game_players,
            )
        )
        message.append(
            f"**Demons ({len(demons)}):** {', '.join(map(lambda gp: gp.player.display_name, demons))}"
        )
        message.append(
            f"**Minions ({len(minions)}):** {', '.join(map(lambda gp: gp.player.display_name, minions))}"
        )
        message.append(
            f"**Townsfolk ({len(townsfolk)}):** {', '.join(map(lambda gp: gp.player.display_name, townsfolk))}"
        )
        message.append(
            f"**Outsiders ({len(outsiders)}):** {', '.join(map(lambda gp: gp.player.display_name, outsiders))}"
        )

    print(message)
    await send_message(
        ctx.channel,
        embed_description="\n".join(message),
        colour=Colour.blue(),
    )
