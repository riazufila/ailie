#!/usr/bin/env python

import os
import discord
from helpers.help import Help
from dotenv import load_dotenv
from discord.ext import commands

if __name__ == "__main__":
    # Get secrets
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Bot setup
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(
        command_prefix=["ailie;", "a;"],
        description="Guardian's collector.",
        help_command=Help(),
        intents=intents,
    )

    # Load extensions
    extensions = ["cogs.bot", "cogs.summon", "cogs.guild", "cogs.misc"]

    for extension in extensions:
        bot.load_extension(extension)

    # Run bot
    bot.run(TOKEN)
