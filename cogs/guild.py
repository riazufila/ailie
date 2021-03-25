#!/usr/bin/env python

from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create", help="Create guild.")
    async def create(self, ctx):
        return "data"


def setup(bot):
    bot.add_cog(Guild(bot))
