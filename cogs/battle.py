#!/usr/bin/env python

from copy import deepcopy
import asyncio
import random
import discord
from discord.ext import commands
from helpers.database import Database


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def addWeaponStatsToHero(self, weapon, hero):
        for h in hero:
            if h in weapon:
                hero[h] = hero[h] + weapon[h]

        return hero

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
        await asyncio.sleep(1.5)

        return victim["stats"], victim["multipliers"]

    async def debuff(self, ctx, actor, victim, debuff, debuffs, count):
        debuffs_buffer = self.initDebuff(count)

        if debuff.startswith("debuff"):
            deb = debuff[7:]
        else:
            deb = debuff

        debuffs_buffer[deb] = -1 * debuffs[debuff]

        # Enter debuffs in a list of many debuffs
        victim["debuffs"].append(debuffs_buffer)

        # Update stats after debuff
        victim["stats"], \
            victim["debuffs"], \
            victim["current_state"]["weapon_skill_cd"] = \
            self.updateStatsAfterMultiplierDebuff(
                victim, victim["debuffs"])

        debuff_readable = self.translateToReadableFormat(deb)
        await ctx.send(
            f"{actor['color']} **{victim['hero_name']}**'s "
            + f"{debuff_readable} is debuffed!"
        )
        await asyncio.sleep(1.5)

        return victim["stats"], victim["debuffs"]

    async def removeAllDebuff(self, ctx, hero):
        if len(hero["debuffs"]) > 0:
            for debuff in hero["debuffs"]:
                # Calculate new stats when debuff is removed
                for debuff_in_debuff in debuff:
                    if debuff_in_debuff not in ["count", "check"]:
                        if debuff_in_debuff in ["attack", "hp", "def"]:
                            hero["stats"][debuff_in_debuff] = round(
                                hero["stats"][debuff_in_debuff]
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
        await asyncio.sleep(1.5)

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
                            if multiplier_debuff == "wsrs" and \
                                    multipliers_debuffs[multiplier_debuff] > 0:
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
        round_reset = False
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
            await asyncio.sleep(1.5)

        if not miss:
            if total_damage < 0:
                total_damage = 0

            victim["stats"]["hp"] = (
                victim["stats"]["hp"]
                - total_damage
            )

            await ctx.send(
                f"{actor['color']} **{actor['hero_name']}** used "
                + f"{move_type} and dealt `{total_damage:,d}` "
                + f"{damage_type}!"
            )
            await asyncio.sleep(1.5)

            if victim["stats"]["hp"] < 0:
                round_reset = True
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
                    + "** has died!"
                )
                await asyncio.sleep(1.5)

            else:
                await ctx.send(
                    f"{victim['color']} "
                    + f"**{victim['hero_name']}"
                    + "**'s HP reduced! "
                    + f"`{victim['stats']['hp']}"
                    + f"`/`{victim['max_hp']}` HP left!"
                )
                await asyncio.sleep(1.5)

                if move_type == "weapon skill":
                    victim["current_state"]["stunned"] = 3
                    await ctx.send(
                        f"{actor['color']} "
                        + f"**{actor['hero_name']}** "
                        + "used weapon skill and stunned "
                        + f"**{victim['hero_name']}** "
                        + "for 3 of their turns!"
                    )
                    await asyncio.sleep(1.5)

        return victim, round_reset, winner, loser

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
        await asyncio.sleep(1.5)
        await ctx.send(
            f"{hero['color']} **{hero['hero_name']}** current HP is "
            + f"`{hp_after_heal}`/`{hero['max_hp']}`."
        )
        await asyncio.sleep(1.5)

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
            if not stat.startswith("all"):
                s = stat

                if s in ["attack", "def", 'hp']:
                    stats[s] = round(stats[s] + ((buffs[stat]/100) * stats[s]))
                else:
                    stats[s] = stats[s] + buffs[stat]

        return stats

    def multiplyStatsWithLevels(self, stats, hero_level, user_level):
        # Increase overall stats
        for stat in stats:
            if stat in ["attack"]:
                increase = 20
                stats[stat] = round(
                    stats[stat]
                    + ((increase/100) * stats[stat] * hero_level)
                    + ((increase/100) * stats[stat] * user_level)
                )
            elif stat in ["hp"]:
                increase = 5
                stats[stat] = round(
                    stats[stat]
                    + ((increase/100) * stats[stat] * hero_level)
                    + ((increase/100) * stats[stat] * user_level)
                )
            elif stat in ["def"]:
                increase = 1
                stats[stat] = round(
                    stats[stat]
                    + ((increase/100) * stats[stat] * hero_level)
                    + ((increase/100) * stats[stat] * user_level)
                )
            else:
                pass

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
            "on_normal_instant_skill_cd": 1,
            "on_hit_instants_skill_cd": 1,
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

    def get_equip_information(self, guardian_id, hero):
        db_ailie = Database()
        inventory_id = db_ailie.get_inventory_id(guardian_id)
        hero_full_name = db_ailie.get_hero_full_name(hero)
        hero_id = db_ailie.get_hero_id(hero_full_name)
        equip_id = db_ailie.get_exclusive_weapon_id(hero_id)
        no_ewp = {
            "stats": {},
            "buffs": {},
            "weapon_skill": {},
            "triggers": {},
            "acquired": {"level": {}, "roll": {}},
            "instant_triggers": {}
        }

        if not equip_id:
            return no_ewp

        obtained = db_ailie.is_equip_obtained(guardian_id, equip_id)

        if not obtained:
            return no_ewp

        equip_acquired = db_ailie.get_equip_acquired_details(
            inventory_id, equip_id
        )
        (
            equip_stats,
            equip_buffs,
            equip_skill,
            equip_triggers,
            equip_instant_triggers
        ) = db_ailie.get_equip_stats(equip_id)

        return {
            "stats": equip_stats,
            "buffs": equip_buffs,
            "weapon_skill": equip_skill,
            "triggers": equip_triggers,
            "acquired": equip_acquired,
            "instant_triggers": equip_instant_triggers
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

    def hasTeam(self, guardian_id, key):
        db_ailie = Database()
        exist = db_ailie.is_team_exists(guardian_id, key)

        if exist:
            return True
        else:
            return False

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
            + "\n`EVADE` is used to increase `speed` for a while "
            + "which may cause opponent "
            + "to miss their attacks. `Surrender` is used to surrender."
        ),
        aliases=["ar"]
    )
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def arena(self, ctx, mention: discord.Member = None, key="main"):
        # Check if mention is present
        if not mention:
            await ctx.send("You forgot to mention who to fight.")
            return

        db_ailie = Database()
        if key == "main":
            if not db_ailie.is_team_exists(ctx.author.id, "main"):
                await ctx.send(
                    "You need to set a team with `a;team`."
                )
                db_ailie.disconnect()
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

        # Check if users has the team chosen
        if not self.hasTeam(challenger_id, key):
            await ctx.send(f"<@{challenger_id}>, you don't have that team.")
            db_ailie.disconnect()
            return

        # Ask for opponent's team to use
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
                    f"<@{opponent_id}>, reply with your team choice."
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

        def confirm_team(message):
            return message.author.id == opponent_id

        # Wait for team chosen
        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_team, timeout=60
            )
            # Check if users has the team chosen
            opponent_team = msg.content
            if not self.hasTeam(opponent_id, opponent_team):
                await ctx.send(f"<@{opponent_id}>, you don't have that team.")
                db_ailie.disconnect()
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

        # If the mentioned player is the same player.
        if challenger_id == opponent_id:
            await ctx.send(
                "Sike! You really thought I'm gonna let "
                + f"you fight yourself eh, <@{challenger_id}>?"
            )
            return

        hero = db_ailie.get_all_heroes_from_team(challenger_id, key)
        opponent_hero = db_ailie.get_all_heroes_from_team(
            opponent_id, opponent_team)

        hero_buffer = []
        count = 0
        for h in hero:
            if h != 0:
                hero_buffer.append(db_ailie.get_hero_name_from_id(h))
                count += 1

        if count > 3:
            await ctx.send(
                f"<@{challenger_id}>, only a team with "
                + "maximum 3 heroes is accepted."
            )
            return

        opponent_hero_buffer = []
        count = 0
        for oh in opponent_hero:
            if oh != 0:
                opponent_hero_buffer.append(db_ailie.get_hero_name_from_id(oh))
                count += 1

        if count > 3:
            await ctx.send(
                f"<@{opponent_id}>, only a team with "
                + "maximum 3 heroes is accepted."
            )

        hero = hero_buffer[:]
        opponent_hero = opponent_hero_buffer[:]

        # Get users' hero information
        heroes = [[], []]
        for name in hero:
            hero_information = self.get_hero_information(challenger_id, name)
            heroes[0].append(hero_information)

        for name in opponent_hero:
            hero_information = self.get_hero_information(opponent_id, name)
            heroes[1].append(hero_information)

        # Get users' exclusive weapon information
        equips = [[], []]
        for name in hero:
            equip_information = self.get_equip_information(challenger_id, name)
            equips[0].append(equip_information)

        for name in opponent_hero:
            equip_information = self.get_equip_information(opponent_id, name)
            equips[1].append(equip_information)

        # Set all the other information needed for a proper battle
        # Associate user details with the heroes
        for hero in heroes:
            for h in hero:
                if heroes.index(hero) == 0:
                    h["guardian_id"] = challenger_id
                    h["guardian_name"] = challenger_name
                    h["color"] = "🔴"
                else:
                    h["guardian_id"] = opponent_id
                    h["guardian_name"] = opponent_name
                    h["color"] = "🔵"

        # Initialize hero current state, multipliers, and debuffs.
        for hero in heroes:
            for h in hero:
                h["current_state"] = self.initCurrentState()
                h["multipliers"] = []
                h["debuffs"] = []

        # Initialize extra stats
        for hero in heroes:
            for h in hero:
                h["stats"] = self.initExtraStats(h["stats"])

        # Initialize element stats
        for hero in heroes:
            for h in hero:
                h["stats"] = self.initElementStats(h["stats"])

        # Modify stats depending on hero and user level
        for hero in heroes:
            for h in hero:
                db_ailie = Database()
                user_level = db_ailie.get_user_level(h["guardian_id"])
                h["stats"] = self.multiplyStatsWithLevels(
                    h["stats"], h["acquired"]["level"], user_level)
                db_ailie.disconnect()

        # Modify weapon stats depending on weapon level
        # Weapon is not affected by user level
        for equip in equips:
            for e in equip:
                db_ailie = Database()
                if len(e) != 0:
                    e["stats"] = self.multiplyStatsWithLevels(
                        e["stats"], e["acquired"]["level"],
                        e["acquired"]["roll"])
                db_ailie.disconnect()

        # Add the stats from weapon to to hero
        # Add weapon skill and instant triggers to heroes as well
        chal_or_opp = 0
        for hero in heroes:
            hero_in_order = 0
            for h in hero:
                h["stats"] = self.addWeaponStatsToHero(
                    equips[chal_or_opp][hero_in_order]["stats"],
                    h["stats"]
                )
                h["weapon_skill"] = \
                    equips[chal_or_opp][hero_in_order]["weapon_skill"]
                h["instant_triggers"] = \
                    equips[chal_or_opp][hero_in_order]["instant_triggers"]
                hero_in_order += 1
            chal_or_opp += 1

        # Modify stats based on buffs
        for hero in heroes:
            for h in hero:
                h["stats"] = self.multiplyHeroBuffs(h["stats"], h["buffs"])

        chal_or_opp = 0
        for hero in heroes:
            hero_in_order = 0
            for h in hero:
                h["stats"] = self.multiplyHeroBuffs(
                    h["stats"],
                    equips[chal_or_opp][hero_in_order]["buffs"]
                )
                hero_in_order += 1
            chal_or_opp += 1

        # Update stats based on Party Buffs
        challenger_party_buffs = {}
        for hero in heroes[0]:
            for buff in hero["buffs"]:
                if buff.startswith("all"):
                    b = buff[4:]

                    if b not in challenger_party_buffs:
                        challenger_party_buffs[b] = hero["buffs"][buff]
                    else:
                        challenger_party_buffs[b] = \
                            challenger_party_buffs[b] + hero["buffs"][buff]

        opponent_party_buffs = {}
        for hero in heroes[0]:
            for buff in hero["buffs"]:
                if buff.startswith("all"):
                    b = buff[4:]

                    if b not in opponent_party_buffs:
                        opponent_party_buffs[b] = hero["buffs"][buff]
                    else:
                        opponent_party_buffs[b] = \
                            opponent_party_buffs[b] + hero["buffs"][buff]

        for hero in heroes[0]:
            hero["stats"] = \
                self.multiplyHeroBuffs(hero["stats"], challenger_party_buffs)

        for hero in heroes[1]:
            hero["stats"] = \
                self.multiplyHeroBuffs(hero["stats"], opponent_party_buffs)

        # Update Max HP to a separate key
        for hero in heroes:
            for h in hero:
                h["max_hp"] = h["stats"]["hp"]

        # Get new weapon skill cooldown after stats have been modified
        for hero in heroes:
            for h in hero:
                h["current_state"]["weapon_skill_cd"] = \
                    self.calcWeapSkillCooldown(
                        h["current_state"]["weapon_skill_cd"],
                        h["stats"]["wsrs"]
                    )

        # Start arena between heroes
        ends_for_real = False
        winner = {}
        loser = {}
        round_num = 1
        total_round_num = 1
        left = False
        chal_hero_order = 0
        opp_hero_order = 0
        chal_hero_died = 0
        opp_hero_died = 0

        # Assign variables for heroes
        heroes_bench = deepcopy(heroes)
        heroes = []
        heroes.append(deepcopy(heroes_bench[0][chal_hero_order]))
        heroes.append(deepcopy(heroes_bench[1][opp_hero_order]))

        while True:
            round_reset = False

            # Show available moves for each player
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                icon_url=self.bot.user.avatar_url,
                name=f"Round {round_num}"
            )
            embed.set_footer(
                text=(
                    "Enter the number or the first letter of the move."
                    + "\nTo surrender, enter `surrender` or `five`."
                )
            )

            for hero in heroes:
                index = heroes.index(hero)
                if index == 0:
                    other_index = 1
                    hero_died = chal_hero_died
                    hero_order = chal_hero_order
                else:
                    other_index = 0
                    hero_died = opp_hero_died
                    hero_order = opp_hero_order

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

                # Display the details
                team = ""
                check_died = 0
                for hero_tmp in heroes_bench[index]:
                    ind = "⏱️ "
                    if hero_died > check_died:
                        ind = "❌ "
                        check_died += 1

                    if heroes_bench[index][hero_order] == hero_tmp:
                        ind = "➡️ "

                    if heroes_bench[index].index(hero_tmp) == 0:
                        team = f"{ind}{hero_tmp['hero_name']}"
                    else:
                        team = f"{team}\n{ind}{hero_tmp['hero_name']}"

                line_consumed = len(heroes_bench[index])
                while line_consumed < 3:
                    team = f"{team}\n🚫 No Hero"
                    line_consumed += 1

                hp_percentage = round(
                    (hero["stats"]["hp"] / hero["max_hp"]) * 100)
                hp = (
                    f"**HP {hp_percentage}%**\n"
                    + f"`{hero['stats']['hp']:,d}`/`{hero['max_hp']:,d}`"
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
                    value=f"{team}\n\n{hp}\n\n{moves}"
                )

            await ctx.send(embed=embed)
            await asyncio.sleep(5)

            # Increase attack on round 16 and later
            rage = 50
            if round_num > 7:
                for hero in heroes:
                    hero["stats"]["attack"] = hero["stats"]["attack"] \
                        + ((rage / 100) * hero["stats"]["attack"])

                await ctx.send(
                    "*Every heroes felt the tension and "
                    + f"increased their attack by {rage}%!*"
                )
                await asyncio.sleep(1.5)

            # Prompt for each player to enter their move
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
                            "a", "w", "ws", "c", "cs", "e", "surrender",
                            "1", "2", "3", "4", "five"
                        ]:
                    choices.append([message.author.id, message.content.lower()])
                    players.remove(message.author.id)
                    if len(players) == 0:
                        return True
                return False

            try:
                await self.bot.wait_for("message", check=check, timeout=60)
                for choice in choices:
                    if choice[1].lower() in ["surrender", "five"]:
                        left = True
                        if choices.index(choice) != 0:
                            popped = choices.pop()
                            choices.insert(0, popped)
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

                    await ctx.send(
                        "Don't get involved in something you can't finish, "
                        + f"<@{quitter_id}>!"
                    )

                    if total_round_num >= 5:
                        winner = {
                            "guardian_id": winner_id,
                            "hero_name": winner_hero
                        }
                        loser = {
                            "guardian_id": quitter_id,
                            "hero_name": quitter_hero
                        }
                        choices.insert(0, [quitter_id, "five"])
                        left = True
                    else:
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
                if not left:
                    await ctx.send(f"<@{heroes[first]['guardian_id']}>'s turn.")
                    await asyncio.sleep(1.5)

                # Move choices available for players
                # Attack Move
                if choice[1].lower() in ["a", "1"] and \
                        heroes[first]["current_state"]["stunned"] == 0:
                    move_type = "attack"
                    percent_damage = heroes[first]["stats"]["normal"]
                    onisc = "on_normal_instant_skill_cd"
                    ohisc = "on_hit_instants_skill_cd"

                    # Trigger instants buffs on attack
                    if heroes[first]["current_state"][onisc] \
                            == 0:
                        if "on_normal" in heroes[first]["instant_triggers"]:
                            heroes = await self.goingToAttackPleaseBuff(
                                ctx, heroes, first, second,
                                heroes[first]["instant_triggers"]["on_normal"],
                            )
                        heroes[first]["current_state"][onisc] = 1

                    # Trigger instant buffs to victim
                    if heroes[second]["current_state"][ohisc] == 0:
                        if "on_hit" in heroes[second]["instant_triggers"]:
                            heroes = await self.gotHitPleaseBuff(
                                ctx, heroes, first, second,
                                heroes[second]["instant_triggers"]["on_hit"],
                            )
                        heroes[second]["current_state"][ohisc] = 1

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
                    heroes[second], \
                        round_reset, winner, loser = await self.attack(
                            ctx, heroes[first], heroes[second],
                            move_type, percent_damage
                        )

                # Weapon Skill Move
                elif choice[1].lower() in ["w", "ws", "2"] and \
                        heroes[first]["current_state"]["stunned"] == 0:
                    if heroes[first]["current_state"]["weapon_skill_cd"] == 0:
                        move_type = "weapon skill"
                        if "damage" in heroes[first]["weapon_skill"]:
                            percent_damage = \
                                heroes[first]["weapon_skill"]["damage"]
                        else:
                            percent_damage = 100
                        onisc = "on_normal_instant_skill_cd"
                        ohisc = "on_hit_instants_skill_cd"

                        # Trigger instants buffs on attack
                        if heroes[first]["current_state"][onisc] \
                                == 0:
                            if "on_normal" in heroes[first]["instant_triggers"]:
                                heroes = await self.goingToAttackPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[first]["instant_triggers"]
                                    ["on_normal"],
                                )
                            heroes[first]["current_state"][onisc] = 1

                        # Trigger instant buffs to victim
                        if heroes[second]["current_state"][ohisc] == 0:
                            if "on_hit" in heroes[second]["instant_triggers"]:
                                heroes = await self.gotHitPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[second]["instant_triggers"]
                                    ["on_hit"],
                                )
                            heroes[second]["current_state"][ohisc] = 1

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

                        # Deal damage
                        if percent_damage is not None:
                            heroes[second], \
                                round_reset, winner, loser = await self.attack(
                                ctx, heroes[first], heroes[second],
                                move_type, percent_damage
                            )

                        heroes[first]["current_state"]["weapon_skill_cd"] = \
                            self.calcWeapSkillCooldown(
                                5, heroes[first]["stats"]["wsrs"])
                    else:
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[first]['hero_name']}**'s "
                            + "weapon skill is on cooldown!"
                        )
                        await asyncio.sleep(1.5)

                # Chain Skill Move
                elif choice[1].lower() in ["c", "cs", "3"] and \
                        heroes[first]["current_state"]["stunned"] == 0:
                    if heroes[second]["current_state"]["stunned"] != 0:
                        move_type = "chain skill"
                        if "damage" in heroes[first]["skill"]:
                            percent_damage = heroes[first]["skill"]["damage"]
                        else:
                            percent_damage = None

                        cs = "current_state"
                        onisc = "on_normal_instant_skill_cd"
                        ohisc = "on_hit_instants_skill_cd"
                        did_cs = False

                        # Trigger instants buffs on attack
                        if heroes[first]["current_state"][onisc] \
                                == 0:
                            if "on_normal" in heroes[first]["instant_triggers"]:
                                heroes = await self.goingToAttackPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[first]["instant_triggers"]
                                    ["on_normal"],
                                )
                            heroes[first]["current_state"][onisc] = 1

                        # Trigger instant buffs to victim
                        if heroes[second]["current_state"][ohisc] == 0:
                            if "on_hit" in heroes[second]["instant_triggers"]:
                                heroes = await self.gotHitPleaseBuff(
                                    ctx, heroes, first, second,
                                    heroes[second]["instant_triggers"]
                                    ["on_hit"],
                                )
                            heroes[second]["current_state"][ohisc] = 1

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
                            did_cs = True

                        # Deal damage
                        if percent_damage is not None:
                            heroes[second], \
                                round_reset, winner, loser = await self.attack(
                                ctx, heroes[first], heroes[second],
                                move_type, percent_damage
                            )
                            did_cs = True

                        if did_cs and not round_reset:
                            heroes[second]["current_state"]["stunned"] = 0
                            await ctx.send(
                                f"{heroes[second]['color']} "
                                + f"**{heroes[second]['hero_name']}** "
                                + "broke free from stun!"
                            )
                            await asyncio.sleep(1.5)
                    else:
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[second]['hero_name']}** "
                            + "is not stunned!"
                        )
                        await asyncio.sleep(1.5)

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
                            + "tries to evade the attack "
                            + "in next turn!"
                        )
                        await asyncio.sleep(1.5)
                    else:
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[first]['hero_name']}** "
                            + "can't use evade right now!"
                        )
                        await asyncio.sleep(1.5)

                # Surrender
                elif choice[1].lower() in ["surrender", "five"]:
                    round_reset = True
                    ends_for_real = True

                    await ctx.send(
                        f"<@{heroes[first]['guardian_id']}> surrendered!")
                    await asyncio.sleep(1.5)

                    if total_round_num >= 3:
                        winner = {
                            "guardian_id": heroes[second]["guardian_id"],
                            "hero_name": heroes[second]["hero_name"]
                        }
                        loser = {
                            "guardian_id": heroes[first]["guardian_id"],
                            "hero_name": heroes[first]["hero_name"]
                        }
                    else:
                        return

                # Pass everything else
                else:
                    pass

                if not round_reset:
                    cs = "current_state"

                    # If enemy is stunned
                    if heroes[first]["current_state"]["stunned"] != 0:
                        await ctx.send(
                            f"{heroes[first]['color']} "
                            + f"**{heroes[first]['hero_name']}** "
                            + "is stunned!"
                        )
                        await asyncio.sleep(1.5)

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
                            heroes[first]["current_state"]["weapon_skill_cd"] \
                            - 1

                    if heroes[first]["current_state"]["stunned"] != 0:
                        heroes[first]["current_state"]["stunned"] = \
                            heroes[first]["current_state"]["stunned"] - 1
                        if heroes[first]["current_state"]["stunned"] == 0:
                            await ctx.send(
                                f"{heroes[first]['color']} "
                                + f"**{heroes[first]['hero_name']}** "
                                + "broke free from stun!"
                            )

                    if heroes[first]["current_state"]["evade_cd"] != 0:
                        heroes[first]["current_state"]["evade_cd"] = \
                            heroes[first]["current_state"]["evade_cd"] - 1

                    if heroes[first]["current_state"]["on_normal_skill_cd"] \
                            != 0:
                        heroes[first]["current_state"]["on_normal_skill_cd"] = \
                            heroes[first][cs]["on_normal_skill_cd"] \
                            - 1

                    if heroes[first]["current_state"]["on_hit_skill_cd"] != 0:
                        heroes[first]["current_state"]["on_hit_skill_cd"] = \
                            heroes[first]["current_state"]["on_hit_skill_cd"] \
                            - 1

                    onisc = "on_normal_instant_skill_cd"
                    if heroes[first]["current_state"][onisc] != 0:
                        heroes[first]["current_state"][onisc] = \
                            heroes[first]["current_state"][onisc] - 1

                    ohisc = "on_hit_instants_skill_cd"
                    if heroes[first]["current_state"][ohisc] != 0:
                        heroes[first]["current_state"][ohisc] = \
                            heroes[first]["current_state"][ohisc] - 1

                    # Multiplier and debuff count
                    for multi_count in heroes[first]["multipliers"]:
                        multi_count["count"] = multi_count["count"] - 1

                    for debuff_count in heroes[first]["debuffs"]:
                        debuff_count["count"] = debuff_count["count"] - 1

                # If it ends, then break.
                if round_reset:
                    if second == 0:
                        chal_hero_died += 1
                        chal_hero_order += 1

                        second_hero_died = chal_hero_died
                        second_hero_order = chal_hero_order
                        first_hero_order = opp_hero_order
                    else:
                        opp_hero_died += 1
                        opp_hero_order += 1

                        second_hero_died = opp_hero_died
                        second_hero_order = opp_hero_order
                        first_hero_order = chal_hero_order

                    if second_hero_died == len(heroes_bench[second]):
                        ends_for_real = True
                    else:
                        heroes[second] = \
                            heroes_bench[second][second_hero_order]
                        hp_buffer = heroes[first]["stats"]["hp"]
                        heroes[first] = \
                            heroes_bench[first][first_hero_order]
                        heroes[first]["stats"]["hp"] = hp_buffer

                    break
            if not round_reset:
                # Increase round count
                round_num = round_num + 1
                total_round_num = total_round_num + 1
            elif round_reset and not ends_for_real:
                round_num = 1
                total_round_num = total_round_num + 1
            elif ends_for_real:
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
                        + f"`{trophy_win:,d}` trophies and `{gems:,d}` gems."
                    )
                    await asyncio.sleep(1.5)
                    await ctx.send(
                        f"<@{loser['guardian_id']}>, "
                        + f"losses `{-1 * trophy_lose:,d}` trophies."
                    )
                    await asyncio.sleep(1.5)
                    break


def setup(bot):
    bot.add_cog(Battle(bot))
