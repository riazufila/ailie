#!/usr/bin/env python

import asyncio
import random
import discord
from discord.ext import commands
from helpers.database import Database


class PvP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_miss(self, speed):
        miss = random.choices(
            [True, False],
            [
                speed,
                (100 - speed),
            ],
            k=1,
        )[0]

        return miss

    async def goingToAttackPleaseBuff(
            self, ctx, heroes, first, second, buffs):
        for buff in buffs:
            if buff == "damage":
                pass
            elif buff in ["all_heal", "heal"]:
                heroes[first]["stats"]["hp"] = await self.heal(
                    ctx, heroes[first], buffs[buff]
                )
            elif buff in ["all_cure", "cure"]:
                heroes[first]["stats"], heroes[first]["debuffs"] = \
                    await self.removeAllDebuff(ctx, heroes[first])
            elif buff.startswith("debuff"):
                heroes[second]["stats"], heroes[second]["debuffs"] \
                    = await self.debuff(
                    ctx, heroes[first], heroes[second], buff, buffs, 3
                )
            else:
                heroes[first]["stats"], heroes[first]["multipliers"] \
                    = await self.multiplier(
                    ctx, heroes[first], heroes[first], buff, buffs, 3
                )

        return heroes

    async def gotHitPleaseBuff(
            self, ctx, heroes, first, second, buffs):
        for buff in buffs:
            if buff == "damage":
                pass
            elif buff in ["all_heal", "heal"]:
                heroes[second]["stats"]["hp"] = await self.heal(
                    ctx, heroes[second], buffs[buff]
                )
            elif buff in ["all_cure", "cure"]:
                heroes[second]["stats"], heroes[second]["debuffs"] = \
                    await self.removeAllDebuff(ctx, heroes[second])
            elif buff.startswith("debuff"):
                heroes[first]["stats"], heroes[first]["debuffs"] \
                    = await self.debuff(
                    ctx, heroes[second], heroes[first], buff, buffs, 3
                )
            else:
                heroes[second]["stats"], heroes[second]["multipliers"] \
                    = await self.multiplier(
                    ctx, heroes[second], heroes[second], buff, buffs, 3
                )

        return heroes

    async def multiplier(
            self, ctx, actor, victim, multiplier, multipliers, count):
        multipliers_buffer = self.initMultiplier(count)
        if multiplier.startswith("all"):
            multi = multiplier[4:]
        else:
            multi = multiplier

        multipliers_buffer[multi] = multipliers[multiplier]

        # Enter multipliers buffer in a list of many multipliers
        victim["multipliers"].append(multipliers_buffer)

        # Update stats after multiplier
        victim["stats"], victim["multipliers"], \
            victim["current_state"]["weapon_skill_cd"] = \
            self.updateStatsAfterMultiplierDebuff(
                victim, victim["multipliers"])

        multi_readable = self.translateToReadableFormat(multi)
        await ctx.send(
            f"{actor['color']} **{victim['hero_name']}**'s "
            + f"{multi_readable} is buffed!"
        )
        await asyncio.sleep(2)

        return victim["stats"], victim["multipliers"]

    async def debuff(self, ctx, actor, victim, debuff, debuffs, count):
        debuffs_buffer = self.initDebuff(count)
        debuffs_buffer[debuff[7:]] = -1 * debuffs[debuff]

        # Enter debuffs in a list of many debuffs
        victim["debuffs"].append(debuffs_buffer)

        # Update stats after debuff
        victim["stats"], \
            victim["debuffs"], \
            victim["current_state"]["weapon_skill_cd"] = \
            self.updateStatsAfterMultiplierDebuff(
                victim, victim["debuffs"])

        debuff_readable = self.translateToReadableFormat(debuff)
        await ctx.send(
            f"{actor['color']} **{victim['hero_name']}**'s "
            + f"{debuff_readable} is debuffed!"
        )
        await asyncio.sleep(2)

        return victim["stats"], victim["debuffs"]

    async def removeAllDebuff(self, ctx, hero):
        if len(hero["debuffs"]) > 0:
            for debuff in hero["debuffs"]:
                # Calculate new stats when debuff is removed
                for debuff_in_debuff in debuff:
                    if debuff_in_debuff not in ["count", "check"]:
                        if debuff_in_debuff in ["attack", "hp", "def"]:
                            hero["stats"][debuff_in_debuff] = round(
                                hero["stats"]
                                * (100 / (100 + debuff[debuff_in_debuff]))
                            )
                        else:
                            hero["stats"][debuff_in_debuff] = \
                                hero["stats"][debuff_in_debuff] \
                                - debuff[debuff_in_debuff]

                # Remove the debuff
                hero["debuffs"].remove(debuff)

        await ctx.send(
            f"{hero['color']} **{hero['hero_name']}** is cured!"
        )
        await asyncio.sleep(2)

        return hero["stats"], hero["debuffs"]

    def updateStatsAfterMultiplierDebuff(
            self, hero, all_multipliers_debuffs):
        wsrs_check = False
        for multipliers_debuffs in all_multipliers_debuffs:
            # if multipliers_debuffs["count"] > 1 and \
            if not multipliers_debuffs["check"]:
                for multiplier_debuff in multipliers_debuffs:
                    # Only update with those that have count 3
                    # and is not checked
                    if multiplier_debuff not in ["count", "check"]:
                        if multiplier_debuff in ["attack", "hp", "def"]:
                            hero["stats"][multiplier_debuff] = round(
                                hero["stats"][multiplier_debuff]
                                * ((100
                                    + multipliers_debuffs[multiplier_debuff])
                                    / 100)
                            )
                        else:
                            if multiplier_debuff == "wsrs":
                                wsrs_check = True

                            hero["stats"][multiplier_debuff] = \
                                hero["stats"][multiplier_debuff] + \
                                multipliers_debuffs[multiplier_debuff]
                    # After stats are done updating, set to checked.
                    multipliers_debuffs["check"] = True
            elif multipliers_debuffs["count"] == 1 and \
                    multipliers_debuffs["check"]:
                for multiplier_debuff in multipliers_debuffs:
                    if multiplier_debuff not in ["count", "check"]:
                        if multiplier_debuff in ["attack", "hp", "def"]:
                            hero["stats"][multiplier_debuff] = round(
                                hero["stats"][multiplier_debuff]
                                * (100
                                    / (100 +
                                        multipliers_debuffs[multiplier_debuff]))
                            )
                        else:
                            hero["stats"][multiplier_debuff] = \
                                hero["stats"][multiplier_debuff] - \
                                multipliers_debuffs[multiplier_debuff]
                # Remove after stats are updated
                all_multipliers_debuffs.remove(multipliers_debuffs)
            else:
                pass

        # If wsrs is updated
        if wsrs_check:
            hero["current_state"]["weapon_skill_cd"] = \
                self.calcWeapSkillCooldown(
                    hero["current_state"]["weapon_skill_cd"],
                    hero["stats"]["wsrs"]
                )

        return hero["stats"], \
            all_multipliers_debuffs, \
            hero["current_state"]["weapon_skill_cd"]

    async def attack(self, ctx, actor, victim, move_type, percent_damage):
        end = False
        winner = {}
        loser = {}
        damage_type = "damage"

        damage = round((
            actor["stats"]["attack"]
            + (actor["stats"]["attack"] * percent_damage / 100))
            * ((100 + actor["stats"][actor["stats"]["element"]]) / 100)
        )

        crit = random.choices(
            [True, False],
            [actor["stats"]["cc"], (100 - actor["stats"]["cc"])],
            k=1,
        )[0]

        if crit:
            damage = damage * 2
            damage_type = "critical damage"

        total_damage = round(
            damage
            * (100
                / (100
                    + victim["stats"]["def"]
                    + victim["stats"][f"{actor['stats']['element']}_res"]))
            - victim["stats"]["dr"]
        )

        enemy_speed = victim["stats"][
            "speed"
        ]

        miss = self.is_miss(enemy_speed)

        if miss:
            await ctx.send(
                f"{actor['color']} **{actor['hero_name']}** missed.")
            await asyncio.sleep(2)

        if not miss:
            if total_damage < 0:
                total_damage = 0

            victim["stats"]["hp"] = (
                victim["stats"]["hp"]
                - total_damage
            )

            await ctx.send(
                f"{actor['color']} **{actor['hero_name']}** used "
                + f"{move_type} and `dealt {total_damage:,d}` "
                + f"{damage_type}!"
            )
            await asyncio.sleep(2)

            if victim["stats"]["hp"] < 0:
                end = True
                winner = {
                    "guardian_id": actor["guardian_id"],
                    "hero_name": actor["hero_name"]
                }
                loser = {
                    "guardian_id": victim["guardian_id"],
                    "hero_name": victim["hero_name"]
                }
                await ctx.send(
                    f"{victim['color']} "
                    + f"**{victim['hero_name']}"
                    + f"** has died! **{actor['hero_name']}** won!"
                )
                await asyncio.sleep(2)

            else:
                await ctx.send(
                    f"{victim['color']} "
                    + f"**{victim['hero_name']}"
                    + "**'s HP reduced! "
                    + f"`{victim['stats']['hp']}"
                    + f"`/`{victim['max_hp']}` HP left!"
                )
                await asyncio.sleep(2)

        return actor["stats"]["hp"], victim["stats"]["hp"], end, winner, loser

    async def heal(self, ctx, hero, buff_percent):
        # Calculate heals
        heal = round(hero["max_hp"] * (buff_percent / 100))
        hp_after_heal = hero["stats"]["hp"] + heal

        if hp_after_heal > hero["max_hp"]:
            hp_after_heal = hero["max_hp"]

        await ctx.send(
            f"{hero['color']} `{heal:,d}` HP healed to "
            + f"**{hero['hero_name']}**.\n"
        )
        await asyncio.sleep(2)
        await ctx.send(
            f"{hero['color']} **{hero['hero_name']}** current HP is "
            + f"`{hp_after_heal}`/`{hero['max_hp']}`."
        )
        await asyncio.sleep(2)

        return hp_after_heal

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

    def calcWeapSkillCooldown(self, ws_cd, wsrs):
        ws_cd = round(ws_cd * (100 / (100 + wsrs)))

        return ws_cd

    def multiplyHeroBuffs(self, stats, buffs):
        for stat in buffs:
            if stat.startswith("all"):
                s = stat[4:]
            else:
                s = stat

            stats[s] = stats[s] + buffs[stat]

        return stats

    def multiplyStatsWithLevels(self, stats, hero_level, user_level):
        # Increase overall stats
        for stat in stats:
            if stat in ["attack", "hp", "def"]:
                stats[stat] = round(
                    stats[stat]
                    + (stats[stat] * (((hero_level - 1) / 100) * 2))
                    + (stats[stat] * (((user_level - 1) / 100) * 2))
                )

        # Increase stats specifically for arena
        for stat in stats:
            if stat in ["hp"]:
                stats[stat] = stats[stat] * 2

        return stats

    def initElementStats(self, stats):
        element = stats["element"]
        element_stats = {}

        if element.lower() == "light":
            element_stats = {
                "water_res": 0,
                "fire_res": 0,
                "earth_res": 0,
                "light_res": 0,
                "basic_res": -30,
                "dark_res": 30,
            }
        elif element.lower() == "dark":
            element_stats = {
                "water_res": 0,
                "fire_res": 0,
                "earth_res": 0,
                "light_res": -30,
                "basic_res": 30,
                "dark_res": 0,
            }
        if element.lower() == "basic":
            element_stats = {
                "water_res": 0,
                "fire_res": 0,
                "earth_res": 0,
                "light_res": 30,
                "basic_res": 0,
                "dark_res": -30,
            }
        if element.lower() == "fire":
            element_stats = {
                "water_res": -30,
                "fire_res": 0,
                "earth_res": 30,
                "light_res": 0,
                "basic_res": 0,
                "dark_res": 0,
            }
        if element.lower() == "water":
            element_stats = {
                "water_res": 0,
                "fire_res": 30,
                "earth_res": -30,
                "light_res": 0,
                "basic_res": 0,
                "dark_res": 0,
            }
        if element.lower() == "earth":
            element_stats = {
                "water_res": 30,
                "fire_res": -30,
                "earth_res": 0,
                "light_res": 0,
                "basic_res": 0,
                "dark_res": 0,
            }

        stats.update(element_stats)

        return stats

    def initExtraStats(self, hero_stats):
        extra_stats = {
            "water": 0,
            "fire": 0,
            "earth": 0,
            "light": 0,
            "dark": 0,
            "basic": 0,
            "wsrs": 0,
            "speed": 0,
            "skill": 0,
            "normal": 20,
        }

        hero_stats.update(extra_stats)

        return hero_stats

    def initCurrentState(self):
        return {
            "weapon_skill_cd": 5,
            "on_normal_skill_cd": 5,
            "on_hit_skill_cd": 5,
            "evade_cd": 0,
            "stunned": 0,
        }

    def initMultiplier(self, count):
        return {
            "count": count,
            "check": False,
            "attack": 0,
            "cc": 0,
            "hp": 0,
            "def": 0,
            "dr": 0,
            "basic": 0,
            "light": 0,
            "dark": 0,
            "fire": 0,
            "earth": 0,
            "water": 0,
            "normal": 0,
            "skill": 0,
            "speed": 0,
            "wsrs": 0,
        }

    def initDebuff(self, count):
        return {
            "count": count,
            "check": False,
            "attack": 0,
            "cc": 0,
            "hp": 0,
            "def": 0,
            "dr": 0,
            "basic_res": 0,
            "light_res": 0,
            "dark_res": 0,
            "fire_res": 0,
            "earth_res": 0,
            "water_res": 0,
            "normal": 0,
            "skill": 0,
            "speed": 0,
            "wsrs": 0,
        }

    def get_hero_information(self, guardian_id, hero):
        db_ailie = Database()
        inventory_id = db_ailie.get_inventory_id(guardian_id)
        hero_full_name = db_ailie.get_hero_full_name(hero)
        hero_id = db_ailie.get_hero_id(hero_full_name)

        hero_acquired = db_ailie.get_hero_acquired_details(
            inventory_id, hero_id
        )
        (
            hero_stats,
            hero_buffs,
            hero_skill,
            hero_triggers,
        ) = db_ailie.get_hero_stats(hero_id)

        # Put damage and the end of dictionary for hero_skill
        buffer = {}
        damage = None
        for skill_percent in hero_skill:
            if skill_percent == "damage":
                damage = hero_skill[skill_percent]
            else:
                buffer[skill_percent] = hero_skill[skill_percent]

        if damage:
            buffer["damage"] = damage

        hero_skill = buffer

        return {
            "stats": hero_stats,
            "buffs": hero_buffs,
            "skill": hero_skill,
            "triggers": hero_triggers,
            "acquired": hero_acquired,
            "hero_name": hero_full_name,
        }

    async def is_min_four_chars(self, ctx, hero):
        if len(hero) < 4:
            await ctx.send(
                f"Yo, <@{ctx.author.id}>. "
                + "At least put 4 characters please?"
            )
            return False
        return True

    async def check_if_initialized(self, ctx, guardian_id):
        db_ailie = Database()
        if not db_ailie.is_initialized(guardian_id):
            if ctx.author.id == guardian_id:
                await ctx.send(
                    "Do `ailie;initialize` or `a;initialize` "
                    + "first before anything!"
                )
            else:
                await ctx.send(
                    f"Can't fight <@{guardian_id}> due to the "
                    + "mentioned being uninitialized!"
                )

            db_ailie.disconnect()
            return False
        return True

    async def hasHero(self, ctx, guardian_id, hero):
        db_ailie = Database()

        hero_full_name = db_ailie.get_hero_full_name(hero)

        # If there is no such hero
        if hero_full_name is None:
            await ctx.send("What hero is that? *annoyed*")
            db_ailie.disconnect()
            return False

        hero_id = db_ailie.get_hero_id(hero_full_name)
        if not db_ailie.is_hero_obtained(guardian_id, hero_id):
            await ctx.send("You don't have that hero!")
            db_ailie.disconnect()
            return False

        return True

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
            for member in ctx.guild.members:
                if db_ailie.is_initialized(member.id):
                    trophy = db_ailie.get_trophy(member.id)
                    level = db_ailie.get_user_level(member.id)
                    if trophy > 0:
                        buffer = [trophy, str(member), member.id, level]
                        guardian_with_trophy.append(buffer)
        elif scope.lower() in ["global", "all"]:
            await ctx.send(
                "Global rank will take a while to produce.. "
                + f"Please wait, <@{ctx.author.id}>."
            )
            logical_whereabouts = "Global"
            for guild in self.bot.guilds:
                for member in guild.members:
                    if db_ailie.is_initialized(member.id):
                        trophy = db_ailie.get_trophy(member.id)
                        level = db_ailie.get_user_level(member.id)
                        if trophy > 0:
                            buffer = [trophy, str(member), member.id, level]
                            if buffer not in guardian_with_trophy:
                                guardian_with_trophy.append(buffer)
        else:
            await ctx.send(
                f"Dear, <@{ctx.author.id}>. You can only specify `server` "
                + "or `global`."
            )

        # If no one has trophy
        if not guardian_with_trophy:
            await ctx.send("No one has trophies.")
            db_ailie.disconnect()
            return

        # Display richest user in discord server
        guardian_with_trophy_sorted = sorted(guardian_with_trophy, reverse=True)
        guardian_with_trophy = guardian_with_trophy_sorted[:10]
        counter = 1
        for barbarian in guardian_with_trophy:
            if counter == 1:
                output = output \
                    + f"{counter}. {barbarian[0]:,d} 🏆 - " \
                    + f"Lvl {barbarian[3]} `{barbarian[1]}`"
            else:
                output = output + \
                        f"\n{counter}. {barbarian[0]:,d} 🏆 - " \
                        + f"Lvl {barbarian[3]} `{barbarian[1]}`"

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
        name="trophy",
        brief="Check trophies.",
        description="Check the amount of your current trophies.",
        aliases=["trophies"]
    )
    async def trophy(self, ctx, mention: discord.Member = None):
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

        # Display trophies
        trophies = db_ailie.get_trophy(guardian_id)
        wins = db_ailie.get_arena_wins(guardian_id)
        losses = db_ailie.get_arena_losses(guardian_id)
        db_ailie.disconnect()
        embed = discord.Embed(
            description=(
                f"**Trophies**: `{trophies:,d}`"
                + f"\n**Wins**: `{wins:,d}`"
                + f"\n**Losses**: `{losses:,d}`"
            ),
            color=discord.Color.purple()
        )
        embed.set_author(
            name=f"{guardian_name}'s Gems", icon_url=guardian_avatar)
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
            + "\n`EVADe` is used to increase `speed` for a while "
            + "which may cause opponent "
            + "to miss their attacks. `Surrender` is used to surrender."
        ),
    )
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    async def arena(self, ctx, mention: discord.Member = None, *hero):
        # Check if mention is present
        if not mention:
            await ctx.send("You forgot to mention who to fight.")
            return

        # Check if hero is specified
        if not hero:
            await ctx.send("You forgot to specify which hero to use.")
            return

        # Check if hero has at least 4 characters
        hero = " ".join(hero)
        if not await self.is_min_four_chars(ctx, hero):
            return

        # Assign id, name, and avatar url to a meaningful variable
        challenger_id = ctx.author.id
        challenger_name = ctx.author.name
        opponent_id = mention.id
        opponent_name = mention.name

        # Check if the users involved are initialized.
        for guardian_id in [challenger_id, opponent_id]:
            if not await self.check_if_initialized(ctx, guardian_id):
                return

        # Check if users has the hero mentioned
        if not await self.hasHero(ctx, challenger_id, hero):
            return

        # Ask for opponent's hero to use
        db_ailie = Database()

        await ctx.send(
            f"<@{opponent_id}>, please choose to accept or decline "
            + f"<@{challenger_id}>'s arena challenge with `Y` or `N`."
        )

        def confirm_application(message):
            return (
                message.author.id == opponent_id
                and message.content.upper() in ["YES", "Y", "NO", "N"]
            )

        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_application, timeout=30
            )

            if msg.content.upper() in ["YES", "Y"]:
                await ctx.send(
                    f"<@{opponent_id}>, reply with your hero choice."
                )
            else:
                await ctx.send("Challenge denied! LOL, what a coward.")
                db_ailie.disconnect()
                return
        except Exception as error:
            if isinstance(error, asyncio.TimeoutError):
                await ctx.send(
                    "Looks like the challenge got ignored, "
                    + f"<@{challenger_id}>. Ouch!"
                )
            else:
                await ctx.send("I bugged.")
            db_ailie.disconnect()
            return

        def confirm_hero(message):
            return message.author.id == opponent_id

        # Wait for hero chosen
        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_hero, timeout=60
            )
            # Check min characters for hero mention
            opponent_hero = msg.content
            if not await self.is_min_four_chars(ctx, opponent_hero):
                return

            # Check if opponent has hero
            if not await self.hasHero(ctx, opponent_id, opponent_hero):
                return
        except Exception as error:
            if isinstance(error, asyncio.TimeoutError):
                await ctx.send(
                    f"<@{opponent_id}>, you're taking too long! Aborting."
                )
            else:
                await ctx.send("I bugged.")
            db_ailie.disconnect()
            return

        # Get users' hero information
        heroes = []
        for guardian_info in [
            [challenger_id, hero],
            [opponent_id, opponent_hero],
        ]:
            hero_information = self.get_hero_information(
                guardian_info[0], guardian_info[1]
            )
            heroes.append(hero_information)

        # If the mentioned hero is the same hero.
        if challenger_id == opponent_id:
            await ctx.send(
                "Sike! You really thought I'm gonna let "
                + f"you fight yourself eh, <@{challenger_id}>?"
            )
            return

        # Set all the other information needed for a proper battle
        # Associate user details with the heroes
        heroes[0]["guardian_id"] = challenger_id
        heroes[0]["guardian_name"] = challenger_name
        heroes[0]["color"] = "🔴"
        heroes[1]["guardian_id"] = opponent_id
        heroes[1]["guardian_name"] = opponent_name
        heroes[1]["color"] = "🔵"

        # Initialize hero current state, multipliers, and debuffs.
        for hero in heroes:
            hero["current_state"] = self.initCurrentState()
            hero["multipliers"] = []
            hero["debuffs"] = []

        # Initialize extra stats
        for hero in heroes:
            hero["stats"] = self.initExtraStats(hero["stats"])

        # Initialize element stats
        for hero in heroes:
            hero["stats"] = self.initElementStats(hero["stats"])

        # Modify stats depending on hero and user level
        for hero in heroes:
            db_ailie = Database()
            user_level = db_ailie.get_user_level(hero["guardian_id"])
            hero["stats"] = self.multiplyStatsWithLevels(
                hero["stats"], hero["acquired"]["level"], user_level)
            db_ailie.disconnect()

        # Modify stats based on hero buffs
        for hero in heroes:
            hero["stats"] = self.multiplyHeroBuffs(hero["stats"], hero["buffs"])

        # Update Max HP to a separate key
        for hero in heroes:
            hero["max_hp"] = hero["stats"]["hp"]

        # Get new weapon skill cooldown after stats have been modified
        for hero in heroes:
            hero["current_state"]["weapon_skill_cd"] = \
                self.calcWeapSkillCooldown(
                    hero["current_state"]["weapon_skill_cd"],
                    hero["stats"]["wsrs"]
                )

        # Start arena between heroes
        end = False
        winner = {}
        loser = {}
        round = 1
        while True:
            # Show available moves for each player
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                icon_url=self.bot.user.avatar_url,
                name=f"Round {round}"
            )
            embed.set_footer(
                text="Enter the number respective to your choice of move.")

            for hero in heroes:
                index = heroes.index(hero)
                if index == 0:
                    other_index = 1
                else:
                    other_index = 0

                # Get weapon skill cooldown
                if heroes[index]["current_state"]["weapon_skill_cd"] != 0:
                    ws_cd = \
                        f"`{str(hero['current_state']['weapon_skill_cd'])}`"
                else:
                    ws_cd = "✅"

                # Get evade cooldown
                if heroes[index]["current_state"]["evade_cd"] != 0:
                    ev_cd = \
                        f"`{str(hero['current_state']['evade_cd'])}`"
                else:
                    ev_cd = "✅"

                # Get chain skill availability
                if heroes[other_index]["current_state"]["stunned"] != 0:
                    cs_cd = "✅"
                else:
                    cs_cd = "❌"

                # Display the moves
                hp = (
                    f"**HP**\n`{hero['stats']['hp']:,d}`/`{hero['max_hp']:,d}`"
                )
                moves = (
                    "**Moves**"
                    + "\n1. **Attack**"
                    + f"\n2. **({ws_cd}) Weapon Skill**"
                    + f"\n3. **({cs_cd}) Chain Skill**"
                    + f"\n4. **({ev_cd}) Evade**"
                    + "\n5. **Surrender**"
                )
                embed.add_field(
                    name=f"{hero['guardian_name']}'s",
                    value=f"{hp}\n\n{moves}"
                )

            await asyncio.sleep(1)
            await ctx.send(embed=embed)

            # Prompt for each player to enter their move
            await asyncio.sleep(5)
            msg = await ctx.send(
                f"<@{heroes[0]['guardian_id']}> and "
                + f"<@{heroes[1]['guardian_id']}>, please go ahead and "
                + "choose your moves.. in.."
            )
            await asyncio.sleep(1)
            await msg.edit(content=msg.content + "\n3..")
            await asyncio.sleep(1)
            await msg.edit(content=msg.content + "\n2..")
            await asyncio.sleep(1)
            await msg.edit(content=msg.content + "\n1!")

            players = [heroes[0]["guardian_id"], heroes[1]["guardian_id"]]
            choices = []

            def check(message):
                if message.channel == ctx.channel \
                        and message.author.id in players \
                        and message.content.lower() in [
                            "a", "ws", "cs", "e", "s",
                            "1", "2", "3", "4", "5"
                        ]:
                    choices.append([message.author.id, message.content.lower()])
                    players.remove(message.author.id)
                    if len(players) == 0:
                        return True
                return False

            try:
                await self.bot.wait_for("message", check=check, timeout=60)
            except Exception as error:
                if isinstance(error, asyncio.TimeoutError) \
                        and len(choices) == 0:
                    await ctx.send(
                        "Aren't you both so responsible? "
                        + "Starting a battle and abandoning it, "
                        + f"<@{heroes[0]['guardian_id']}> and "
                        + f"<@{heroes[1]['guardian_id']}>!"
                    )
                    return
                elif isinstance(error, asyncio.TimeoutError) \
                        and len(choices) == 1:
                    winner_id = ""
                    winner_hero = ""
                    quitter_id = ""
                    quitter_hero = ""
                    for choice in choices:
                        if choice[0] == heroes[0]["guardian_id"]:
                            winner_id = heroes[0]["guardian_id"]
                            winner_hero = heroes[0]["hero_name"]

                            quitter_id = heroes[1]["guardian_id"]
                            quitter_hero = heroes[1]["hero_name"]
                        else:
                            winner_id = heroes[1]["guardian_id"]
                            winner_hero = heroes[1]["hero_name"]

                            quitter_id = heroes[0]["guardian_id"]
                            quitter_hero = heroes[0]["hero_name"]

                    if round >= 3:
                        winner = {
                            "guardian_id": winner_id,
                            "hero_name": winner_hero
                        }
                        loser = {
                            "guardian_id": quitter_id,
                            "hero_name": quitter_hero
                        }

                    await ctx.send(
                        "Don't get involved in something you can't finish, "
                        + f"<@{quitter_id}>!"
                    )
                    return
                else:
                    await ctx.send("A problem occured.")

            # Now process the choice for each player
            for choice in choices:
                # Determining in which index is the the one who first
                # and second replied
                first = 0
                second = 1

                for hero in heroes:
                    if choice[0] == hero["guardian_id"]:
                        first = heroes.index(hero)

                        if first == 0:
                            second = 1
                        else:
                            second = 0

                # Indicator of who's move it is
                await ctx.send(f"<@{heroes[first]['guardian_id']}>'s turn.")
                await asyncio.sleep(2)

                # Move choices available for players
                # Attack Move
                if choice[1].lower() in ["a", "1"] and \
                        heroes[first]["current_state"]["stunned"] == 0:
                    move_type = "attack"
                    percent_damage = heroes[first]["stats"]["normal"]

                    # Trigger buffs on attack
                    if heroes[first]["current_state"]["on_normal_skill_cd"] \
                            == 0:
                        if "on_normal" in heroes[first]["triggers"]:
                            heroes = await self.goingToAttackPleaseBuff(
                                ctx, heroes, first, second,
                                heroes[first]["triggers"]["on_normal"],
                            )
                        heroes[first]["current_state"]["on_normal_skill_cd"] = 5

                    # Trigger buffs to victim
                    if heroes[second]["current_state"]["on_hit_skill_cd"] == 0:
                        if "on_hit" in heroes[second]["triggers"]:
                            heroes = await self.gotHitPleaseBuff(
                                ctx, heroes, first, second,
                                heroes[second]["triggers"]["on_hit"],
                            )
                        heroes[second]["current_state"]["on_hit_skill_cd"] = 5

                    # Deal damage
                    heroes[first]["stats"]["hp"], \
                        heroes[second]["stats"]["hp"], \
                        end, winner, loser = await self.attack(
                            ctx, heroes[first], heroes[second],
                            move_type, percent_damage
                        )

                # Weapon Skill Move
                elif choice[1].lower() in ["ws", "2"] and \
                        heroes[first]["current_state"]["stunned"] == 0:
                    if heroes[first]["current_state"]["weapon_skill_cd"] == 0:
                        # Trigger buffs on attack
                        cs = "current_state"
                        if heroes[first][cs]["on_normal_skill_cd"] \
                                == 0:
                            if "on_normal" in heroes[first]["triggers"]:
                                heroes = await self.goingToAttackPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[first]["triggers"]["on_normal"],
                                )
                            heroes[first][cs]["on_normal_skill_cd"] = 5

                        # Trigger buffs to victim
                        if heroes[second][cs]["on_hit_skill_cd"] == 0:
                            if "on_hit" in heroes[second]["triggers"]:
                                heroes = await self.gotHitPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[second]["triggers"]["on_hit"],
                                )
                            heroes[second]["current_state"]["on_hit_skill_cd"] \
                                = 5

                        # Weapon Skill calculations
                        miss = self.is_miss(heroes[second]["stats"]["speed"])
                        if not miss:
                            heroes[second]["current_state"]["stunned"] = 3
                            await ctx.send(
                                f"{heroes[first]['color']} "
                                + f"**{heroes[first]['hero_name']}** "
                                + "used weapon skill and stunned "
                                + f"**{heroes[second]['hero_name']}** "
                                + "for 3 rounds!"
                            )
                            await asyncio.sleep(2)
                        else:
                            await ctx.send(
                                f"{heroes[first]['color']} "
                                + f"**{heroes[first]['hero_name']}** "
                                + "missed!"
                            )
                            await asyncio.sleep(2)
                        heroes[first]["current_state"]["weapon_skill_cd"] = \
                            self.calcWeapSkillCooldown(
                                5, heroes[first]["stats"]["wsrs"])
                    else:
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[first]['hero_name']}**'s "
                            + "weapon skill is on cooldown!"
                        )
                        await asyncio.sleep(2)

                # Chain Skill Move
                elif choice[1].lower() in ["cs", "3"] and \
                        heroes[first]["current_state"]["stunned"] == 0:
                    if heroes[second]["current_state"]["stunned"] != 0:
                        move_type = "chain skill"
                        if "damage" in heroes[first]["skill"]:
                            percent_damage = heroes[first]["skill"]["damage"]
                        else:
                            percent_damage = None

                        cs = "current_state"
                        # Trigger buffs on attack
                        if heroes[first][cs]["on_normal_skill_cd"] \
                                == 0:
                            if "on_normal" in heroes[first]["triggers"]:
                                heroes = await self.goingToAttackPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[first]["triggers"]["on_normal"],
                                )
                            heroes[first][cs]["on_normal_skill_cd"] = 5

                        # Trigger buffs to victim
                        if heroes[second][cs]["on_hit_skill_cd"] == 0:
                            if "on_hit" in heroes[second]["triggers"]:
                                heroes = await self.gotHitPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[second]["triggers"]["on_hit"],
                                )
                            heroes[second][cs]["on_hit_skill_cd"] = 5

                        # Buffs from activating chain skill
                        if heroes[second]["current_state"]["stunned"] != 0:
                            heroes = await self.goingToAttackPleaseBuff(
                                ctx, heroes, first,
                                second, heroes[first]["skill"])

                        # Deal damage
                        if percent_damage is not None:
                            heroes[first]["stats"]["hp"], \
                                heroes[second]["stats"]["hp"], \
                                end, winner, loser = await self.attack(
                                ctx, heroes[first], heroes[second],
                                move_type, percent_damage
                            )

                        # Break stunned condition after CS
                        heroes[second]["current_state"]["stunned"] = 0
                    else:
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[second]['hero_name']}** "
                            + "is not stunned!"
                        )
                        await asyncio.sleep(2)

                # Evade Move
                elif choice[1].lower() in ["e", "4"] and \
                        heroes[first]["current_state"]["stunned"] == 0:
                    if heroes[first]["current_state"]["evade_cd"] == 0:
                        evasion_buff = {"speed": 50}
                        heroes[first]["stats"], heroes[first]["multipliers"] = \
                            await self.multiplier(
                                ctx, heroes[first], heroes[first],
                                "speed", evasion_buff, 2)
                        heroes[first]["current_state"]["evade_cd"] = 3
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[first]['hero_name']}** "
                            + "tries to evade the next attack "
                            + "in the nearest time!"
                        )
                        await asyncio.sleep(2)
                    else:
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[first]['hero_name']}** "
                            + "can't use evade right now!"
                        )
                        await asyncio.sleep(2)

                # Surrender
                elif choice[1].lower() in ["s", "5"]:
                    end = True
                    if round >= 3:
                        winner = {
                            "guardian_id": heroes[second]["guardian_id"],
                            "hero_name": heroes[second]["hero_name"]
                        }
                        loser = {
                            "guardian_id": heroes[first]["guardian_id"],
                            "hero_name": heroes[first]["hero_name"]
                        }

                    await ctx.send(
                        f"<@{heroes[first]['guardian_id']}> surrendered!")
                    await asyncio.sleep(2)

                # Pass everything else
                else:
                    pass

                # If enemy is stunned
                if heroes[first]["current_state"]["stunned"] != 0:
                    await ctx.send(
                        f"{heroes[first]['color']} "
                        + f"**{heroes[first]['hero_name']}** "
                        + "is stunned!"
                    )
                    await asyncio.sleep(2)

                # Update stats after multipliers
                for hero in heroes:
                    hero["stats"], hero["multipliers"], \
                        hero["current_state"]["weapon_skill_cd"] = \
                        self.updateStatsAfterMultiplierDebuff(
                            hero, hero["multipliers"]
                        )

                # Update stats after debuffs
                for hero in heroes:
                    hero["stats"], hero["debuffs"], \
                        hero["current_state"]["weapon_skill_cd"] = \
                        self.updateStatsAfterMultiplierDebuff(
                            hero, hero["debuffs"]
                        )

                # Update cooldown and more
                if heroes[first]["current_state"]["weapon_skill_cd"] != 0:
                    heroes[first]["current_state"]["weapon_skill_cd"] = \
                        heroes[first]["current_state"]["weapon_skill_cd"] - 1

                if heroes[first]["current_state"]["stunned"] != 0:
                    heroes[first]["current_state"]["stunned"] = \
                        heroes[first]["current_state"]["stunned"] - 1

                if heroes[first]["current_state"]["evade_cd"] != 0:
                    heroes[first]["current_state"]["evade_cd"] = \
                        heroes[first]["current_state"]["evade_cd"] - 1

                if heroes[first]["current_state"]["on_normal_skill_cd"] != 0:
                    heroes[first]["current_state"]["on_normal_skill_cd"] = \
                        heroes[first]["current_state"]["on_normal_skill_cd"] - 1

                if heroes[first]["current_state"]["on_hit_skill_cd"] != 0:
                    heroes[first]["current_state"]["on_hit_skill_cd"] = \
                        heroes[first]["current_state"]["on_hit_skill_cd"] - 1

                # Multiplier and debuff count
                for multi_count in heroes[first]["multipliers"]:
                    multi_count["count"] = multi_count["count"] - 1

                for debuff_count in heroes[first]["debuffs"]:
                    debuff_count["count"] = debuff_count["count"] - 1

                # If it ends, then break.
                if end:
                    break

            if not end:
                # Increase round count
                round = round + 1
            else:
                if winner and loser:
                    trophy_win = 25
                    trophy_lose = -10
                    hero_exp_win = 50
                    hero_exp_lose = 30
                    user_exp_win = 100
                    user_exp_lose = 70
                    gems = 1000

                    db_ailie = Database()

                    db_ailie.update_trophy(winner["guardian_id"], trophy_win)
                    db_ailie.update_trophy(loser["guardian_id"], trophy_lose)

                    db_ailie.increase_arena_wins(winner["guardian_id"])
                    db_ailie.increase_arena_losses(loser["guardian_id"])

                    db_ailie.update_hero_exp(
                        winner["guardian_id"],
                        winner["hero_name"],
                        hero_exp_win
                    )
                    db_ailie.update_hero_exp(
                        loser["guardian_id"], loser["hero_name"], hero_exp_lose)

                    db_ailie.store_gems(winner["guardian_id"], gems)

                    db_ailie.update_user_exp(
                        winner["guardian_id"], user_exp_win)
                    db_ailie.update_user_exp(
                        loser["guardian_id"], user_exp_lose)

                    db_ailie.disconnect()

                    await ctx.send(
                        f"<@{winner['guardian_id']}>, wins and obtained "
                        + f"{trophy_win} 🏆 and {gems} 💎."
                    )
                    await asyncio.sleep(2)
                    await ctx.send(
                        f"<@{loser['guardian_id']}>, "
                        + f"losses {-1 * trophy_lose} 🏆. Boooooo."
                    )
                    await asyncio.sleep(2)
                    break


def setup(bot):
    bot.add_cog(PvP(bot))
