#!/usr/bin/env python

import os
from dotenv import load_dotenv
import discord.ext.commands as commands

if __name__ == "__main__":
    # Get secrets
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Bot setup
    bot = commands.Bot(
        command_prefix=["ailie;", "a;"], description="Guardian's collector."
    )
    bot.remove_command("help")

    # Load extensions
    extensions = ["cogs.help", "cogs.basic", "cogs.summon", "cogs.extra"]

    for extension in extensions:
        bot.load_extension(extension)

    # Run bot
    bot.run(TOKEN)
