from datetime import datetime, timezone
import asyncio
import os
from discord import Colour, Embed, Member, Message, Reaction, User
from discord.ext.commands import Context, CommandError, UserInputError
from dotenv import load_dotenv

from .bot import COMMAND_PREFIX, bot
from .prisma import prisma_client


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx: Context, error: CommandError):
    if isinstance(error, UserInputError):
        if ctx.command.usage:
            await ctx.channel.send(
                embed=Embed(
                    description=f"Usage: {COMMAND_PREFIX}{ctx.command.name} {ctx.command.usage}",
                    colour=Colour.red(),
                )
            )
        else:
            await ctx.channel.send(
                embed=Embed(
                    description=f"Usage: {COMMAND_PREFIX}{ctx.command.name} {ctx.command.signature}",
                    colour=Colour.red(),
                )
            )
    else:
        if ctx.command:
            print("[on_command_error]:", error, ", command:", ctx.command.name)
        else:
            print("[on_command_error]:", error)


@bot.event
async def on_message(message: Message):
    print("[on_message]", message.author.display_name, ":", message.content)
    # if CHANNEL_ID and message.channel.id == CHANNEL_ID:
    if True:
        player = await prisma_client.player.find_unique(
            where={"discord_id": str(message.author.id)}
        )
        if player:
            await prisma_client.player.update(
                where={
                    "discord_id": str(message.author.id),
                },
                data={
                    "display_name": message.author.display_name,
                    "last_activity_at": datetime.now(timezone.utc),
                    "name": message.author.name,
                },
            )
        else:
            await prisma_client.player.create(
                data={
                    "discord_id": str(message.author.id),
                    "display_name": message.author.display_name,
                    "last_activity_at": datetime.now(timezone.utc),
                    "name": message.author.name,
                }
            )

    #     else:
    #         session.add(
    #             Player(
    #                 id=message.author.id,
    #                 name=message.author.display_name,
    #                 last_activity_at=datetime.now(timezone.utc),
    #             )
    #         )
    #     session.commit()
    #     session.close()
    #     await bot.process_commands(message)

    #     # Custom commands below
    #     if not message.content.startswith(COMMAND_PREFIX):
    #         return

    #     bot_commands = {command.name for command in bot.commands}
    #     command_name = message.content.split(" ")[0][1:]
    #     session = Session()
    #     if command_name not in bot_commands:
    #         custom_command: CustomCommand | None = (
    #             session.query(CustomCommand)
    #             .filter(CustomCommand.name == command_name)
    #             .first()
    #         )
    #         if custom_command:
    #             await message.channel.send(content=custom_command.output)
    #     session.close()


@bot.event
async def on_reaction_add(reaction: Reaction, user: User | Member):
    pass
    # session = Session()
    # player: Player | None = session.query(Player).filter(Player.id == user.id).first()
    # if player:
    #     player.last_activity_at = datetime.now(timezone.utc)
    #     session.commit()
    # else:
    #     session.add(
    #         Player(
    #             id=reaction.message.author.id,
    #             name=reaction.message.author.display_name,
    #             last_activity_at=datetime.now(timezone.utc),
    #         )
    #     )
    # session.close()


@bot.event
async def on_join(member: Member):
    pass
    # session = Session()
    # player = session.query(Player).filter(Player.id == member.id).first()
    # if player:
    #     player.name = member.name
    #     session.commit()
    # else:
    #     session.add(Player(id=member.id, name=member.name))
    #     session.commit()
    # session.close()


@bot.event
async def on_leave(member: Member):
    pass
    # session = Session()
    # session.query(QueuePlayer).filter(QueuePlayer.player_id == member.id).delete()
    # session.query(QueueWaitlistPlayer).filter(
    #     QueueWaitlistPlayer.player_id == member.id
    # ).delete()
    # session.commit()


def main():
    load_dotenv()
    API_KEY = os.getenv("DISCORD_API_KEY")
    if API_KEY:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(prisma_client.connect())
        bot.run(API_KEY)
    else:
        print("You must define DISCORD_API_KEY!")


if __name__ == "__main__":
    main()
