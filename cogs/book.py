#!/usr/bin/env python

import discord
from discord.ext import commands
from helpers.database import Database


class Book(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def translateToReadableFormat(self, non_readable_format):
        buffer_for_res = non_readable_format[::-1]
        if buffer_for_res[3:4] == "_":
            buffer_list = []
            split = non_readable_format.split("_")

            for s in split:
                if s == "res":
                    buffer_list.append("Resistance")
                else:
                    buffer_list.append(s.capitalize())

            readable_format = " ".join(buffer_list)
        elif non_readable_format[6:7] == "_":
            buffer_list = []
            split = non_readable_format.split("_")

            for s in split:
                buffer_list.append(s.capitalize())

            readable_format = " ".join(buffer_list)
        elif non_readable_format.lower() in ["wsrs", "dr", "hp", "cc", "aoe"]:
            readable_format = non_readable_format.upper()
        else:
            readable_format = non_readable_format.capitalize()

        return readable_format

    @commands.command(
        name="book",
        brief="Open book of everything.",
        description=(
            "Use the book to check information of heroes and equipments. "
            + "`type` can be either `hero` or `equip`. "
            + "Target can be any heroes or equipments."
        ),
    )
    async def book(self, ctx, type, *target):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if target:
            target = " ".join(target)
            exists = False
            hero_name = ""
            hero_stats = (
                hero_buffs
            ) = hero_skill = hero_on_hit = hero_on_normal = {}
        else:
            await ctx.send("No hero or equipment mentioned.")
            db_ailie.disconnect()
            return

        if type in ["heroes", "hero", "h"]:
            exists = True
            hero_name = db_ailie.get_hero_full_name(target)

            if not hero_name:
                exists = False
            else:
                hero_id = db_ailie.get_hero_id(hero_name)
                (
                    hero_stats,
                    hero_buffs,
                    hero_skill,
                    hero_triggers,
                ) = db_ailie.get_hero_stats(hero_id)

                for trigger in hero_triggers:
                    if trigger == "on_hit":
                        hero_on_hit = hero_triggers[trigger]
                    else:
                        hero_on_normal = hero_triggers[trigger]

        elif type in ["equipments", "equips", "equip", "eq", "e"]:
            await ctx.send(
                f"Sorry, <@{ctx.author.id}>. Book on equipments are "
                + "still under maintenance."
            )
            return
        else:
            await ctx.send("Please specify the type as hero or equipment.")
            return

        if exists:
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                icon_url=self.bot.user.avatar_url, name=f"Lvl 1 {hero_name}"
            )

            # Set output
            for info in [
                hero_stats,
                hero_buffs,
                hero_skill,
                hero_on_hit,
                hero_on_normal,
            ]:
                information = ""
                info_title = ""
                for i in info:
                    all = False
                    party = ""

                    if info == hero_stats:
                        info_title = "Stats 📋"
                    elif info == hero_buffs:
                        info_title = "Buffs ✨"
                    elif info == hero_skill:
                        info_title = "Chain Skill 🔗"
                    elif info == hero_on_hit:
                        info_title = "On Hit 🛡️"
                    else:
                        info_title = "On Attack ⚔️"

                    if i.startswith("all"):
                        buffer = i[4:]
                        all = True
                    else:
                        buffer = i

                    info_proper = self.translateToReadableFormat(buffer)

                    if all:
                        party = " (Party)"

                    if information == "":
                        information = f"\n**{info_proper}**: `{info[i]}`{party}"
                    else:
                        information = (
                            information
                            + f"\n**{info_proper}**: `{info[i]}`{party}"
                        )

                if information:
                    embed.add_field(
                        name=info_title, value=information, inline=False
                    )

            await ctx.send(embed=embed)
        else:
            await ctx.send("The target you asked for does not exist.")


def setup(bot):
    bot.add_cog(Book(bot))
