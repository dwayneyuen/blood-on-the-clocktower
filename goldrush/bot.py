import os

import discord
from discord.ext.commands import Bot, DefaultHelpCommand
from dotenv import load_dotenv

from .cogs.game.game import GameCog

intents = discord.Intents.default()
intents.members = True

load_dotenv()
COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX") or "!"

bot = Bot(
    case_insensitive=True,
    command_prefix=COMMAND_PREFIX,
    help_command=DefaultHelpCommand(verify_checks=False, dm_help=True),
    intents=intents,
)

bot.add_cog(GameCog(bot))
