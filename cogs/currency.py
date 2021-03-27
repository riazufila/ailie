#!/usr/bin/env python

import random
from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="race", help="Race against Lana.")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def race(self, ctx):
        # Variables initialized
        gems_to_obtain = []
        counter = 0
        gems = 0

        # Fill gems to obtain list with many random increasing numbers
        while counter < 500:
            gems_to_obtain.append(random.randint(counter, counter + 100))
            counter += 100

        # Choose gems from list with weights
        gems_obtained = random.choices(
            gems_to_obtain, [65, 20, 10, 3.5, 1.5], k=1
        )

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        reply = [
            f"You raced against Lana and obtained {gems} gems, "
            + f"<@{ctx.author.id}>!",
            f"You got {gems} gems! Lana can't win with that wheelchair on. "
            + f"Right, <@{ctx.author.id}>?",
            f"YES! {gems} gems obtained! Good job, <@{ctx.author.id}>!",
            f"Don't you get tired of racing Lana, <@{ctx.author.id}>? Oh well, "
            + f"you've gotten {gems} gems though.",
        ]

        db_ailie = DatabaseAilie(ctx.author.id)
        db_ailie.store_gems(ctx.author.id, gems)

        await ctx.send(random.choice(reply))


def setup(bot):
    bot.add_cog(Currency(bot))
