#!/usr/bin/env python

import discord
from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Guardian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile", help="View profile.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send("Do `ailie;initialize` or `a;initialize` first before anything!")
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

    @commands.command(name="inventory", help="View profile.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def inventory(self, ctx, type, grade):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send("Do `ailie;initialize` or `a;initialize` first before anything!")
            db_ailie.disconnect()
            return
        
        if type.lower() in ["heroes", "hero", "h"]:
            hero_inventory = db_ailie.hero_inventory(ctx.author.id)

            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(name=ctx.author.name + "'s Inventory", icon_url=ctx.author.avatar_url)

            if grade.lower() in ["unique", "u"]:
                embed.add_field(name="Unique Heroes", value="\n".join(hero_inventory[2]), inline=False)
            elif grade.lower() in ["rare", "r"]:
                embed.add_field(name="Rare Heroes", value="\n".join(hero_inventory[1]), inline=False)
            elif grade.lower() in ["normal", "n"]:
                embed.add_field(name="Normal Heroes", value="\n".join(hero_inventory[0]), inline=False)
            else:
                db_ailie.disconnect()
                return

            await ctx.send(embed=embed)
        elif type.lower() in ["equipments", "equipment", "equips", "equip", "e"]:
            await ctx.send(f"Sorry, <@{ctx.author.id}>. Equipments is still being maintained.")
        else:
            await ctx.send(f"<@{ctx.author.id}>, that is not a valid option.")

        db_ailie.disconnect()

    @commands.command(name="username", help="Set username.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def username(self, ctx, username):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send("Do `ailie;initialize` or `a;initialize` first before anything!")
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
        db_ailie = DatabaseAilie()

        if db_ailie.initialize_user(ctx.author.id):
            await ctx.send(
                f"You can now use the other commands, <@{ctx.author.id}>. Have fun!"
            )
        else:
            await ctx.send(
                f"You are already initialized, <@{ctx.author.id}>. Have fun!"
            )


def setup(bot):
    bot.add_cog(Guardian(bot))
