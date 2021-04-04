#!/usr/bin/env python

import discord
from discord.ext import commands
from helpers.database import Database


class Guardian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile", help="View profile.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        username, guild_name, position, gems = db_ailie.get_guardian_info(
            ctx.author.id
        )
        guild_id = db_ailie.get_guild_id_of_member(ctx.author.id)

        output = (
            f"**Username**: `{username}`"
            + f"\n**Gems**: `{gems}` 💎"
            + f"\n**Guild**: `{guild_name}`#`{guild_id}`"
            + f"\n**Position**: `{position}`"
        )

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Guardian's Profile", value=output)

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="inventory", help="View profile.", aliases=["inv", "i"]
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

    @commands.command(name="username", help="Set username.")
    @commands.cooldown(1, 60, commands.BucketType.user)
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

    @commands.command(name="initialize", help="Initialize user.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def initialize(self, ctx):
        db_ailie = Database()

        if db_ailie.initialize_user(ctx.author.id):
            await ctx.send(
                "You can now use the other commands, "
                + f"<@{ctx.author.id}>. Have fun!"
            )
        else:
            await ctx.send(
                f"You are already initialized, <@{ctx.author.id}>. Have fun!"
            )


def setup(bot):
    bot.add_cog(Guardian(bot))
