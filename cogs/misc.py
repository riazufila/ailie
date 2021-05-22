#!/usr/bin/env python

import os
import asyncio
import discord
import random
from discord.ext import commands
from helpers.database import Database


class Misc(commands.Cog):
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
                + f"the parameters wrong, <@{ctx.author.id}>. "
                + "Don't be lazy and read the `help` command!"
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
                f"<@{ctx.author.id}>, there's too many arguments. "
                + "Don't be lazy and read the `help` command!"
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
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(
                "That command can only be used within a Private Message. "
                + "Kindly, send me a Private Message and initiate the "
                + "command again. I won't bite."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                "That command can only be used within a Discord Server."
            )
        elif self.bot.is_ws_ratelimited():
            await ctx.send(
                "We are being rate limited. Nothing can be helped here. "
                + "Please wait and try again."
            )
        elif not commands.bot_has_permissions():
            await ctx.send(
                "Please check that I have the permission, "
                + "`View Channels`, `Send Messages`, `Embed Links` "
                + "`Add Reactions`, `Read Message History`, "
                + "and Manage Messages."
            )
        else:
            await self.notifyOwner(ctx, error)

            official_server = False
            if ctx.guild.id == int(os.getenv("GUILD_ID")):
                official_server = True

            if not official_server:
                await ctx.send(
                    "I encountered a bug. Don't worry. "
                    + "I've logged the bug. However, "
                    + "if it still happens, you might "
                    + "want to join the support server "
                    + "through the `server` command "
                    + "for a more thorough assistance."
                )
            else:
                await ctx.send(
                    "I encountered a bug. Don't worry. "
                    + "I've logged the bug."
                )

    # Pours salt to those lucky people
    @commands.command(
        name="salt",
        brief="Pour salt.",
        description="Someone is too lucky? Pour some salt.",
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pourSalt(self, ctx, mention: discord.Member):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Check if receiver is initialized
        if not db_ailie.is_initialized(mention.id):
            await ctx.send(f"{mention.mention} haven't initialized yet.")
            db_ailie.disconnect()
            return

        db_ailie.disconnect()

        reply = [
            f"*Pours salt on {mention.mention}.. POURING INTENSIFIED!*",
            f"{mention.mention}, get wrecked in mountains of salt!",
            f"THIS IS FOR GETTING LUCKY, {mention.mention}! TAKE ALL THE "
            + "SALT. TAKE IT!",
            "No one is allowed to get this lucky! Especially you, "
            + f"{mention.mention}!",
            f"*Pours multiple bottles of salt at {mention.mention}.*",
            f"Sending boxes of salt to {mention.mention}. "
            + f"From yours truly, <@{ctx.author.id}>.",
            f"<@{ctx.author.id}> wishes there's no cooldown to this command "
            + f"just to keep spamming salt to you, {mention.mention}. HAHA.",
            f"EVERYONE! Come spam salt to, {mention.mention}!",
        ]
        msg = await ctx.send(random.choice(reply))

        # Bot reacts with salt
        await msg.add_reaction("🧂")

    # Press F
    @commands.command(
        name="f",
        brief="Pay respect.",
        description="Someone is too unlucky? Press lots of F.",
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pressF(self, ctx, mention: discord.Member):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Check if receiver is initialized
        if not db_ailie.is_initialized(mention.id):
            await ctx.send(f"Tell {mention.mention} to initialize first!")
            db_ailie.disconnect()
            return

        reply = [
            f"Pay respect to the fallen member, {mention.mention}..",
            f"Be strong, {mention.mention}.",
            f"*Believing is the key, {mention.mention}..*",
            f"Never stop trying. You're not alone, {mention.mention}!",
            f"{mention.mention}, keep fighting!",
            f"Sending support to {mention.mention}. From yours truly, "
            + f"<@{ctx.author.id}>.",
        ]
        msg = await ctx.send(random.choice(reply))

        db_ailie.disconnect()

        # Bot reacts with 'F'
        await msg.add_reaction("🇫")

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

            official_server = False
            if ctx.guild.id == int(os.getenv("GUILD_ID")):
                official_server = True

            if not official_server:
                await ctx.send(
                    f"Ding dong, <@{ctx.author.id}>! "
                    + "Your message has been logged. "
                    + "You might wanna join Ailie's server "
                    + "so you can resolve issues and "
                    + "keep updated on Ailie's updated. "
                    + "If so, then do `a;server`."
                )
            else:
                await ctx.send(
                    f"Ding dong, <@{ctx.author.id}>! "
                    + "Your message has been logged. "
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
        version = "1.9.0"

        await ctx.send(
            f"Hello, <@{ctx.author.id}>! "
            + f"My current version is `{version}`!"
        )


def setup(bot):
    bot.add_cog(Misc(bot))
