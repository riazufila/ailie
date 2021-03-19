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
    @commands.command(name="ping", help="Check latency.")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def ping(self, ctx):
        await ctx.send(f"Pong, <@{ctx.author.id}>! Sending back this message with {round(self.bot.latency * 1000)}ms latency.")

    # Retrieve Ailie's version
    @commands.command(name="version", help="Shows version.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def version(self, ctx):
        # Change upon version update
        version = "1.1.3"

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
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Yo, <@{ctx.author.id}>.. There's no such commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Not to be rude. But you've got the parameters wrong, <@{ctx.author.id}>.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"No such members. Try again, but try with someone in the server, <@{ctx.author.id}>.")
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(f"<@{ctx.author.id}>, there's too many arguments.")
        elif isinstance(error, commands.UserInputError):
            await ctx.send(f"<@{ctx.author.id}>, are you okay? I don't think you're using the command correctly.")
        else:
            await ctx.send(f"**Oops! An error occured.**\n\n*Error: {error}*\n\nPlease post a new issue under the tab 'Issue' at https://github.com/riazufila/ailie.\nSorry, <@{ctx.author.id}>.. And thank you.")


def setup(bot):
    bot.add_cog(Basic(bot))
