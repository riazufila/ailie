#!/usr/bin/env python

import os
import discord
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
    extensions = ["cogs.help", "cogs.summon"]

    for extension in extensions:
        bot.load_extension(extension)

    # Bot event on_ready
    @bot.event
    async def on_ready():
        print(f"{bot.user} is collecting!")
        await bot.change_presence(activity=discord.Game("Guardian Tales"))

    @bot.command()
    async def version(ctx):
        version = 1.0
        msg = await ctx.send(f"Hello, <@{ctx.author.id}>! Ailie, reporting to duty!")
        await asyncio.sleep(1.5)
        await msg.edit(content=msg.content + "\nMy current version is")
        await asyncio.sleep(0.5)
        await msg.edit(content=msg.content + ".")
        await asyncio.sleep(0.5)
        await msg.edit(content=msg.content + ".")
        await asyncio.sleep(0.5)
        await msg.edit(content=msg.content + f" {version}!")
        await asyncio.sleep(0.5)

    # Run bot
    bot.run(TOKEN)
