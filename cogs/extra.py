#!/usr/bin/env python

import asyncio
import discord
from discord.ext import commands


class Extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Retrieve Ailie's version
    @commands.command(name="salt", help="Pour salt on someone")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pourSalt(self, ctx, mention: discord.Member):
        try:
            await ctx.send(f"*Pours salt on <@{mention.id}>*")
        except:
            await ctx.send(f"<@{ctx.author.id}, please mention someone you wanna pour salt to.>")


def setup(bot):
    bot.add_cog(Extra(bot))
