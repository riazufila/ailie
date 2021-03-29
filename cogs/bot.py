#!/usr/bin/env python

import asyncio
import discord
from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Assign help command to Info category
        self.bot.help_command.cog = self

    # Execute when bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is collecting!")
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="ailie;help"
            )
        )

    # Check bot's latency
    @commands.command(name="ping", help="Check latency.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send("Do `ailie;initialize` or `a;initialize` first before anything!")
            db_ailie.disconnect()
            return
        
        db_ailie.disconnect()

        await ctx.send(
            f"Pong, <@{ctx.author.id}>! Sending back this message with "
            + f"{round(self.bot.latency * 1000)}ms latency."
        )

    # Retrieve Ailie's version
    @commands.command(name="version", help="Shows version.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def version(self, ctx):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send("Do `ailie;initialize` or `a;initialize` first before anything!")
            db_ailie.disconnect()
            return
        
        db_ailie.disconnect()

        # Change upon version update
        version = "1.2.3"

        # Mimic loading animation
        msg = await ctx.send(
            f"Hello, <@{ctx.author.id}>! " + "Ailie reporting to duty!"
        )
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
            msg = await ctx.send(
                f"Yo, <@{ctx.author.id}>..There's no such commands. "
                + "Try again. But properly."
            )
            await ctx.send_help()
            await asyncio.sleep(0.5)
            await msg.edit(content=msg.content + " Hope this helps!")
        elif isinstance(error, commands.MissingRequiredArgument):
            msg = await ctx.send(
                "Not to be rude. But you've got "
                + f"the parameters wrong, <@{ctx.author.id}>."
            )
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.MemberNotFound):
            msg = await ctx.send(
                "No such members. Try again, but try with someone in the "
                + f"server, <@{ctx.author.id}>."
            )
            await asyncio.sleep(0.5)
            await msg.edit(
                content=msg.content
                + " Oh! And `everyone` or `roles` is not a valid option."
            )
        elif isinstance(error, commands.TooManyArguments):
            msg = await ctx.send(
                f"<@{ctx.author.id}>, there's too many arguments."
            )
            await ctx.send_help(ctx.command)
            await asyncio.sleep(0.5)
            await msg.edit(content=msg.content + " Read that!")
        elif isinstance(error, commands.UserInputError):
            msg = await ctx.send(
                f"<@{ctx.author.id}>, are you okay? I don't think "
                + "you're using the command correctly."
            )
            await ctx.send_help(ctx.command)
            await asyncio.sleep(0.5)
            await msg.edit(content=msg.content + " Will that help?")
        else:
            await ctx.send(
                "**Oops! Looks like you found a bug.**"
                + f"\n\n*Error: {error}*\n\nPlease post a new issue under "
                + "the tab 'Issue' at https://github.com/riazufila/ailie."
                + f"\nSorry, <@{ctx.author.id}>.. And thank you."
            )


def setup(bot):
    bot.add_cog(Bot(bot))
