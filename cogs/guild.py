#!/usr/bin/env python

import random
from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create", help="Create guild.")
    async def create(self, ctx, guild_name):
        db_ailie = DatabaseAilie(ctx.author.id)
        guild_check = True
        guild_id = 0

        while guild_check:
            guild_id = random.randint(pow(10, 14), (pow(10, 15) - 1))
            guild_check = db_ailie.guild_exists(guild_id)

        if db_ailie.is_guildless(ctx.author.id):
            db_ailie.create_guild(ctx.author.id, guild_id, guild_name)
            await ctx.send(
                f"Congratulations, <@{ctx.author.id}>! You have created "
                + f"a Guild named, `{guild_name}` with the ID, `{guild_id}`."
            )
        else:
            await ctx.send(
                "I don't think you should be creating a guild when you "
                + f"already have one. No, <@{ctx.author.id}>?"
            )

        db_ailie.disconnect()

    @commands.command(name="join", help="Join guild.")
    async def join(self, ctx, guild_id):
        db_ailie = DatabaseAilie(ctx.author.id)

        if db_ailie.is_guildless(ctx.author.id):
            db_ailie.join_guild(ctx.author.id, guild_id)
            await ctx.send(
                f"<@{ctx.author.id}> has joined the guild "
                + f"with an ID of `{guild_id}`."
            )


def setup(bot):
    bot.add_cog(Guild(bot))
