#!/usr/bin/env python

import random
import discord
from discord.ext import commands
from helpers.database import Database


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="race",
        brief="Race against Lana.",
        description=(
            "Participate in racing Lana where a random amount "
            + "of gems from roughly 10 to 500 can be obtained."
        ),
    )
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
            gems_to_obtain.append(random.randint(counter + 10, counter + 100))
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
            f"You raced against Lana and obtained {gems:,d} gems, "
            + f"<@{ctx.author.id}>!",
            f"You got {gems:,d} gems! Lana can't win with that wheelchair on. "
            + f"Right, <@{ctx.author.id}>?",
            f"YES! {gems:,d} gems obtained! Good job, <@{ctx.author.id}>!",
            f"Don't you get tired of racing Lana, <@{ctx.author.id}>? Oh well, "
            + f"you've gotten {gems:,d} gems though.",
        ]

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.update_user_exp(ctx.author.id, 2)
        db_ailie.disconnect()

        await ctx.send(random.choice(reply))

    @commands.command(
        name="pat",
        brief="Pats Little Princess's head.",
        description=(
            "Obtain roughly 10 to 1500 gems depending on "
            + "how much Little Princess likes you."
        ),
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
            gems_to_obtain.append(random.randint(counter + 10, counter + 500))
            counter += 500

        # Choose gems from list with weights
        gems_obtained = random.choices(gems_to_obtain, [50, 30, 20], k=1)

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        reply = [
            f"Little Princess found you {gems:,d} gems, <@{ctx.author.id}>!",
            "Little Princess did all the hard work for you and got you, "
            + f"{gems:,d} gems. Good one, <@{ctx.author.id}>?",
            f"{gems:,d} gems obtained! You get that by being nice to "
            + f"Little Princess, <@{ctx.author.id}>!",
            f"Don't you ever get tired of Little Princess, <@{ctx.author.id}>? "
            + f"Oh well, she gave you {gems:,d} gems though.",
        ]

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.update_user_exp(ctx.author.id, 3)
        db_ailie.disconnect()

        await ctx.send(random.choice(reply))

    @commands.command(
        name="gamble",
        brief="Gamble gems.",
        description=(
            "Gamble any amount of gems (of course you can't gamble 0 gems "
            + "or less) to gain the exact amount back in return. That. "
            + "Or you lose the gems gambled."
        ),
    )
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
                f"<@{ctx.author.id}>, you lost {lost_gems:,d} gems. HAHA.",
                f"Condolences to <@{ctx.author.id}> for losing {lost_gems:,d} "
                + "gems.",
                f"Welp. Lost {lost_gems:,d} gems. Too bad, <@{ctx.author.id}>.",
            ]
            db_ailie.store_lose_gambled_count(ctx.author.id)
            db_ailie.store_lose_gambled_gems(ctx.author.id, lost_gems)
        else:
            reply = [
                f"<@{ctx.author.id}>, your luck is omnipotent! Gained "
                + f"{gems:,d} gems.",
                f"Congratulations for winning {gems:,d} gems, "
                + f"<@{ctx.author.id}>!",
                f"Keep the gems rolling, <@{ctx.author.id}>. {gems:,d} gems "
                + "obtained!",
            ]
            db_ailie.store_gambled_gems(ctx.author.id, gems)
            db_ailie.store_win_gambled_count(ctx.author.id)
            db_ailie.store_won_gambled_gems(ctx.author.id, gems)

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.store_gambled_count(ctx.author.id)
        db_ailie.update_user_exp(ctx.author.id, 10)
        db_ailie.disconnect()

        await ctx.send(random.choice(reply))

    @commands.command(
        name="share",
        brief="Share gems.",
        description=(
            "Give a certain amount of gems that you obtain to someone else."
        ),
        aliases=["give", "gift"],
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
        if gems < 0:
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
        db_ailie.update_user_exp(ctx.author.id, 5)
        await ctx.send(
            f"<@{ctx.author.id}> shared {gems:,d} gem(s) to {mention.mention}. "
            + "SWEET!"
        )

    @commands.command(
        name="rich",
        brief="Show whales.",
        description=(
            "Rank users based on the server you're in or globally. "
            + "To rank based on the server you're in, put `server` as "
            + "the scope (default). To rank based on global, "
            + "put `global` as the scope."
        ),
    )
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

        # Get members in discord server that is initialized
        guardian_with_gems = []
        logical_whereabouts = ""
        output = ""

        if scope.lower() in ["server"]:
            logical_whereabouts = ctx.guild.name
            async for member in ctx.guild.fetch_members(limit=None):
                if db_ailie.is_initialized(member.id):
                    gems = db_ailie.get_gems(member.id)
                    if gems != 0:
                        buffer = [gems, member, member.id]
                        guardian_with_gems.append(buffer)
        elif scope.lower() in ["global", "all"]:
            await ctx.send(
                "Global rank will take a while to produce.. "
                + f"Please wait, <@{ctx.author.id}>."
            )
            logical_whereabouts = "Global"
            for guild in self.bot.guilds:
                async for member in guild.fetch_members(limit=None):
                    if db_ailie.is_initialized(member.id):
                        gems = db_ailie.get_gems(member.id)
                        if gems != 0:
                            buffer = [gems, member, member.id]
                            if buffer not in guardian_with_gems:
                                guardian_with_gems.append(buffer)
        else:
            await ctx.send(
                f"Dear, <@{ctx.author.id}>. You can only specify `server` "
                + "or `global`."
            )

        # Display richest user in discord server
        guardian_with_gems_sorted = sorted(guardian_with_gems)[::-1]
        guardian_with_gems = guardian_with_gems_sorted[:10]
        counter = 1
        for whales in guardian_with_gems:
            if counter == 1:
                output = output + f"{counter}. {whales[0]:,d} 💎 - `{whales[1]}`"
            else:
                output = (
                    output + f"\n{counter}. {whales[0]:,d} 💎 - `{whales[1]}`"
                )

            # Get username if any
            username = db_ailie.get_username(whales[2])
            if username is not None:
                output = output + f" a.k.a. `{username}`"

            counter += 1

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name=ctx.me.name, icon_url=ctx.me.avatar_url)
        embed.add_field(name=f"Whales in {logical_whereabouts}!", value=output)

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="gems",
        brief="Check gems.",
        description="Check the amount of your current gems statistics.",
    )
    async def gems(self, ctx, mention: discord.Member = None):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        # Check if person mentioned is initialized
        if mention:
            if not db_ailie.is_initialized(mention.id):
                await ctx.send(f"{mention.mention} is not initialized yet!")
                db_ailie.disconnect()
                return

        if mention is None:
            guardian_id = ctx.author.id
            guardian_name = ctx.author.name
            guardian_avatar = ctx.author.avatar_url
        else:
            guardian_id = mention.id
            guardian_name = mention.name
            guardian_avatar = mention.avatar_url

        # Display gems balance
        gems = db_ailie.get_gems(guardian_id)
        gems_gambled = db_ailie.get_gambled_gems(guardian_id)
        gems_spent = db_ailie.get_spent_gems(guardian_id)
        gems_gained = db_ailie.get_gained_gems(guardian_id)
        db_ailie.disconnect()
        embed = discord.Embed(
            description=(
                f"**Current Gems**: `{gems}`"
                + f"\n**Gems Spent**: `{gems_spent}`"
                + f"\n**Gems Gambled**: `{gems_gambled}`"
                + f"\n**Overall Gems Gained**: `{gems_gained}`"
            ),
            color=discord.Color.purple()
        )
        embed.set_author(
            name=f"{guardian_name}'s Gems", icon_url=guardian_avatar)
        await ctx.send(embed=embed)

    @commands.command(
        name="hourly",
        brief="Hourly gems.",
        description="Claim hourly gems.",
    )
    async def hourly(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        qualified_hourly = db_ailie.get_hourly_qualification(ctx.author.id)

        if qualified_hourly:
            gems = 500
            db_ailie.store_gems(ctx.author.id, gems)
            db_ailie.update_user_exp(ctx.author.id, 5)
            await ctx.send(
                f"Hourly gems claimed. You obtained {gems:,d} 💎, "
                + f"<@{ctx.author.id}>!"
            )
        else:
            cd = db_ailie.get_hourly_cooldown(ctx.author.id)
            await ctx.send(
                f"One can be so greedy, <@{ctx.author.id}>. "
                + f"{cd} left before reset."
            )

    @commands.command(
        name="daily",
        brief="Daily gems.",
        description="Claim daily gems.",
    )
    async def daily(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        qualified_daily = db_ailie.get_daily_qualification(ctx.author.id)

        if qualified_daily:
            count = db_ailie.get_daily_count(ctx.author.id)
            gems = 2500 + (200 * count)
            db_ailie.store_gems(ctx.author.id, gems)
            db_ailie.update_user_exp(ctx.author.id, 5)
            await ctx.send(
                f"Daily gems claimed for {count} time(s). "
                + f"You obtained {gems:,d} 💎, <@{ctx.author.id}>!"
            )
        else:
            cd = db_ailie.get_daily_cooldown(ctx.author.id)
            await ctx.send(
                f"One can be so greedy, <@{ctx.author.id}>. "
                + f"{cd} left before reset."
            )


def setup(bot):
    bot.add_cog(Currency(bot))
