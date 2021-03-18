#!/usr/bin/env python

import asyncio
import discord
from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Execute when bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is collecting!")
        await self.bot.change_presence(activity=discord.Game("Guardian Tales"))

    # Check bot's latency
    @commands.command(name="ping", help="Check latency.", aliases=["p"])
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def ping(self, ctx):
        await ctx.send(f"Pong, <@{ctx.author.id}>! Sending back this message with {round(self.bot.latency * 1000)}ms latency.")

    # Retrieve Ailie's version
    @commands.command(name="version", help="Shows version.", aliases=["v"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def version(self, ctx):
        # Change upon version update
        version = "1.1.2"

        # Mimic loading animation
        msg = await ctx.send(f"Hello, <@{ctx.author.id}>! Ailie reporting to duty!")
        await asyncio.sleep(1.5)
        await msg.edit(content=msg.content + "\nMy current version is")
        await asyncio.sleep(0.5)
        await msg.edit(content=msg.content + ".")
        await asyncio.sleep(0.5)
        await msg.edit(content=msg.content + ".")
        await asyncio.sleep(0.5)
        await msg.edit(content=msg.content + f" {version}!")
        await asyncio.sleep(0.5)

    # Send error message upon spamming commands
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Hey, <@{ctx.author.id}>.. {error}!")
        else:
            await ctx.send(f"**Oops! An error occured.**\n\n*Error: {error}.*\n\nThis is expected as this bot is still under heavy development.\nPlease post an issue at https://github.com/riazufila/ailie.\n\nSorry, <@{ctx.author.id}>.. And thank you.")


def setup(bot):
    bot.add_cog(Basic(bot))
