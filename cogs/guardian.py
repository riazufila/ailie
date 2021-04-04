#!/usr/bin/env python

import discord
from discord.ext import commands
from helpers.database import Database


class Guardian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="profile", help="View profile.", aliases=["prof", "pro", "pr"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, mention: discord.Member = None):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
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
            guardian = ctx.author.id
        else:
            guardian = mention.id

        # Get all information needed for a profile show off
        username, guild_name, position, gems = db_ailie.get_guardian_info(
            guardian
        )
        guild_id = db_ailie.get_guild_id_of_member(guardian)
        heroes_obtained = db_ailie.hero_inventory(guardian)
        equips_obtained = db_ailie.equip_inventory(guardian)

        # Set embed baseline
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(
            name=f"{ctx.author.name}'s Profile", icon_url=ctx.author.avatar_url
        )

        # Username and gems
        embed.add_field(name="Username 📝", value=username)
        embed.add_field(name="Gems 💎", value=gems)

        # Total unique and epic exclusive
        heroes_equips_count = (
            f"Unique Heroes: {len(heroes_obtained[len(heroes_obtained) - 1])}"
            + f"\nEpic Exclusive Equips: {len(equips_obtained[len(equips_obtained) - 1])}"
        )
        embed.add_field(
            name="Unit Counts 🗡️", value=heroes_equips_count, inline=False
        )

        # Guild details
        guild_detail = (
            f"Guild Name: {guild_name}"
            + f"\nGuild ID: {guild_id}"
            + f"\nPosition: {position}"
        )
        embed.add_field(
            name="Guild Details 🏠",
            value=guild_detail,
            inline=False,
        )

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="inventory", help="View inventory.", aliases=["inv", "i"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def inventory(self, ctx, type):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Determine inventory to check
        if type.lower() in ["heroes", "hero", "h"]:
            inventory = db_ailie.hero_inventory(ctx.author.id)
            if len(inventory[len(inventory) - 1]) > 1:
                header = "Heroes"
            else:
                header = "Hero"
        elif type.lower() in [
            "equipments",
            "equipment",
            "equips",
            "equip",
            "e",
        ]:
            inventory = db_ailie.equip_inventory(ctx.author.id)
            if len(inventory[len(inventory) - 1]) > 1:
                header = "Equipments"
            else:
                header = "Equipment"
        else:
            await ctx.send(
                "There's only inventories for heroes and equipments, "
                + f"<@{ctx.author.id}>."
            )
            db_ailie.disconnect()
            return

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(
            name=ctx.author.name + "'s Inventory",
            icon_url=ctx.author.avatar_url,
        )
        if len(inventory[len(inventory) - 1]) == 0:
            data = "None"
        else:
            data = "\n".join(inventory[len(inventory) - 1])

        embed.add_field(
            name=header,
            value=data,
            inline=False,
        )
        await ctx.send(embed=embed)

        db_ailie.disconnect()

    @commands.command(name="username", help="Set username.", aliases=["name"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def username(self, ctx, username):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        db_ailie.set_username(ctx.author.id, username)
        await ctx.send(
            f"Your username is now, {username}. Enjoy, <@{ctx.author.id}>."
        )

        db_ailie.disconnect()

    @commands.command(
        name="initialize", help="Initialize user.", aliases=["init"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def initialize(self, ctx):
        db_ailie = Database()

        if db_ailie.initialize_user(ctx.author.id):
            await ctx.send(
                "You can now use the other commands, "
                + f"<@{ctx.author.id}>. Have fun!"
            )
        else:
            await ctx.send(
                f"You are already initialized, <@{ctx.author.id}>. "
                + "No need to initialize for the second time. Have fun!"
            )


def setup(bot):
    bot.add_cog(Guardian(bot))
