#!/usr/bin/env python

import math
import discord
from discord.ext import commands
from helpers.database import Database


class Guardian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def statsLevel(self, stats, hero_level, user_level):
        # Increase overall stats
        for stat in stats:
            if stat in ["attack"]:
                increase = 10
                stats[stat] = round(
                    stats[stat]
                    + ((increase/100) * stats[stat] * (hero_level - 1))
                    + ((increase/100) * stats[stat] * (user_level - 1))
                )
            elif stat in ["hp"]:
                increase = 5
                stats[stat] = round(
                    stats[stat]
                    + ((increase/100) * stats[stat] * (hero_level - 1))
                    + ((increase/100) * stats[stat] * (user_level - 1))
                )
            elif stat in ["def"]:
                increase = 2
                stats[stat] = round(
                    stats[stat]
                    + ((increase/100) * stats[stat] * (hero_level - 1))
                    + ((increase/100) * stats[stat] * (user_level - 1))
                )
            else:
                pass

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
        aliases=["pr", "prof"],
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
        embed.add_field(
            name="User EXP 💪", value=f"`{user_exp:,d}`", inline=False)
        embed.add_field(name="Gems 💎", value=f"`{gems:,d}`")
        embed.add_field(name="Trophies 🏆", value=f"`{trophies:,d}`")

        # Total unique and epic exclusive
        heroes_equips_count = (
            "**Summon Count**: "
            + f"`{summon_count:,d}`"
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
            + "`target` is optional as it can be used to view "
            + "your specific hero statistics."
        ),
        aliases=["inv"],
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
        in_bag = False
        full_name = ""
        acquired = {}
        stats = buffs = skill = on_hit = on_normal \
            = on_normal_instant = on_hit_instant = {}

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
            type = "Hero"
            exists = True
            full_name = db_ailie.get_hero_full_name(target)

            if not full_name:
                exists = False
            else:
                hero_id = db_ailie.get_hero_id(full_name)
                (
                    stats,
                    buffs,
                    skill,
                    triggers,
                ) = db_ailie.get_hero_stats(hero_id)

                for trigger in triggers:
                    if trigger == "on_hit":
                        on_hit = triggers[trigger]
                    else:
                        on_normal = triggers[trigger]

                inventory_id = db_ailie.get_inventory_id(guardian_id)
                if db_ailie.is_hero_obtained(guardian_id, hero_id):
                    user_level = db_ailie.get_user_level(guardian_id)
                    acquired = db_ailie.get_hero_acquired_details(
                        inventory_id, hero_id
                    )
                    stats = self.statsLevel(
                        stats, acquired["level"], user_level
                    )
                    in_bag = True
                else:
                    in_bag = False
        elif type in ["equipments", "equips", "equip", "eq", "e"] and target:
            type = "Equip"
            exists = True
            full_name = db_ailie.get_equip_full_name(target)

            if not full_name:
                exists = False
            else:
                equip_id = db_ailie.get_equip_id(full_name)
                (
                    stats,
                    buffs,
                    skill,
                    triggers,
                    instant_triggers
                ) = db_ailie.get_equip_stats(equip_id)

                for trigger in triggers:
                    if trigger == "on_hit":
                        on_hit = triggers[trigger]
                    else:
                        on_normal = triggers[trigger]

                for instant_trigger in instant_triggers:
                    if instant_trigger == "on_hit":
                        on_hit_instant = instant_triggers[instant_trigger]
                    else:
                        on_normal_instant = instant_triggers[instant_trigger]

                inventory_id = db_ailie.get_inventory_id(guardian_id)
                if db_ailie.is_equip_obtained(guardian_id, equip_id):
                    acquired = db_ailie.get_equip_acquired_details(
                        inventory_id, equip_id
                    )
                    stats = self.statsLevel(
                        stats, acquired["level"], 0
                    )
                    in_bag = True
                else:
                    in_bag = False
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
        elif target and in_bag:
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                icon_url=self.bot.user.avatar_url,
                name=f"Lvl {acquired['level']} {full_name}",
            )
            embed.add_field(
                name=f"{type} EXP 💪",
                value=f"`{acquired['exp']:,d}`"
            )

            # Set output
            for info in [
                stats,
                buffs,
                skill,
                on_hit,
                on_normal,
                on_hit_instant,
                on_normal_instant
            ]:
                information = ""
                info_title = ""
                for i in info:
                    all = False
                    party = ""

                    if info == stats:
                        info_title = "Stats 📋"
                    elif info == buffs:
                        info_title = "Buffs ✨"
                    elif info == skill:
                        info_title = "Chain Skill 🔗"
                    elif info == on_hit:
                        info_title = "On Hit 🛡️"
                    elif info == on_normal:
                        info_title = "On Attack ⚔️"
                    elif info == on_hit_instant:
                        info_title = "On Hit Instant 🛡️⚡"
                    else:
                        info_title = "On Attack Instant ⚔️⚡"

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
        elif not exists:
            await ctx.send("The target you stated doesn't exist.")
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
        brief="Limit breaks a hero or equipment to extend the level cap.",
        description=(
            "Extends the capability of an already overly powerful hero "
            + "or equipment by increasing its level cap. `type` "
            + "can be either `hero` or `equip`. `target` is the hero "
            + "or equipment to limit break."
        ),
        aliases=["li", "lb"]
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def limitBreak(self, ctx, type, *target):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        exists = True
        obtained = True
        max_lb = 10
        target_id = None

        if not target:
            await ctx.send("Please specify a hero or equipment.")
            return

        target = " ".join(target)

        if len(target) < 4:
            await ctx.send(
                f"Yo, <@{ctx.author.id}>. "
                + "At least put 4 characters please?"
            )
            db_ailie.disconnect()
            return

        if type.lower() in ["heroes", "hero", "h"]:
            type = "hero"
            target_name = db_ailie.get_hero_full_name(target)
            if not target_name:
                exists = False
            else:
                target_id = db_ailie.get_hero_id(target_name)
                obtained = db_ailie.is_hero_obtained(ctx.author.id, target_id)
        elif type.lower() in \
                ["equipments", "equipment", "equips", "equip", "eq", "e"]:
            type = "equip"
            target_name = db_ailie.get_equip_full_name(target)
            if not target_name:
                exists = False
            else:
                target_id = db_ailie.get_equip_id(target_name)
                obtained = db_ailie.is_equip_obtained(ctx.author.id, target_id)
        else:
            await ctx.send("Only heroes and equipments can be limit broken.")
            return

        if not exists:
            await ctx.send("The target you specified does not exist!")
            return

        if not obtained:
            await ctx.send("You don't have the target you specified!")
            return
        else:
            if type == "hero":
                current_lb = db_ailie.get_hero_limit_break(
                    ctx.author.id, target_name)
            else:
                current_lb = db_ailie.get_equip_limit_break(
                    ctx.author.id, target_name)

            if current_lb >= max_lb:
                await ctx.send("You can't limit break that beast anymore.")
                return

            required_gems = (current_lb + 1) * 50000
            current_gems = db_ailie.get_gems(ctx.author.id)

            if current_gems < required_gems:
                await ctx.send(
                    f"<@{ctx.author.id}>, you only "
                    + f"have `{current_gems:,d}` "
                    + f"gems and you need `{required_gems:,d}` 💎 to limit "
                    + f"break **{target_name}** from `{current_lb}` to "
                    + f"`{current_lb + 1}`."
                )
                db_ailie.disconnect()
                return

        # Get confirmation
        await ctx.send(
                f"<@{ctx.author.id}>, confirm to limit break "
                + f"**{target_name}** from `{current_lb}` "
                + f"to `{current_lb + 1}` for "
                + f"`{required_gems:,d}` gems. `Y` or `N`?"
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
                db_ailie.spend_gems(ctx.author.id, required_gems)
                if type == "hero":
                    db_ailie.increase_limit_break_hero(
                        inventory_id, target_id, current_lb)
                else:
                    db_ailie.increase_limit_break_equip(
                        inventory_id, target_id, current_lb)

                await ctx.send(
                        f"Congratulations, <@{ctx.author.id}>! "
                        + f"Your **{target_name}**'s current limit "
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
        name="enhance",
        brief="Enhance equipments.",
        description=(
            "Enhance equipments for EXP. `level_increase` is "
            + "the amount of level increase that is aim on "
            + "the equipment. `equipment` is the equipment "
            + "to be enhanced."
        ),
        aliases=["en"],
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @commands.is_owner()
    async def enhance(self, ctx, level_increase: int, *equipment):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if level_increase <= 0:
            await ctx.send(f"Are you insane, <@{ctx.author.id}>?")
            db_ailie.disconnect()
            return

        if not equipment:
            await ctx.send("You need to specify an equipment to enhance.")
            db_ailie.disconnect()
            return

        equipment = " ".join(equipment)

        if len(equipment) < 4:
            await ctx.send(
                f"Yo, <@{ctx.author.id}>. "
                + "At least put 4 characters please?"
            )
            db_ailie.disconnect()
            return

        equip_full_name = db_ailie.get_equip_full_name(equipment)

        if not equip_full_name:
            await ctx.send("No such equipment exists.")
            db_ailie.disconnect()
            return

        equip_id = db_ailie.get_equip_id(equip_full_name)

        if not db_ailie.is_equip_obtained(ctx.author.id, equip_id):
            await ctx.send(f"You dont have that equipment, <@{ctx.author.id}>!")
            db_ailie.disconnect()
            return

        exp_to_increase = level_increase * 100

        inventory_id = db_ailie.get_inventory_id(ctx.author.id)
        acquired = db_ailie.get_equip_acquired_details(inventory_id, equip_id)

        current_level = acquired["level"]
        current_exp = acquired["exp"]
        lb = acquired["limit_break"]

        level = math.trunc((current_exp / 100) + 1)
        max_level = ((4900 * (lb + 1)) / 100) + (lb + 1)

        if level > max_level:
            await ctx.send(
                f"You can't increase that much, <@{ctx.author.id}>. "
                + f"Your max level for that equipment is {max_level}."
            )
            db_ailie.disconnect()
            return

        gems_required = level_increase * 2700
        current_gems = db_ailie.get_gems(ctx.author.id)

        if gems_required > current_gems:
            await ctx.send(
                f"Oof, poor guys <@{ctx.author.id}>.. "
                + f"You need {gems_required:,d} gems "
                + f"and you only have {current_gems:,d} gems. Sad life."
            )
            db_ailie.disconnect()
            return

        # Get confirmation
        await ctx.send(
                f"<@{ctx.author.id}>, confirm to enhance "
                + f"**{equip_full_name}** from `{current_level}` "
                + f"to `{current_level + level_increase}` for "
                + f"`{gems_required:,d}` gems. `Y` or `N`?"
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
                db_ailie.spend_gems(ctx.author.id, gems_required)
                print(exp_to_increase)
                db_ailie.update_equip_exp(ctx.author.id, equip_full_name, exp_to_increase)

                await ctx.send(
                        f"Congratulations, <@{ctx.author.id}>! "
                        + f"Your **{equip_full_name}**'s current level "
                        + f"is now `{current_level + level_increase}`."
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
        aliases=["ini"],
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
