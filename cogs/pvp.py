#!/usr/bin/env python

import os
import asyncio
import random
import discord
from discord.ext import commands
from helpers.database import Database


class PvP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def calcWeapSkillCooldown(self, current_cd, wsrs, over=None):
        if over == "over":
            new_cd = round(current_cd * ((100 + wsrs) / 100))
        else:
            new_cd = round(current_cd * (100 / (100 + wsrs)))

        return new_cd

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
        elif non_readable_format.lower() in ["wsrs", "dr", "hp", "cc", 'aoe']:
            readable_format = non_readable_format.upper()
        else:
            readable_format = non_readable_format.capitalize()

        return readable_format

    async def onNormal(self, ctx, participants, enemy_counter):
        # Get hero counter
        if enemy_counter == 1:
            hero_counter = 0
        else:
            hero_counter = 1

        hero_on_trigger_cd = \
            participants[hero_counter]["current_state"]["on_normal_skill_cd"]
        hero_triggers = \
            participants[hero_counter]["hero_triggers"]["on_normal"]
        hero_color = participants[hero_counter]["color"]
        hero_hero_name = participants[hero_counter]["hero_name"]
        hero_stats = participants[hero_counter]["hero_stats"]
        hero_multipliers = participants[hero_counter]["multipliers"]
        hero_debuffs = participants[hero_counter]["debuffs"]
        hero_max_hp = participants[hero_counter]["max_hp"]
        hero_ws_cd = \
            participants[hero_counter]["current_state"]["weapon_skill_cd"]
        hero_stunned = participants[hero_counter]["current_state"]["stunned"]

        color = participants[enemy_counter]["color"]
        hero_name = participants[enemy_counter]["hero_name"]
        stats = participants[enemy_counter]["hero_stats"]
        multipliers = participants[enemy_counter]["multipliers"]
        debuffs = participants[enemy_counter]["debuffs"]
        ws_cd = \
            participants[enemy_counter]["current_state"]["weapon_skill_cd"]

        not_enemy = {
            "stats": hero_stats,
            "multipliers": hero_multipliers,
            "debuffs": hero_debuffs,
            "ws_cd": hero_ws_cd
        }

        enemy = {
            "stats": stats,
            "multipliers": multipliers,
            "debuffs": debuffs,
            "ws_cd": ws_cd
        }

        if hero_on_trigger_cd == 0 and hero_stunned == 0:
            hero_on_trigger_cd = 5
            multipliers_buffer = {}
            debuffs_buffer = {}
            multi_debuff_check = False

            for on_normal_buff in hero_triggers:
                if on_normal_buff in ["all_heal", "heal"]:
                    hp_left = await self.heal(
                        ctx, hero_max_hp, hero_triggers,
                        hero_color, hero_hero_name, on_normal_buff,
                        hero_stats
                    )

                    # Update hero hp after heals
                    hero_stats["hp"] = hp_left
                elif on_normal_buff in ["all_cure", "cure"]:
                    debuffs = await self.cure(
                        ctx, hero_debuffs,
                        hero_color, hero_hero_name
                    )
                elif on_normal_buff.startswith("debuff"):
                    debuffs_buffer = await self.debuff(
                        ctx, on_normal_buff,
                        hero_triggers,
                        color,
                        hero_name
                    )

                    debuffs.append(debuffs_buffer)
                    multi_debuff_check = True
                else:
                    multipliers_buffer = await self.multiplier(
                        ctx, on_normal_buff,
                        hero_triggers,
                        hero_color,
                        hero_hero_name
                    )

                    hero_multipliers.append(multipliers_buffer)
                    multi_debuff_check = True

            # Update stats after multipliers and debuffs
            if multi_debuff_check:
                hero_stats, hero_multipliers, \
                    hero_debuffs, hero_ws_cd = \
                    self.updateStatsAfterMultiplierDebuff(
                        hero_stats,
                        hero_multipliers,
                        hero_debuffs,
                        hero_ws_cd
                    )
                stats, multipliers, debuffs, ws_cd = \
                    self.updateStatsAfterMultiplierDebuff(
                        stats,
                        multipliers,
                        debuffs,
                        ws_cd
                    )

            # Return enemy and not_enemy
            not_enemy = {
                "stats": hero_stats,
                "multipliers": hero_multipliers,
                "debuffs": hero_debuffs,
                "ws_cd": hero_ws_cd
            }

            enemy = {
                "stats": stats,
                "multipliers": multipliers,
                "debuffs": debuffs,
                "ws_cd": ws_cd
            }

        return enemy, not_enemy, hero_on_trigger_cd

    async def onHit(self, ctx, participants, enemy_counter):
        # Get hero counter
        if enemy_counter == 1:
            hero_counter = 0
        else:
            hero_counter = 1

        enemy_on_trigger_cd = \
            participants[enemy_counter]["current_state"]["on_hit_skill_cd"]
        enemy_triggers = \
            participants[enemy_counter]["hero_triggers"]["on_hit"]
        enemy_color = participants[enemy_counter]["color"]
        enemy_hero_name = participants[enemy_counter]["hero_name"]
        enemy_stats = participants[enemy_counter]["hero_stats"]
        enemy_multipliers = participants[enemy_counter]["multipliers"]
        enemy_debuffs = participants[enemy_counter]["debuffs"]
        enemy_max_hp = participants[enemy_counter]["max_hp"]
        enemy_ws_cd = \
            participants[enemy_counter]["current_state"]["weapon_skill_cd"]

        color = participants[hero_counter]["color"]
        hero_name = participants[hero_counter]["hero_name"]
        stats = participants[hero_counter]["hero_stats"]
        multipliers = participants[hero_counter]["multipliers"]
        debuffs = participants[hero_counter]["debuffs"]
        ws_cd = \
            participants[hero_counter]["current_state"]["weapon_skill_cd"]
        stunned = participants[hero_counter]["current_state"]["stunned"]

        enemy = {
            "stats": enemy_stats,
            "multipliers": enemy_multipliers,
            "debuffs": enemy_debuffs,
            "ws_cd": enemy_ws_cd
        }

        not_enemy = {
            "stats": stats,
            "multipliers": multipliers,
            "debuffs": debuffs,
            "ws_cd": ws_cd
        }

        if enemy_on_trigger_cd == 0 and stunned == 0:
            enemy_on_trigger_cd = 5
            multipliers_buffer = {}
            debuffs_buffer = {}
            multi_debuff_check = False

            for on_hit_buff in enemy_triggers:
                if on_hit_buff in ["all_heal", "heal"]:
                    hp_left = await self.heal(
                        ctx, enemy_max_hp, enemy_triggers,
                        enemy_color, enemy_hero_name, on_hit_buff,
                        enemy_stats
                    )

                    # Update hero hp after heals
                    enemy_stats["hp"] = hp_left
                elif on_hit_buff in ["all_cure", "cure"]:
                    debuffs = await self.cure(
                        ctx, enemy_debuffs,
                        enemy_color, enemy_hero_name
                    )
                elif on_hit_buff.startswith("debuff"):
                    debuffs_buffer = await self.debuff(
                        ctx, on_hit_buff,
                        enemy_triggers,
                        color,
                        hero_name
                    )

                    debuffs.append(debuffs_buffer)
                    multi_debuff_check = True
                else:
                    multipliers_buffer = await self.multiplier(
                        ctx, on_hit_buff,
                        enemy_triggers,
                        enemy_color,
                        enemy_hero_name
                    )

                    enemy_multipliers.append(multipliers_buffer)
                    multi_debuff_check = True

            # Update stats after multipliers and debuffs
            if multi_debuff_check:
                enemy_stats, enemy_multipliers, \
                    enemy_debuffs, enemy_ws_cd = \
                    self.updateStatsAfterMultiplierDebuff(
                        enemy_stats,
                        enemy_multipliers,
                        enemy_debuffs,
                        enemy_ws_cd
                    )
                stats, multipliers, debuffs, ws_cd = \
                    self.updateStatsAfterMultiplierDebuff(
                        stats,
                        multipliers,
                        debuffs,
                        ws_cd
                    )

            # Return enemy and not_enemy
            enemy = {
                "stats": enemy_stats,
                "multipliers": enemy_multipliers,
                "debuffs": enemy_debuffs,
                "ws_cd": enemy_ws_cd
            }

            not_enemy = {
                "stats": stats,
                "multipliers": multipliers,
                "debuffs": debuffs,
                "ws_cd": ws_cd
            }

        return enemy, not_enemy, enemy_on_trigger_cd

    def updateStatsAfterMultiplierDebuff(
            self, stats, multipliers, debuffs, ws_cd):
        buffers = [multipliers, debuffs][:]

        for buffer in buffers:
            for stats_buffer in buffer:
                if stats_buffer["count"] > 1 and not stats_buffer["check"]:
                    for stat_buffer in stats_buffer:
                        if stat_buffer not in ["count", "check"]:
                            if stat_buffer in ["attack", "hp", "def"]:
                                stats[stat_buffer] = round(
                                        stats[stat_buffer]
                                        * ((100 + stats_buffer[stat_buffer])
                                            / 100)
                                    )
                            else:
                                stats[stat_buffer] = \
                                    stats[stat_buffer] \
                                    + stats_buffer[stat_buffer]
                                # If wsrs, then calculate the new cd.
                                if stat_buffer == "wsrs":
                                    # Get new weapon skill CD
                                    ws_cd = self.calcWeapSkillCooldown(
                                            ws_cd,
                                            stats["wsrs"]
                                        )

                    stats_buffer["check"] = True
                elif stats_buffer["count"] == 1 and stats_buffer["check"]:
                    for stat_buffer in stats_buffer:
                        if stat_buffer not in ["count", "check"]:
                            if stat_buffer in ["attack", "hp", "def"]:
                                stats[stat_buffer] = round(
                                        stats[stat_buffer]
                                        * (100 /
                                            (100 + stats_buffer[stat_buffer]))
                                    )
                            else:
                                stats[stat_buffer] = \
                                    stats[stat_buffer] \
                                    - stats_buffer[stat_buffer]

                    buffer.remove(stats_buffer)
                else:
                    pass

        multipliers = buffers[0][:]
        debuffs = buffers[1][:]

        return stats, multipliers, debuffs, ws_cd

    async def multiplier(self, ctx, skill, skill_stats, color, hero_name):
        multipliers = self.resetMultiplier()
        if skill.startswith("all"):
            h = skill[4:]
        else:
            h = skill

        multipliers[h] = skill_stats[skill]

        h = self.translateToReadableFormat(h)

        await ctx.send(f"{color} **{hero_name}**'s {h} is buffed!")
        await asyncio.sleep(1)

        return multipliers

    async def debuff(
            self, ctx, skill, skill_stats,
            color, enemy_hero_name
            ):
        debuffs = self.resetDebuff()

        if skill.startswith("debuff"):
            d = skill[7:]
        else:
            d = skill

        debuffs[d] = -1 * skill_stats[skill]

        d = self.translateToReadableFormat(d)

        await ctx.send(
            f"{color} **{enemy_hero_name}**'s "
            + f"{d} is debuffed!"
        )
        await asyncio.sleep(1)

        return debuffs

    async def cure(self, ctx, debuffs, color, hero_name):
        if len(debuffs) > 0:
            for debuff in debuffs:
                debuff["count"] = 1

        await ctx.send(
            f"{color} **{hero_name}** is cured!"
        )
        await asyncio.sleep(1)

        return debuffs

    async def heal(
            self, ctx, max_hp, skill_stats, color, hero_name, skill, stats):
        # Calculate heals
        heal = round(max_hp * (skill_stats[skill] / 100))
        total_health = stats["hp"] + heal

        if total_health > max_hp:
            stats["hp"] = max_hp
        else:
            stats["hp"] = total_health

        await ctx.send(
            f"{color} `{heal:,d}` HP healed to "
            + f"**{hero_name}**.\n"
        )
        await asyncio.sleep(1)
        await ctx.send(
            f"{color} **{hero_name}** current HP is "
            + f"`{stats['hp']}`/`{max_hp}`"
        )
        await asyncio.sleep(1)

        return stats["hp"]

    async def weaponSkill(
                self, ctx, weapon_skill_cd, color, hero_name,
                enemy_stats, enemy_hero_name, stunned, enemy_stunned,
                wsrs
            ):
        attack_type = "used weapon skill"
        if stunned != 0:
            await ctx.send(f"{color} **{hero_name}** is stunned.")
            await asyncio.sleep(1)
        elif weapon_skill_cd != 0:
            await ctx.send(
                f"{color} "
                + f"**{hero_name}** weapon skill is still "
                + "on cooldown."
            )
            await asyncio.sleep(1)
        else:
            weapon_skill_cd = self.calcWeapSkillCooldown(5, wsrs)
            enemy_speed = enemy_stats[
                "speed"
            ]
            miss = random.choices(
                [True, False],
                [
                    enemy_speed,
                    (100 - enemy_speed),
                ],
                k=1,
            )[0]

            if miss:
                await ctx.send(f"{color} **{hero_name}** missed.")
                await asyncio.sleep(1)

            if not miss:
                enemy_stunned = 3
                await ctx.send(
                    f"{color} "
                    + f"**{hero_name}** {attack_type} and stunned"
                    + f" **{enemy_hero_name}"
                    + "** for 3 rounds!"
                )
                await asyncio.sleep(1)
        return enemy_stunned, weapon_skill_cd

    async def attack(
            self, ctx, stats, enemy_stats, enemy_color, enemy_hero_name,
            stunned, color, hero_name, attack_type, ori_hp, percent_damage
            ):
        end = False

        if stunned == 0:
            damage_type = "damage"

            damage = round(
                (stats["attack"] + (stats["attack"] * percent_damage / 100))
                * ((100 + stats[stats["element"]]) / 100)
            )

            crit = random.choices(
                [True, False],
                [stats["cc"], (100 - stats["cc"])],
                k=1,
            )[0]

            if crit:
                damage = damage * 2
                damage_type = "critical damage"

            total_damage = round(
                damage
                * (
                    100
                    / (
                        100
                        + enemy_stats["def"]
                        + enemy_stats[f"{stats['element']}_res"]
                    )
                )
                - enemy_stats["dr"]
            )

            enemy_speed = enemy_stats[
                "speed"
            ]

            miss = random.choices(
                [True, False],
                [
                    enemy_speed,
                    (100 - enemy_speed),
                ],
                k=1,
            )[0]

            if miss:
                await ctx.send(f"{color} **{hero_name}** missed.")
                await asyncio.sleep(1)

            if not miss:
                if total_damage < 0:
                    total_damage = 0

                enemy_stats["hp"] = (
                    enemy_stats["hp"]
                    - total_damage
                )

                await ctx.send(
                    f"{color} **{hero_name}** {attack_type} and "
                    + f"`dealt {total_damage:,d}` {damage_type}!"
                )
                await asyncio.sleep(1)

                if enemy_stats["hp"] < 0:
                    end = True
                    await ctx.send(
                        f"{enemy_color} "
                        + f"**{enemy_hero_name}"
                        + f"** has died! **{hero_name}** won!"
                    )
                    await asyncio.sleep(1)
                else:
                    await ctx.send(
                        f"{enemy_color} "
                        + f"**{enemy_hero_name}"
                        + "**'s HP reduced! "
                        + f"`{enemy_stats['hp']}"
                        + f"`/`{ori_hp}` HP left!"
                    )
                    await asyncio.sleep(1)
        else:
            await ctx.send(f"{color} **{hero_name}** is stunned.")
            await asyncio.sleep(1)

        return end, enemy_stats["hp"]

    async def displayHeroStats(
            self, ctx, stats, levels, name, avatar, hero, participants, p):
        # Set embed baseline
        if participants.index(p) == 1:
            color = discord.Color.blue()
            await ctx.send("**Opponent**:")
        else:
            color = discord.Color.red()
            await ctx.send("**Challenger**:")

        embed = discord.Embed(color=color)
        embed.set_author(name=name, icon_url=avatar)

        # Set output
        stats_output = ""
        for s in stats:
            if s.lower() in [
                    "attack", "def", "hp", "cc",
                    "dr", "wsrs", "element", "skill"
                    ]:
                stat_proper = self.translateToReadableFormat(s)
                if stats_output == "":
                    stats_output = f"\n**{stat_proper}**: `{stats[s]}`"
                else:
                    stats_output = stats_output \
                        + f"\n**{stat_proper}**: `{stats[s]}`"

        embed.add_field(
            name=f"Lvl {levels['level']} {hero}",
            value=stats_output
        )

        # Send embed
        await ctx.send(embed=embed)

    def heroStatsBuffs(self, stats, buffs):
        for stat in buffs:
            if stat.startswith("all"):
                s = stat[4:]
            else:
                s = stat

            stats[s] = stats[s] + buffs[stat]

        return stats

    def heroStatsLevels(self, stats, levels):
        for stat in stats:
            if stat in ["attack", "hp", "def"]:
                stats[stat] = stats[stat] * (levels["level"])

        return stats

    def resetCurrentState(self):
        return {
            "on_hit_by_any": False,
            "weapon_skill_cd": 5,
            "on_normal_skill_cd": 5,
            "on_hit_skill_cd": 5,
            "stunned": 0,
            "done_normal": False,
        }

    def resetMultiplier(self):
        return {
            "count": 3,
            "check": False,
            "attack": 0,
            "def": 0,
            "normal": 0,
            "basic": 0,
            "light": 0,
            "dark": 0,
            "fire": 0,
            "earth": 0,
            "water": 0,
        }

    def resetDebuff(self):
        return {
            "count": 3,
            "check": False,
            "attack": 0,
            "def": 0,
            "normal": 0,
            "basic_res": 0,
            "light_res": 0,
            "dark_res": 0,
            "fire_res": 0,
            "earth_res": 0,
            "water_res": 0,
        }

    def resetOtherStats(self, ori):
        modifications = {
            "water": 0,
            "fire": 0,
            "earth": 0,
            "light": 0,
            "basic": 0,
            "dark": 0,
            "wsrs": 0,
            "speed": 0,
            "skill": 0,
            "normal": 20
        }

        ori.update(modifications)

        return ori

    def assignElementStats(self, element, ori):
        modifications = {}

        if element.lower() == "light":
            modifications = {
                "water_res": 0,
                "fire_res": 0,
                "earth_res": 0,
                "light_res": 0,
                "basic_res": -30,
                "dark_res": 30
            }
        elif element.lower() == "dark":
            modifications = {
                "water_res": 0,
                "fire_res": 0,
                "earth_res": 0,
                "light_res": -30,
                "basic_res": 30,
                "dark_res": 0,
            }
        if element.lower() == "basic":
            modifications = {
                "water_res": 0,
                "fire_res": 0,
                "earth_res": 0,
                "light_res": 30,
                "basic_res": 0,
                "dark_res": -30
            }
        if element.lower() == "fire":
            modifications = {
                "water_res": -30,
                "fire_res": 0,
                "earth_res": 30,
                "light_res": 0,
                "basic_res": 0,
                "dark_res": 0
            }
        if element.lower() == "water":
            modifications = {
                "water_res": 0,
                "fire_res": 30,
                "earth_res": -30,
                "light_res": 0,
                "basic_res": 0,
                "dark_res": 0
            }
        if element.lower() == "earth":
            modifications = {
                "water_res": 30,
                "fire_res": -30,
                "earth_res": 0,
                "light_res": 0,
                "basic_res": 0,
                "dark_res": 0
            }

        ori.update(modifications)

        return ori

    async def hasHero(self, ctx, guardian_id, hero):
        db_ailie = Database()
        inventory_id = db_ailie.get_inventory_id(guardian_id)
        hero_name = db_ailie.get_hero_full_name(hero)

        if hero_name is None:
            await ctx.send("What hero is that? *annoyed*")
            return []

        hero_id = db_ailie.get_hero_id(hero_name)

        if not db_ailie.is_hero_obtained(guardian_id, hero_id):
            await ctx.send("You don't have that hero!")
            return []

        hero_acquired = db_ailie.get_hero_acquired_details(
            inventory_id, hero_id
        )
        (
            hero_stats,
            hero_buffs,
            hero_skill,
            hero_triggers,
        ) = db_ailie.get_hero_stats(hero_id)

        # If no hero, then exit
        if hero_acquired is None:
            await ctx.send(f"You don't have that hero, <@{guardian_id}>.")
            db_ailie.disconnect()
            return []

        return [
            hero_stats, hero_buffs,
            hero_skill, hero_triggers,
            hero_acquired, hero_name
        ]

    async def getOpponentHero(self, ctx, guardian_id):
        db_ailie = Database()

        await ctx.send(
            f"<@{guardian_id}>, please choose to accept or decline "
            + f"<@{ctx.author.id}>'s arena challenge with `Y` or `N`."
        )

        # Function to confirm challenge
        def confirm_application(message):
            return (
                message.author.id == guardian_id
                and message.content.upper() in ["YES", "Y", "NO", "N"]
            )

        # Wait for confirmation
        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_application, timeout=30
            )

            # Challenge accepted
            if msg.content.upper() in ["YES", "Y"]:
                await ctx.send(
                    f"<@{guardian_id}>, reply with your hero choice."
                )
            else:
                # Application rejected else:
                await ctx.send("Challenge denied! LOL, what a coward..")
                db_ailie.disconnect()
                return
        except Exception:
            await ctx.send(
                "Looks like your challenge got ignored, "
                + f"<@{guardian_id}>. Ouch!"
            )
            db_ailie.disconnect()
            return

        def confirm_hero(message):
            return message.author.id == guardian_id

        # Wait for hero chosen
        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_hero, timeout=60
            )
            # Check min characters for hero mention
            hero = msg.content
            if len(hero) < 4:
                await ctx.send(
                    f"Yo, <@{guardian_id}>. "
                    + "At least put 4 characters please?"
                )
                db_ailie.disconnect()
                return

            # Check if opponent has hero
            hero_stats = await self.hasHero(ctx, guardian_id, hero)

        except Exception:
            await ctx.send(f"<@{guardian_id}>, you're taking too long!")
            db_ailie.disconnect()
            return

        return hero_stats

    @commands.command(
        name="rank",
        brief="Show PvP ranks.",
        description=(
            "Rank users based on the server you're in or globally. "
            + "To rank based on the server you're in, put `server` as "
            + "the scope (default). To rank based on global, "
            + "put `global` as the scope."
        ),
    )
    async def rank(self, ctx, scope="server"):
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
        guardian_with_trophy = []
        logical_whereabouts = ""
        output = ""

        if scope.lower() in ["server"]:
            logical_whereabouts = ctx.guild.name
            async for member in ctx.guild.fetch_members(limit=None):
                if db_ailie.is_initialized(member.id):
                    trophy = db_ailie.get_trophy(member.id)
                    if trophy > 0:
                        buffer = [trophy, member, member.id]
                        guardian_with_trophy.append(buffer)
        elif scope.lower() in ["global", "all"]:
            await ctx.send(
                "Global rank will take a while to produce.. "
                + f"Please wait, <@{ctx.author.id}>."
            )
            logical_whereabouts = "Global"
            for guild in self.bot.guilds:
                async for member in guild.fetch_members(limit=None):
                    if db_ailie.is_initialized(member.id):
                        trophy = db_ailie.get_trophy(member.id)
                        if trophy > 0:
                            buffer = [trophy, member, member.id]
                            if buffer not in guardian_with_trophy:
                                guardian_with_trophy.append(buffer)
        else:
            await ctx.send(
                f"Dear, <@{ctx.author.id}>. You can only specify `server` "
                + "or `global`."
            )

        # Display richest user in discord server
        guardian_with_trophy_sorted = sorted(guardian_with_trophy)[::-1]
        guardian_with_trophy = guardian_with_trophy_sorted[:10]
        counter = 1
        for barbarian in guardian_with_trophy:
            if counter == 1:
                output = output \
                    + f"{counter}. {barbarian[0]:,d} ⚔️ - `{barbarian[1]}`"
            else:
                output = output + \
                    f"\n{counter}. {barbarian[0]:,d} ⚔️ - `{barbarian[1]}`"

            # Get username if any
            username = db_ailie.get_username(barbarian[2])
            if username is not None:
                output = output + f" a.k.a. `{username}`"

            counter += 1

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name="Ailie", icon_url=ctx.me.avatar_url)
        embed.add_field(
            name=f"Barbarians in {logical_whereabouts}!", value=output)

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="arena",
        brief="Play arena.",
        description=(
            "Turn-Based arena where you go againts someone else in "
            + "an attempt to gain trophies, exp for your heroes, and gems."
            + "\n\n`ATTACK` attacks the enemy."
            + "\n`WEAPON SKILL` uses your weapon "
            + "to draw its skill on your opponent and cause them "
            + "to be `stunned`."
            + "\n`CHAIN SKILL` can be used only on `stunned` opponents."
            + "\n`DODGE` is used to increase `speed` which may cause opponent to "
            + "miss their attacks. `FLEE` is used to surrender."
        )
    )
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    async def arena(self, ctx, mention: discord.Member = None, *hero):
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
                await ctx.send(
                    f"Can't fight {mention.mention} due to the "
                    + "mentioned being uninitialized!"
                )
                db_ailie.disconnect()
                return

        # Assignment variables
        challenger_id = ctx.author.id
        challenger_name = ctx.author.name
        challenger_avatar = ctx.author.avatar_url
        opponent_id = mention.id
        opponent_name = mention.name
        opponent_avatar = mention.avatar_url

        # Check min characters for hero mention
        hero = " ".join(hero)
        if len(hero) < 4:
            await ctx.send(
                f"Yo, <@{ctx.author.id}>. "
                + "At least put 4 characters please?"
            )
            db_ailie.disconnect()
            return

        # Check if challenger has hero
        hero_stats = await self.hasHero(ctx, challenger_id, hero)

        if not hero_stats:
            return

        hero_stats_challenger = hero_stats[0]
        hero_buffs_challenger = hero_stats[1]
        hero_skill_challenger = hero_stats[2]
        hero_triggers_challenger = hero_stats[3]
        hero_acquired_challenger = hero_stats[4]
        hero_name_challenger = hero_stats[5]

        buffer = {}
        damage = None
        for skill_percent in hero_skill_challenger:
            if skill_percent == "damage":
                damage = hero_skill_challenger[skill_percent]
            else:
                buffer[skill_percent] = hero_skill_challenger[skill_percent]

        if damage:
            buffer["damage"] = damage

        hero_skill_challenger = buffer

        # Get opponent's hero
        hero_stats = await self.getOpponentHero(ctx, opponent_id)

        if not hero_stats:
            return

        hero_stats_opponent = hero_stats[0]
        hero_buffs_opponent = hero_stats[1]
        hero_skill_opponent = hero_stats[2]
        hero_triggers_opponent = hero_stats[3]
        hero_acquired_opponent = hero_stats[4]
        hero_name_opponent = hero_stats[5]

        buffer = {}
        damage = None
        for skill_percent in hero_skill_opponent:
            if skill_percent == "damage":
                damage = hero_skill_opponent[skill_percent]
            else:
                buffer[skill_percent] = hero_skill_opponent[skill_percent]

        if damage:
            buffer["damage"] = damage

        hero_skill_opponent = buffer

        # Same opponent and challenger
        if challenger_id == opponent_id:
            await ctx.send(
                "Sike! You really thought I'm gonna let "
                + f"you fight yourself eh, <@{challenger_id}>?"
            )
            return
        else:
            msg = await ctx.send(
                "An arena fight is about to begin between "
                + f"<@{challenger_id}> and <@{opponent_id}>.."
            )
            await asyncio.sleep(1)
            await msg.edit(content=msg.content + " May the best guardian win!")
            await asyncio.sleep(1)

        # If both parties have chosen heroes, get the raw stats.
        hero_stats_challenger_buffer = hero_stats_challenger
        hero_stats_opponent_buffer = hero_stats_opponent

        # Initialize hero current state
        challenger_current_state = self.resetCurrentState()
        opponent_current_state = self.resetCurrentState()

        # Initialize multiplier and debuff
        multiplier_challenger = []
        multiplier_opponent = []
        debuff_challenger = []
        debuff_opponent = []

        # All the information on participants
        participants = [
            {
                "hero_stats": hero_stats_challenger_buffer,
                "hero_acquired": hero_acquired_challenger,
                "guardian_name": challenger_name,
                "guardian_avatar": challenger_avatar,
                "hero_name": hero_name_challenger,
                "guardian_id": challenger_id,
                "max_hp": hero_stats_challenger_buffer["hp"],
                "hero_buffs":hero_buffs_challenger,
                "color": "🔴",
                "current_state": challenger_current_state,
                "hero_skill": hero_skill_challenger,
                "multipliers": multiplier_challenger,
                "debuffs": debuff_challenger,
                "hero_triggers": hero_triggers_challenger
            },
            {
                "hero_stats": hero_stats_opponent_buffer,
                "hero_acquired": hero_acquired_opponent,
                "guardian_name": opponent_name,
                "guardian_avatar": opponent_avatar,
                "hero_name": hero_name_opponent,
                "guardian_id": opponent_id,
                "max_hp": hero_stats_opponent_buffer["hp"],
                "hero_buffs":hero_buffs_opponent,
                "color": "🔵",
                "current_state": opponent_current_state,
                "hero_skill": hero_skill_opponent,
                "multipliers": multiplier_opponent,
                "debuffs": debuff_opponent,
                "hero_triggers": hero_triggers_opponent
            },
        ]

        # Initialize other stats
        for p in participants:
            p["hero_stats"] = self.resetOtherStats(p["hero_stats"])

        for p in participants:
            p["hero_stats"] = self.assignElementStats(
                p["hero_stats"]["element"], p["hero_stats"])

        # Modify stats depending on levels
        for p in participants:
            p["hero_stats"] = self.heroStatsLevels(
                p["hero_stats"], p["hero_acquired"])

        # Hero buffs
        for p in participants:
            p["hero_stats"] = self.heroStatsBuffs(
                p["hero_stats"], p["hero_buffs"])

        # Get new weapon skill CD
        for p in participants:
            p["current_state"]["weapon_skill_cd"] = \
                self.calcWeapSkillCooldown(
                    p["current_state"]["weapon_skill_cd"],
                    p["hero_stats"]["wsrs"]
                )

        # Display participants' heroes
        for p in participants:
            await self.displayHeroStats(
                ctx, p["hero_stats"], p["hero_acquired"],
                p["guardian_name"], p["guardian_avatar"],
                p["hero_name"], participants, p
            )
            if participants.index(p) == 0:
                await asyncio.sleep(1)
                await ctx.send("**VS**")
                await asyncio.sleep(1)

        enemy_counter = 1
        participants = participants[::-1]
        end = False
        winner = None
        loser = None
        winner_hero = None
        loser_hero = None

        while not end:
            for p in participants:
                if not end:
                    # Ask for move
                    if p["current_state"]["weapon_skill_cd"] == 0:
                        ws_ready = " ✅"
                    else:
                        ws_ready = " ❌"

                    if participants[enemy_counter]["current_state"]["stunned"]:
                        cs_ready = " ✅"
                    else:
                        cs_ready = " ❌"

                    await ctx.send(
                        f"Whats your move, <@{p['guardian_id']}>?\n"
                        + "=============================\n"
                        + "`ATTACK` **(A)**, `WEAPON SKILL` **(WS)** "
                        + f"**[{p['current_state']['weapon_skill_cd']}]**"
                        + f"{ws_ready}, \n`CHAIN SKILL` **(CS)**{cs_ready}, "
                        + "`DODGE` **(D)**, `FLEE` **(F)**.\n"
                        + "============================="
                    )

                    def confirm_move(message):
                        return (
                            message.author.id == p["guardian_id"]
                            and message.content.upper()
                            in [
                                "ATTACK",
                                "A",
                                "WEAPON SKILL",
                                "WS",
                                "CHAIN SKILL",
                                "CS",
                                "DODGE",
                                "D",
                                "FLEE",
                                "F",
                            ]
                        )

                    # Wait for move
                    try:
                        msg = await self.bot.wait_for(
                            "message", check=confirm_move, timeout=60
                        )
                        move = msg.content

                        if move.upper() in ["ATTACK", "A"]:
                            ec = enemy_counter
                            cs = "current_state"
                            wscd = "weapon_skill_cd"
                            # On hit buffs
                            if participants[ec][cs]["on_hit_skill_cd"] == 0 \
                                    and "on_hit" in \
                                    participants[ec]["hero_triggers"]:
                                enemy, not_enemy, on_hit_skill_cd = \
                                    await self.onHit(
                                        ctx, participants,
                                        enemy_counter
                                    )

                                p["hero_stats"] = not_enemy["stats"]
                                p["multipliers"] = not_enemy["multipliers"]
                                p["debuffs"] = not_enemy["debuffs"]
                                p[cs][wscd] = not_enemy["ws_cd"]

                                participants[enemy_counter]["hero_stats"] = \
                                    enemy["stats"]
                                participants[enemy_counter]["multipliers"] = \
                                    enemy["multipliers"]
                                participants[enemy_counter]["debuffs"] = \
                                    enemy["debuffs"]
                                participants[enemy_counter][cs][wscd] = \
                                    enemy["ws_cd"]

                                participants[ec][cs]["on_hit_skill_cd"] = \
                                    on_hit_skill_cd

                            # On normal attack buffs
                            if p[cs]["on_normal_skill_cd"] == 0 \
                                    and "on_normal" in \
                                    p["hero_triggers"]:
                                enemy, not_enemy, on_normal_skill_cd = \
                                    await self.onNormal(
                                        ctx, participants,
                                        enemy_counter
                                    )
                                cs = "current_state"
                                wscd = 'weapon_skill_cd'

                                p["hero_stats"] = not_enemy["stats"]
                                p["multipliers"] = not_enemy["multipliers"]
                                p["debuffs"] = not_enemy["debuffs"]
                                p[cs][wscd] = not_enemy["ws_cd"]

                                participants[enemy_counter]["hero_stats"] = \
                                    enemy["stats"]
                                participants[enemy_counter]["multipliers"] = \
                                    enemy["multipliers"]
                                participants[enemy_counter]["debuffs"] = \
                                    enemy["debuffs"]
                                participants[enemy_counter][cs][wscd] = \
                                    enemy["ws_cd"]

                                p[cs]["on_normal_skill_cd"] = \
                                    on_normal_skill_cd

                            # Finally, attack.
                            end, enemy_hp_left = await self.attack(
                                ctx,
                                p["hero_stats"],
                                participants[enemy_counter]["hero_stats"],
                                participants[enemy_counter]["color"],
                                participants[enemy_counter]["hero_name"],
                                p["current_state"]["stunned"],
                                p["color"],
                                p["hero_name"],
                                "used attack",
                                p["max_hp"],
                                p["hero_stats"]["normal"],
                            )

                            if end:
                                winner = p["guardian_id"]
                                loser = participants[ec]["guardian_id"]
                                winner_hero = p["hero_name"]
                                loser_hero = participants[ec]["hero_name"]

                            # Update enemy's hp
                            participants[enemy_counter]["hero_stats"]["hp"] = \
                                enemy_hp_left

                        if move.upper() in ["WEAPON SKILL", "WS"]:
                            enemy_stunned, weapon_skill_cd = \
                                await self.weaponSkill(
                                    ctx,
                                    p["current_state"]["weapon_skill_cd"],
                                    p["color"],
                                    p["hero_name"],
                                    participants[enemy_counter]["hero_stats"],
                                    participants[enemy_counter]["hero_name"],
                                    p["current_state"]["stunned"],
                                    participants[enemy_counter]
                                    ["current_state"]["stunned"],
                                    p["hero_stats"]["wsrs"]
                                )

                            if enemy_stunned == 3:
                                ec = enemy_counter
                                cs = "current_state"
                                wscd = "weapon_skill_cd"
                                # On hit buffs
                                if participants[ec][cs]["on_hit_skill_cd"] \
                                        == 0 and "on_hit" in \
                                        participants[ec]["hero_triggers"]:
                                    enemy, not_enemy, on_hit_skill_cd = \
                                        await self.onHit(
                                            ctx, participants,
                                            enemy_counter
                                        )

                                    p["hero_stats"] = not_enemy["stats"]
                                    p["multipliers"] = not_enemy["multipliers"]
                                    p["debuffs"] = not_enemy["debuffs"]
                                    p[cs][wscd] = not_enemy["ws_cd"]

                                    participants[enemy_counter]["hero_stats"] \
                                        = enemy["stats"]
                                    participants[enemy_counter]["multipliers"] \
                                        = enemy["multipliers"]
                                    participants[enemy_counter]["debuffs"] = \
                                        enemy["debuffs"]
                                    participants[enemy_counter][cs][wscd] = \
                                        enemy["ws_cd"]

                                    participants[ec][cs]["on_hit_skill_cd"] = \
                                        on_hit_skill_cd

                                # On normal attack buffs
                                if p[cs]["on_normal_skill_cd"] \
                                        == 0 and "on_normal" in \
                                        p["hero_triggers"]:
                                    enemy, not_enemy, on_normal_skill_cd = \
                                        await self.onNormal(
                                            ctx, participants,
                                            enemy_counter
                                        )
                                    cs = "current_state"
                                    wscd = 'weapon_skill_cd'

                                    p["hero_stats"] = not_enemy["stats"]
                                    p["multipliers"] = not_enemy["multipliers"]
                                    p["debuffs"] = not_enemy["debuffs"]
                                    p[cs][wscd] = not_enemy["ws_cd"]

                                    participants[enemy_counter]["hero_stats"] \
                                        = enemy["stats"]
                                    participants[enemy_counter]["multipliers"] \
                                        = enemy["multipliers"]
                                    participants[enemy_counter]["debuffs"] = \
                                        enemy["debuffs"]
                                    participants[enemy_counter][cs][wscd] = \
                                        enemy["ws_cd"]

                                    p[cs]["on_normal_skill_cd"] \
                                        = on_normal_skill_cd

                            # Update enemy stunned and skill cd of caster
                            cs = "current_state"
                            s = "stunned"
                            participants[enemy_counter][cs][s] = \
                                enemy_stunned
                            p["current_state"]["weapon_skill_cd"] = \
                                weapon_skill_cd

                        if move.upper() in ["CHAIN SKILL", "CS"]:
                            cs = "current_state"
                            s = "stunned"

                            if participants[enemy_counter][cs][s]:
                                for skill in p["hero_skill"]:
                                    if skill == "damage":
                                        ec = enemy_counter
                                        cs = "current_state"
                                        ohsc = "on_hit_skill_cd"
                                        ht = "hero_triggers"
                                        hs = "hero_stats"
                                        m = "multipliers"
                                        d = "debuffs"
                                        wscd = "weapon_skill_cd"
                                        # On hit buffs
                                        if participants[ec][cs][ohsc] == 0 \
                                                and "on_hit" in \
                                                participants[ec][ht]:
                                            enemy, not_enemy, \
                                                on_hit_skill_cd = \
                                                await self.onHit(
                                                    ctx, participants,
                                                    enemy_counter
                                                )

                                            p["hero_stats"] = not_enemy["stats"]
                                            p["multipliers"] = not_enemy[m]
                                            p["debuffs"] = not_enemy[d]
                                            p[cs][wscd] = not_enemy["ws_cd"]

                                            participants[enemy_counter][hs] \
                                                = enemy["stats"]
                                            participants[enemy_counter][m] \
                                                = enemy["multipliers"]
                                            participants[enemy_counter][d] = \
                                                enemy["debuffs"]
                                            participants[ec][cs][wscd] \
                                                = enemy["ws_cd"]

                                            participants[ec][cs][ohsc] = \
                                                on_hit_skill_cd

                                        onsc = "on_normal_skill_cd"
                                        # On normal buffs
                                        if p[cs][onsc] == 0 \
                                                and "on_normal" in \
                                                p[ht]:
                                            enemy, not_enemy, \
                                                on_normal_skill_cd = \
                                                await self.onNormal(
                                                    ctx, participants,
                                                    enemy_counter
                                                )
                                            cs = "current_state"
                                            wscd = 'weapon_skill_cd'

                                            p["hero_stats"] = not_enemy["stats"]
                                            p["multipliers"] = \
                                                not_enemy["multipliers"]
                                            p["debuffs"] = not_enemy["debuffs"]
                                            p[cs][wscd] = not_enemy["ws_cd"]

                                            participants[enemy_counter][hs] = \
                                                enemy["stats"]
                                            participants[enemy_counter][m] = \
                                                enemy[m]
                                            participants[enemy_counter][d] = \
                                                enemy["debuffs"]
                                            participants[ec][cs][wscd] = \
                                                enemy["ws_cd"]

                                            p[cs][onsc] = \
                                                on_normal_skill_cd

                                        # Attack calculations
                                        hs = "hero_stats"
                                        c = "color"
                                        hn = "hero_name"
                                        end, enemy_hp_left = await self.attack(
                                            ctx,
                                            p["hero_stats"],
                                            participants[enemy_counter][hs],
                                            participants[enemy_counter][c],
                                            participants[enemy_counter][hn],
                                            p["current_state"]["stunned"],
                                            p["color"],
                                            p["hero_name"],
                                            "used chain skill",
                                            p["max_hp"],
                                            p["hero_skill"][skill]
                                        )

                                        if end:
                                            gi = "guardian_id"
                                            winner = p[gi]
                                            loser = participants[ec][gi]
                                            winner_hero = p["hero_name"]
                                            loser_hero = \
                                                participants[ec]["hero_name"]

                                        # Update enemy's hp
                                        participants[enemy_counter][hs]["hp"] \
                                            = enemy_hp_left
                                    elif skill in ["all_heal", "heal"]:
                                        hp_left = await self.heal(
                                            ctx,
                                            p["max_hp"],
                                            p["hero_skill"],
                                            p["color"],
                                            p["hero_name"],
                                            skill,
                                            p["hero_stats"]
                                        )

                                        # Update hp after heals
                                        p["hero_stats"]["hp"] = hp_left

                                    elif skill.startswith("debuff"):
                                        hn = "hero_name"
                                        debuffs = await self.debuff(
                                                ctx, skill,
                                                p["hero_skill"], p["color"],
                                                participants[enemy_counter][hn]
                                            )

                                        # Append debuffs into debuff list
                                        participants[enemy_counter]["debuffs"]\
                                            .append(debuffs)

                                        # Update stats after debuffs
                                        ec = enemy_counter
                                        cs = "current_state"
                                        wscd = "weapon_skill_cd"
                                        participants[ec]["hero_stats"], \
                                            participants[ec]["multipliers"], \
                                            participants[ec]["debuffs"], \
                                            participants[ec][cs][wscd] = \
                                            self.\
                                            updateStatsAfterMultiplierDebuff(
                                                participants[ec]["hero_stats"],
                                                participants[ec]["multipliers"],
                                                participants[ec]["debuffs"],
                                                participants[ec][cs][wscd]
                                            )

                                    elif p["hero_skill"] in \
                                            ["all_cure", "cure"]:
                                        debuffs = await self.cure(
                                                ctx, p["debuffs"],
                                                p["color"], p["hero_name"]
                                            )
                                    else:
                                        multipliers = await self.multiplier(
                                                ctx, skill,
                                                p["hero_skill"], p["color"],
                                                p["hero_name"]
                                            )

                                        # Append multiplier to list
                                        p["multipliers"].append(multipliers)

                                        # Update stats after multipliers
                                        cs = "current_state"
                                        wscd = "weapon_skill_cd"
                                        p["hero_stats"], p["multipliers"], \
                                            p["debuffs"], p[cs][wscd] = \
                                            self.\
                                            updateStatsAfterMultiplierDebuff(
                                                p["hero_stats"],
                                                p["multipliers"],
                                                p["debuffs"],
                                                p[cs][wscd]
                                            )
                            else:
                                ec = enemy_counter
                                await ctx.send(
                                    f"{participants[enemy_counter]['color']} "
                                    + f"**{participants[ec]['hero_name']}** "
                                    + "is not stunned!"
                                )

                            ec = enemy_counter
                            participants[ec]["current_state"]["stunned"] = 0

                        if move.upper() in ["DODGE", "D"]:
                            if not p["current_state"]["stunned"]:
                                ori_speed = round(p["hero_stats"]["speed"])
                                p["hero_stats"]["speed"] = \
                                    p["hero_stats"]["speed"] + 3

                                hn = "hero_name"
                                hs = "hero_stats"
                                await ctx.send(
                                    f"{p['color']} "
                                    + f"**{p[hn]}**'s speed increased from "
                                    + f"`{ori_speed}` to `{p[hs]['speed']}`!"
                                )
                            else:
                                await ctx.send(
                                    f"{p['color']} **{p['hero_name']}** "
                                    + "is stunned."
                                )

                        if move.upper() in ["FLEE", "F"]:
                            end = True
                            gi = "guardian_id"
                            winner = participants[enemy_counter][gi]
                            loser = p[gi]
                            winner_hero = \
                                participants[enemy_counter]["hero_name"]
                            loser_hero = p["hero_name"]
                            await ctx.send(
                                f"{p['color']} "
                                + f"<@{p[gi]}> fled from the battlefield. "
                                + f"<@{participants[enemy_counter][gi]}> wins!"
                            )

                    except Exception as error:
                        if isinstance(error, asyncio.TimeoutError):
                            gi = "guardian_id"
                            await ctx.send(
                                f"{p['color']} "
                                + f"<@{p[gi]}>, you're taking too long! "
                                + f"<@{participants[enemy_counter][gi]}> wins "
                                + "by default!"
                            )
                            db_ailie.disconnect()
                            return
                        else:
                            AUTHOR_ID = os.getenv("AUTHOR_ID")
                            author = await self.bot.fetch_user(AUTHOR_ID)

                            embed = discord.Embed(color=discord.Color.purple())
                            embed.set_author(
                                name="Ailie's Log",
                                icon_url=ctx.me.avatar_url
                            )
                            embed.add_field(
                                name=ctx.command, value=error, inline=False)

                            await author.send(embed=embed)

                            await ctx.send(
                                "I encountered a bug. Don't worry. "
                                + "I've logged the bug. However, "
                                + "if it still happens, you might "
                                + "wanna send a feedback with "
                                + "the `feedback` command."
                            )

                    # Interchange enemy counter
                    if enemy_counter == 1:
                        enemy_counter = 0
                    else:
                        enemy_counter = 1

                    # Countdown for status and skills
                    if p["current_state"]["weapon_skill_cd"] != 0:
                        p["current_state"]["weapon_skill_cd"] = \
                            p["current_state"]["weapon_skill_cd"] - 1

                    if p["current_state"]["stunned"] != 0:
                        p["current_state"]["stunned"] = \
                            p["current_state"]["stunned"] - 1

                    if p["current_state"]["on_normal_skill_cd"] != 0:
                        p["current_state"]["on_normal_skill_cd"] = \
                            p["current_state"]["on_normal_skill_cd"] - 1

                    if p["current_state"]["on_hit_skill_cd"] != 0:
                        p["current_state"]["on_hit_skill_cd"] = \
                            p["current_state"]["on_hit_skill_cd"] - 1

                    # Update stats after debuffs and multiplier
                    cs = "current_state"
                    wscd = "weapon_skill_cd"

                    p["hero_stats"], p["multipliers"], \
                        p["debuffs"], p[cs][wscd] = \
                        self.updateStatsAfterMultiplierDebuff(
                            p["hero_stats"], p["multipliers"], p["debuffs"],
                            p["current_state"]["weapon_skill_cd"]
                        )
                    participants[enemy_counter]["hero_stats"], \
                        participants[enemy_counter]["multipliers"], \
                        participants[enemy_counter]["debuffs"], \
                        participants[enemy_counter][cs][wscd] = \
                        self.updateStatsAfterMultiplierDebuff(
                            participants[enemy_counter]["hero_stats"],
                            participants[enemy_counter]["multipliers"],
                            participants[enemy_counter]["debuffs"],
                            participants[enemy_counter][cs][wscd]
                        )

                    # Multiplier and debuff count
                    for multi_count in p["multipliers"]:
                        multi_count["count"] = multi_count["count"] - 1

                    for debuff_count in p["debuffs"]:
                        debuff_count["count"] = debuff_count["count"] - 1

        # Give out medals, hero exp, and gems.
        trophy_win = 25
        trophy_lose = -10
        hero_exp_win = 50
        hero_exp_lose = 30

        db_ailie.update_trophy(winner, trophy_win)
        db_ailie.update_trophy(loser, trophy_lose)
        db_ailie.update_hero_exp(winner, winner_hero, hero_exp_win)
        db_ailie.update_hero_exp(loser, loser_hero, hero_exp_lose)
        db_ailie.store_gems(winner, 500)

        # Disconnect Database
        db_ailie.disconnect()


def setup(bot):
    bot.add_cog(PvP(bot))
