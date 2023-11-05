from discord.ext.tasks import loop
from prisma.enums import GameStatus

from .logger import logger
from .prisma import prisma_client


@loop(seconds=5)
async def game_loop():
    logger.info("game loop")
    game = await prisma_client.game.find_first(where={"status": GameStatus.IN_PROGRESS})
    if not game:
        logger.info("No game in progress, leaving game loop")
    pass
