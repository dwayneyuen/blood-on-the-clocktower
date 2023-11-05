from discord.ext.commands import Bot, Cog, Context
from discord.ext.tasks import loop
from prisma.enums import GamePhase, GameStatus

from ...logger import logger
from ...prisma import prisma_client
from ...utils.asserts import assert_never


class GameCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.game_loop.start()

    @loop(seconds=5)
    async def game_loop(self):
        """
        The main game loop
        """
        game = await prisma_client.game.find_first(
            where={"status": GameStatus.IN_PROGRESS}
        )
        if not game:
            logger.info("No game in progress, leaving game loop")
            return

        if game.phase is GamePhase.DAY:
            pass
        elif game.phase is GamePhase.NIGHT:
            pass
        else:
            assert_never(game.phase)
