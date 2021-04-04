#!/usr/bin/env python

import random
import discord
from discord.ext import commands
from helpers.database import Database


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="race", help="Race against Lana.", aliases=["rc"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def race(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
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

    @commands.command(
        name="pat", help="Pats Little Princess's head.", aliases=["pt"]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pat(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
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

    @commands.command(
        name="gamble",
        help="Gamble gems.",
        aliases=["gamb", "gam", "bet"],
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def gamble(self, ctx, gems: int):
        # Check if user is initialized first
        db_ailie = Database()
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
        db_ailie = Database()
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

    @commands.command(
        name="share", help="Share gems.", aliases=["shr", "sh", "give"]
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def share(self, ctx, gems: int, mention: discord.Member):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        # Check if receiver is initialized
        if not db_ailie.is_initialized(mention.id):
            await ctx.send(
                f"Poor thing.. {mention.mention} haven't initialized yet. "
                + f"Tell {mention.mention} to initialize so you can share "
                + "your precious gems!"
            )
            db_ailie.disconnect()
            return

        # Disallow negative numbers as input
        if gems <= 0:
            await ctx.send(f"Are you high, <@{ctx.author.id}>?")
            db_ailie.disconnect()
            return

        # Check if gems is available to gamble
        db_ailie = Database()
        current_gems = db_ailie.get_gems(ctx.author.id)
        balance = current_gems - gems
        if balance < 0:
            await ctx.send(
                "To share gems, you need gems yourself first, "
                + f"<@{ctx.author.id}>.."
            )
            db_ailie.disconnect()
            return

        # Transfer gems from sender to receiver
        db_ailie.spend_gems(ctx.author.id, gems)
        db_ailie.store_gems(mention.id, gems)
        await ctx.send(
            f"<@{ctx.author.id}> shared {gems} gem(s) to {mention.mention}. "
            + "SWEET!"
        )

    @commands.command(name="rich", help="Show whales.", aliases=["rch", "rh"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rich(self, ctx, scope="server"):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        # initialize database
        db_ailie = Database()

        # Get members in discord server that is initialized
        guardian_with_gems = []
        logical_whereabouts = ""
        output = ""

        if scope.lower() in ["server", "svr", "s"]:
            logical_whereabouts = ctx.guild.name
            async for member in ctx.guild.fetch_members(limit=None):
                if db_ailie.is_initialized(member.id):
                    gems = db_ailie.get_gems(member.id)
                    buffer = [gems, member, member.id]
                    guardian_with_gems.append(buffer)
        elif scope.lower() in ["global", "glob", "g"]:
            logical_whereabouts = "Global"
            for guild in self.bot.guilds:
                async for member in guild.fetch_members(limit=None):
                    if db_ailie.is_initialized(member.id):
                        gems = db_ailie.get_gems(member.id)
                        buffer = [gems, member, member.id]
                        if buffer not in guardian_with_gems:
                            guardian_with_gems.append(buffer)
        else:
            await ctx.send(
                "Dear, <@{ctx.author.id}>. You can only specify `server` "
                + "or `global`."
            )

        # Display richest user in discord server
        guardian_with_gems = guardian_with_gems[:10]
        guardian_with_gems.sort(reverse=True)
        counter = 1
        for whales in guardian_with_gems:
            if counter == 1:
                output = output + f"{counter}. {whales[0]} 💎 - `{whales[1]}`"
            else:
                output = output + f"\n{counter}. {whales[0]} 💎 - `{whales[1]}`"

            # Get username if any
            username = db_ailie.get_username(whales[2])
            if username is not None:
                output = output + f" a.k.a. `{username}`"

            counter += 1

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name="Ailie", icon_url=ctx.me.avatar_url)
        embed.add_field(name=f"Whales in {logical_whereabouts}!", value=output)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Currency(bot))
