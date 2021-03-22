#!/usr/bin/env python

import asyncio
import discord
from discord.ext import commands
from helpers.ailie_db import Database


class Info(commands.Cog):
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
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def ping(self, ctx):
        await ctx.send(
            f"Pong, <@{ctx.author.id}>! Sending back this message with "
            + f"{round(self.bot.latency * 1000)}ms latency."
        )

    # Retrieve Ailie's version
    @commands.command(name="version", help="Shows version.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def version(self, ctx):
        # Change upon version update
        version = "1.1.3"

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

    # Retrieve guardian profile
    @commands.command(name="profile", help="Shows user profile.")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def profile(self, ctx):
        # Initialize and retrieve gems count for user
        ailie_db = Database()
        guardian_info = ailie_db.getGuardianInfo(ctx.author.id)
        if guardian_info:
            expired = ailie_db.checkTimeExpired(ctx.author.id)
        else:
            await ctx.send(
                f"<@{ctx.author.id}>, summon first before you can have any "
                + "profile at all!"
            )
            return
        ailie_db.disconnect()

        if expired:
            guardian_info["tmp_gems"] = 0

        embed = discord.Embed(
            description="User statistics according to summons.",
            color=discord.Color.purple(),
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(
            name="Session",
            value=f"{guardian_info['tmp_gems']} 💎",
        )
        embed.add_field(
            name="Overall",
            value=f"{guardian_info['total_gems']} 💎",
        )
        embed.set_footer(
            text="Session is the total gems used in continuation in less "
            + "than\n10 minutes between one pull and the other.\nOverall "
            + "is the total gems used for every summon including\nseparate "
            + "sessions."
        )

        await ctx.send(embed=embed)

    # Send error message upon spamming commands
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Hey, <@{ctx.author.id}>.. {error}!")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(
                f"Yo, <@{ctx.author.id}>..There's no such commands. "
                + "Try again. But properly."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Not to be rude. But you've got"
                + f"the parameters wrong, <@{ctx.author.id}>."
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                "No such members. Try again, but try with someone in the "
                + f"server, <@{ctx.author.id}>."
            )
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(f"<@{ctx.author.id}>, there's too many arguments.")
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"<@{ctx.author.id}>, are you okay? I don't think "
                + "you're using the command correctly."
            )
        else:
            await ctx.send(
                "**Oops! Looks like you found a bug.**"
                + f"\n\n*Error: {error}*\n\nPlease post a new issue under "
                + "the tab 'Issue' at https://github.com/riazufila/ailie."
                + f"\nSorry, <@{ctx.author.id}>.. And thank you."
            )


def setup(bot):
    bot.add_cog(Info(bot))
