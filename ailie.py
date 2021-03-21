#!/usr/bin/env python

import os
import discord
from dotenv import load_dotenv
from discord.ext import commands


class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(
                color=discord.Color.purple(), description=page
            )
            await destination.send(embed=embed)


if __name__ == "__main__":
    # Get secrets
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Bot setup
    bot = commands.Bot(
        command_prefix=["ailie;", "a;"],
        description="Guardian's collector.",
        help_command=Help(),
    )

    # Load extensions
    extensions = ["cogs.info", "cogs.summon", "cogs.misc"]

    for extension in extensions:
        bot.load_extension(extension)

    # Run bot
    bot.run(TOKEN)
