#!/usr/bin/env python

import random
import discord
from discord.ext import commands


class Extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Pours salt to those lucky people
    @commands.command(name="salt", help="Pour salt.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pourSalt(self, ctx, mention: discord.Member):
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
    @commands.command(name="f", help="Pay respect.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pressF(self, ctx, mention: discord.Member):
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

        # Bot reacts with 'F'
        await msg.add_reaction("🇫")


def setup(bot):
    bot.add_cog(Extra(bot))
