#!/usr/bin/env python

import discord
from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Guardian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile", help="View profile.")
    async def profile(self, ctx):
        db_ailie = DatabaseAilie(ctx.author.id)
        username, guild_name, position = db_ailie.get_guardian_info(
            ctx.author.id
        )
        guild_id = db_ailie.get_guild_id_of_member(ctx.author.id)

        output = (
            f"**Username**: `{username}`\n**Guild**: "
            + f"`{guild_name}`#`{guild_id}`\n**Position**: `{position}`"
        )

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Guardian's Profile", value=output)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Guardian(bot))
