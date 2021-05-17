#!/usr/bin/env python

import os
import asyncio
import discord
import aiohttp
from discord.ext import commands
from helpers.database import Database


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command.cog = self

    async def notifyOwner(self, ctx, error, agreement=None):
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(
            name=f"{ctx.me.name}'s Log", icon_url=ctx.me.avatar_url
        )

        if agreement:
            channel = self.bot.get_channel(int(os.getenv("FEEDBACK_CHANNEL")))
            embed.add_field(
                name=str(ctx.command).capitalize(),
                value=error,
                inline=False,
            )
            embed.add_field(
                name="By",
                value=f"{ctx.author}",
                inline=False,
            )

        else:
            channel = self.bot.get_channel(int(os.getenv("ERROR_CHANNEL")))
            embed.add_field(
                name="Command",
                value=ctx.command,
                inline=False,
            )
            arguments = ""
            if len(ctx.args) > 0:
                for args in ctx.args:
                    arguments = arguments + "\n" + str(args)

            embed.add_field(
                name="Arguments",
                value=arguments,
                inline=False,
            )
            embed.add_field(name="Error", value=error, inline=False)
            embed.add_field(
                name="By",
                value=f"{ctx.author}",
                inline=False,
            )

        await channel.send(embed=embed)

    # Execute when bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is collecting!")
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="ailie;help"
            )
        )

    # Send error message upon spamming commands
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Hey, <@{ctx.author.id}>.. {error}!")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(
                f"Yo, <@{ctx.author.id}>.. There's no such commands. "
                + "Try checking `a;help`!"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Not to be rude. But you've got "
                + f"the parameters wrong, <@{ctx.author.id}>."
            )
            await asyncio.sleep(0.5)
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
            await asyncio.sleep(0.5)
            await ctx.send_help(ctx.command)
            await asyncio.sleep(0.5)
            await msg.edit(content=msg.content + " Read that!")
        elif isinstance(error, commands.UserInputError):
            msg = await ctx.send(
                f"<@{ctx.author.id}>, are you okay? I don't think "
                + "you're using the command correctly."
            )
            await asyncio.sleep(0.5)
            await ctx.send_help(ctx.command)
            await asyncio.sleep(0.5)
            await msg.edit(content=msg.content + " Will that help?")
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(f"Yo, <@{ctx.author.id}>! CHILL?")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("That command is only for my awesome creator.")
        elif self.bot.is_ws_ratelimited():
            await ctx.send(
                "We are being rate limited. Nothing can be helped here. "
                + "Please wait and try again."
            )
        elif commands.bot_has_permissions():
            await ctx.send(
                "Please check that I have the permission, "
                + "`View Channels`, `Send Messages`, `Embed Links` "
                + "`Add Reactions`, and `Read Message History`."
            )
        else:
            await self.notifyOwner(ctx, error)

            await ctx.send(
                "I encountered a bug. Don't worry. "
                + "I've logged the bug. However, "
                + "if it still happens, you might "
                + "want to join the support server "
                + "through the `server` command "
                + "for a more thorough assistance."
            )

    # Check bot's latency
    @commands.command(
        name="ping",
        brief="Check latency.",
        description=(
            "Check how many milliseconds is Ailie taking to respond. "
            + "This can be used to check if Ailie is responsive."
        ),
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        db_ailie.disconnect()

        await ctx.send(
            f"Pong, <@{ctx.author.id}>! Sending back this message with "
            + f"{round(self.bot.latency * 1000)}ms latency."
        )

    # Send feedback or issue to owner
    @commands.command(
        name="feedback",
        brief="Sends feedback.",
        description=(
            "Sends feedback, issue, complaint. "
            + "Basically anything that requires assistance. "
            + "Do note that along with the feedback, "
            + "your user info will also be sent."
        ),
        aliases=["fe"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def feedback(self, ctx, *feedback):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        db_ailie.disconnect()

        if feedback:
            # Process complain
            feedback = " ".join(feedback)
            await self.notifyOwner(ctx, feedback, "agree")

            # Mimic loading animation
            await ctx.send(
                f"Ding dong, <@{ctx.author.id}>! "
                + "Your message has been logged. "
                + "You might wanna join Ailie's server "
                + "so you can resolve issues and "
                + "keep updated on Ailie's updated. "
                + "If so, then do `a;server`."
            )
        else:
            await ctx.send("Can't send anything since you put no messages!")

    @commands.command(
        name="server",
        brief="Sends server's invite link.",
        description=("Sends an active invite link to Ailie's server."),
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def server(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        db_ailie.disconnect()

        await ctx.send(
            "Here's the link to Ailie's server, "
            + f"<{os.getenv('SERVER_INVITE')}>."
        )

    # Retrieve Ailie's version
    @commands.command(
        name="version",
        brief="Shows version.",
        description=(
            "Shows the version Ailie is currently bearing. "
            + "The version uses the format `x.y.z` where "
            + "`x` is for major updates, "
            + "`y` is for minor updates, and `z` is for bug fixes."
        ),
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def version(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        db_ailie.disconnect()

        # Change upon version update
        version = "1.8.3"

        await ctx.send(
            f"Hello, <@{ctx.author.id}>! "
            + f"My current version is `{version}`!"
        )


def setup(bot):
    bot.add_cog(Bot(bot))
