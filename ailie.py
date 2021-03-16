#!/usr/bin/env python

import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

if __name__ == "__main__":
    # Get secrets
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Bot setup
    bot = commands.Bot(command_prefix="ailie;",
                       description="Guardian's collector.")
    bot.remove_command("help")

    # Load extensions
    extensions = ["cogs.basic", "cogs.help", "cogs.hero", "cogs.equipment"]

    for extension in extensions:
        bot.load_extension(extension)

    # Run bot
    bot.run(TOKEN)
