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
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

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

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.disconnect()

        await ctx.send(random.choice(reply))

    @commands.command(name="pat", help="Pats Little Princess's head.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pat(self, ctx):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Variables initialized
        gems_to_obtain = []
        counter = 0
        gems = 0

        # Fill gems to obtain list with many random increasing numbers
        while counter < 1500:
            gems_to_obtain.append(random.randint(counter, counter + 500))
            counter += 500

        # Choose gems from list with weights
        gems_obtained = random.choices(gems_to_obtain, [50, 30, 20], k=1)

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        reply = [
            f"Little Princess found you {gems} gems, <@{ctx.author.id}>!",
            "Little Princess did all the hard work for you and got you, "
            + f"{gems} gems. Good one, <@{ctx.author.id}>?",
            f"{gems} gems obtained! You get that by being nice to "
            + f"Little Princess, <@{ctx.author.id}>!",
            f"Don't you ever get tired of Little Princess, <@{ctx.author.id}>? "
            + f"Oh well, she gave you {gems} gems though.",
        ]

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.disconnect()

        await ctx.send(random.choice(reply))

    @commands.command(name="gamble", help="Gamble gems.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def gamble(self, ctx, gems: int):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Disallow negative numbers as input
        if gems <= 0:
            await ctx.send(f"Are you okay, <@{ctx.author.id}>?")
            db_ailie.disconnect()
            return

        # Check if gems is available to gamble
        db_ailie = DatabaseAilie()
        current_gems = db_ailie.get_gems(ctx.author.id)
        balance = current_gems - gems
        if balance < 0:
            await ctx.send(
                "You don't have enough gems to gamble, "
                + f"<@{ctx.author.id}>.."
            )
            db_ailie.disconnect()
            return

        # 50% chance of gambled gems being negative or positive
        gems_obtained = random.choices([-gems, gems], [50, 50], k=1)

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        if gems < 0:
            lost_gems = -gems
            reply = [
                f"<@{ctx.author.id}>, you lost {lost_gems} gems. HAHA.",
                f"Condolences to <@{ctx.author.id}> for losing {lost_gems} "
                + "gems.",
                f"Welp. Lost {lost_gems} gems. Too bad, <@{ctx.author.id}>.",
            ]
        else:
            reply = [
                f"<@{ctx.author.id}>, your luck is omnipotent! Gained "
                + f"{gems} gems.",
                f"Congratulations for winning {gems} gems, <@{ctx.author.id}>!",
                f"Keep the gems rolling, <@{ctx.author.id}>. {gems} gems "
                + "obtained!",
            ]

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.disconnect()

        await ctx.send(random.choice(reply))


def setup(bot):
    bot.add_cog(Currency(bot))
