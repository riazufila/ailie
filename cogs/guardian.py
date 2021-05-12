#!/usr/bin/env python

import discord
from discord.ext import commands
from helpers.database import Database


class Guardian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def heroStatsLevel(self, stats, hero_level, user_level):
        # Increase overall stats
        for stat in stats:
            if stat in ["attack", "hp", "def"]:
                stats[stat] = round(
                    stats[stat]
                    + (stats[stat] * (((hero_level - 1) / 100) * 2))
                    + (stats[stat] * (((user_level - 1) / 100) * 2))
                )

        return stats

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
        name="profile",
        brief="View profile.",
        description="View profile of yourself or someone else's.",
        aliases=["prof"],
    )
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
            guardian_id = ctx.author.id
            guardian_name = ctx.author.name
            guardian_avatar = ctx.author.avatar_url
        else:
            guardian_id = mention.id
            guardian_name = mention.name
            guardian_avatar = mention.avatar_url

        # Get all information needed for a profile show off
        username, guild_name, position, gems = db_ailie.get_guardian_info(
            guardian_id
        )
        trophies = db_ailie.get_trophy(guardian_id)
        guild_id = db_ailie.get_guild_id_of_member(guardian_id)
        heroes_obtained = db_ailie.hero_inventory(guardian_id)
        equips_obtained = db_ailie.equip_inventory(guardian_id)
        user_exp = db_ailie.get_user_exp(guardian_id)
        user_level = db_ailie.get_user_level(guardian_id)
        summon_count = db_ailie.get_summon_count(guardian_id)

        # Set embed baseline
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(
            name=f"Lvl {user_level} {guardian_name}'s Profile",
            icon_url=guardian_avatar
        )

        # Username, gems, and trophies
        embed.add_field(name="Username 📝", value=f"`{username}`", inline=False)
        embed.add_field(name="User EXP 💪", value=f"`{user_exp}`", inline=False)
        embed.add_field(name="Gems 💎", value=f"`{gems:,d}`")
        embed.add_field(name="Trophies 🏆", value=f"`{trophies:,d}`")

        # Total unique and epic exclusive
        heroes_equips_count = (
            "**Summon Count**: "
            + f"`{summon_count}`"
            + "\n**Unique Heroes**: "
            + f"`{len(heroes_obtained[len(heroes_obtained) - 1])}`"
            + "\n**Epic Exclusive Equipments**: "
            + f"`{len(equips_obtained[len(equips_obtained) - 1])}`"
        )
        embed.add_field(
            name="Summons⚔️",
            value=heroes_equips_count,
            inline=False
        )

        # Guild details
        guild_detail = (
            f"**Guild Name**: `{guild_name}`"
            + f"\n**Guild ID**: `{guild_id}`"
            + f"\n**Position**: `{position}`"
        )
        embed.add_field(
            name="Guild Details 🏠",
            value=guild_detail,
            inline=False,
        )

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="inventory",
        brief="View inventory.",
        description=(
            "Open inventory to check what you have collected so far."
            + "`type` can be either `hero` or `equip`. "
            + "Mention is optional as it can be used to view "
            + "others' inventories instead."
        ),
        aliases=["inv", "bag"],
    )
    async def inventory(
            self, ctx, type, *target):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        guardian_id = ctx.author.id
        guardian_name = ctx.author.name
        guardian_avatar = ctx.author.avatar_url
        inventory = []
        header = ""
        exists = False
        hero_name = ""
        hero_acquired = {}
        hero_stats = hero_buffs = hero_skill = hero_on_hit = hero_on_normal = {}

        if target:
            target = " ".join(target)
            if len(target) < 4:
                await ctx.send(
                    f"Yo, <@{ctx.author.id}>. "
                    + "At least put 4 characters please?"
                )
                db_ailie.disconnect()
                return

        # Determine inventory to check
        if type.lower() in ["heroes", "hero", "h"] and not target:
            inventory = db_ailie.hero_inventory(guardian_id)
            if len(inventory[len(inventory) - 1]) > 1:
                header = "Unique Heroes"
            else:
                header = "Unique Hero"
        elif (
            type.lower()
            in [
                "equipments",
                "equipment",
                "equips",
                "equip",
                "e",
            ]
            and not target
        ):
            inventory = db_ailie.equip_inventory(guardian_id)
            if len(inventory[len(inventory) - 1]) > 1:
                header = "Epic Exclusive Equipments"
            else:
                header = "Epic Exclusive Equipment"
        elif type in ["heroes", "hero", "h"] and target:
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

                inventory_id = db_ailie.get_inventory_id(guardian_id)
                if db_ailie.is_hero_obtained(guardian_id, hero_id):
                    user_level = db_ailie.get_user_level(guardian_id)
                    hero_acquired = db_ailie.get_hero_acquired_details(
                        inventory_id, hero_id
                    )
                    hero_stats = self.heroStatsLevel(
                        hero_stats, hero_acquired["level"], user_level
                    )
                else:
                    exists = False
        elif type in ["equipments", "equips", "equip", "eq", "e"]:
            await ctx.send(
                f"Sorry, <@{ctx.author.id}>. Further information on equipments "
                + "are still under maintenance."
            )
            return
        else:
            await ctx.send(
                "There's only inventories for heroes and equipments, "
                + f"<@{ctx.author.id}>."
            )
            db_ailie.disconnect()
            return

        if not target:
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                name=guardian_name + "'s Inventory",
                icon_url=guardian_avatar,
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
        elif target and exists:
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                icon_url=self.bot.user.avatar_url,
                name=f"Lvl {hero_acquired['level']} {hero_name}",
            )
            embed.add_field(name="Hero EXP 💪", value=f"`{hero_acquired['exp']}`")

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
            await ctx.send("You don't own the target you stated.")

        db_ailie.disconnect()

    @commands.command(
        name="username",
        brief="Set username.",
        description=(
            "Set username that you use in-game or not. "
            + "This is optional. If you set it, you'll see the "
            + "username you set in some commands."
        ),
        aliases=["name", "ign"],
    )
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
        name="limitbreak",
        brief="Limit breaks a hero to extend the level cap.",
        description=(
            "Extends the capability of an already overly powerful hero "
            + "by increasing its level cap."
        ),
    )
    async def limitBreak(self, ctx, *target):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        proceed = False
        target = " ".join(target)

        # Check if target is obtained
        hero_name = db_ailie.get_hero_full_name(target)

        if hero_name and target:
            hero_id = db_ailie.get_hero_id(hero_name)
            obtained = db_ailie.is_hero_obtained(ctx.author.id, hero_id)

            if obtained:
                current_lb = db_ailie.get_hero_limit_break(
                    ctx.author.id, hero_name)
                required_gems = (current_lb + 1) * 50000
                current_gems = db_ailie.get_gems(ctx.author.id)

                if current_gems > required_gems:
                    proceed = True
                else:
                    await ctx.send(
                        f"<@{ctx.author.id}>, you only "
                        + f"have `{current_gems:,d}` "
                        + f"💎 and you need `{required_gems:,d}` 💎 to limit "
                        + f"break **{hero_name}** from `{current_lb}` to "
                        + f"`{current_lb + 1}`."
                    )
                    db_ailie.disconnect()
                    return
            else:
                await ctx.send(f"<@{ctx.author.id}>, you don't have that hero.")
                db_ailie.disconnect()
                return
        else:
            await ctx.send(f"<@{ctx.author.id}>, what hero is that?")
            db_ailie.disconnect()
            return

        if proceed:
            # Get confirmation
            await ctx.send(
                    f"<@{ctx.author.id}>, confirm to limit break "
                    + f"**{hero_name}** from `{current_lb}` "
                    + f"to `{current_lb + 1}` for "
                    + f"`{required_gems:,d}` 💎?"
            )

            # Function to confirm request
            def confirm_request(message):
                return (
                    message.author.id == ctx.author.id
                    and message.content.upper() in ["YES", "Y", "NO", "N"]
                )

            # Wait for confirmation
            try:
                msg = await self.bot.wait_for(
                    "message", check=confirm_request, timeout=30
                )

                # Request confirmed
                if msg.content.upper() in ["YES", "Y"]:
                    inventory_id = db_ailie.get_inventory_id(ctx.author.id)
                    db_ailie.increase_limit_break_hero(
                        inventory_id, hero_id, current_lb)
                    await ctx.send(
                            f"Congratulations, <@{ctx.author.id}>! "
                            + f"Your **{hero_name}**'s current limit "
                            + f"break is now `{current_lb + 1}`."
                    )
                # Change of mind
                else:
                    await ctx.send(
                        f"Maybe next time, <@{ctx.author.id}>.."
                    )
            except Exception:
                await ctx.send(
                    f"I guess you're away already, <@{ctx.author.id}>."
                )

    @commands.command(
        name="initialize",
        brief="Initialize user.",
        description=(
            "This command needs to be issued before most of the other commands "
            + "can be used. Think of it as a registration process."
        ),
        aliases=["init"],
    )
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
