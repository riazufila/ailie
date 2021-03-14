#!/usr/bin/env python

import os
from dotenv import load_dotenv
from discord.ext import commands

if __name__ == "__main__":
    # Get secrets
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Bot setup
    bot = commands.Bot(command_prefix="ailie;",
                       description="Guardian's companion.")

    # Bot event on_ready
    @bot.event
    async def on_ready():
        print(f"{bot.user} is now active!")

    # Run bot
    bot.run(TOKEN)
