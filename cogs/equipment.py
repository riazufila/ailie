#!/usr/bin/env python

import asyncio
import random
from discord.ext import commands


class Equipment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Equipment(bot))
