#!/usr/bin/env python

import asyncio
import random
import discord
from discord.ext import commands
from helpers.database import Database


class Summon(commands.Cog):
    def __init__(self, bot):
        # Bot assigned to class
        self.bot = bot

        # Initialize database for Ailie
        db_ailie = Database()

        # Get all the data for heroes and pick up heroes
        self.heroes = db_ailie.get_pool("heroes", "normal", [[], [], []])
        self.pick_up_heroes = db_ailie.get_pool("heroes", "pickup", [])

        # Weights declaration for probability upon hero summons
        self.heroes_weights = [78.250, 19.000, 2.750]
        self.heroes_pick_up_weights = [78.250, 19.000, 1.375, 1.375]
        self.heroes_last_slot_weights = [97.25, 2.75]

        # Get all the data for heroes and pick up heroes
        self.equipments = db_ailie.get_pool(
                "equipments", "normal", [[], [], [], [], []])
        self.pick_up_equipments = db_ailie.get_pool(
                "equipments", "pickup", [])

        # Weights declaration for probability upon hero summons
        self.equipments_weights = [58.000, 27.000, 9.000, 3.000, 3.000]
        self.equipments_pick_up_weights = [
            58.000, 27.000, 9.000, 3.000, 1.000, 2.000
        ]
        self.equipments_last_slot_weights = [94, 3, 3]

        # Disconnect database for Ailie
        db_ailie.disconnect()

    def grantExpOnDupe(self, guardian_id, boxes, type):
        exp = 100

        db_ailie = Database()
        for box in boxes:
            if type in ["h", "hero", "heroes"]:
                requirement = "★★★ "
                if box.startswith(requirement):
                    hero_id = db_ailie.get_hero_id(box[4:])
                    if db_ailie.is_hero_obtained(guardian_id, hero_id):
                        db_ailie.update_user_exp(guardian_id, exp)
            elif type in ["e", "eq", "equip", "equipment", "equipments"]:
                requirement = "★★★★★ [Ex]"
                another_requirement = "★★★★ [Ex]"
                if box.startswith(requirement) or \
                        box.startswith(another_requirement):
                    equip_id = db_ailie.get_equip_id(box[box.find("]"):][2:])
                    if db_ailie.is_equip_obtained(guardian_id, equip_id):
                        db_ailie.update_user_exp(guardian_id, exp)
            else:
                pass

    # Summons are determined to check for certain requirements
    def checkWhatIsSummoned(
            self, r, target, not_easter_eggs, easter_eggs=None):
        if not_easter_eggs["heroes_check"]:
            if "★★★" in r:
                not_easter_eggs["white_box"] = True
            if r == target:
                not_easter_eggs["obtainedPickup"] = True
            if "Ailie" in r:
                easter_eggs["ailie"] = True
            if "Alef" in r:
                easter_eggs["alef"] = True
            if "Plitvice" in r:
                easter_eggs["plitvice"] = True
            if "Lapice" in r:
                easter_eggs["lapice"] = True
            if "Nari" in r:
                easter_eggs["nari"] = True
            if "Lupina" in r:
                easter_eggs["lupina"] = True
            if "Idol" in r:
                easter_eggs["idol"] = True
        else:
            if "[Ex]" in r:
                not_easter_eggs["white_box"] = True
            if "★★★★ [Ex]" in r:
                not_easter_eggs["four_ex"] = True
            if "★★★★★ [Ex]" in r:
                not_easter_eggs["five_ex"] = True
            if r == target:
                not_easter_eggs["obtainedPickup"] = True

        return not_easter_eggs, easter_eggs

    # Replies are sent back according to the summons obtained
    def getRepliesForSpecificSummons(
            self, ctx, target, not_easter_eggs, easter_eggs):
        # Initialize reply variable
        reply = ""

        if not_easter_eggs["heroes_check"]:
            type = "3 star hero"
            type_short = "hero"
        else:
            type = "exclusive weapon"
            type_short = "weapon"

        # Get funky replies
        # Easter Eggs counter
        useless_check = False
        ailie_check = False
        for eg in easter_eggs:
            if easter_eggs["ailie"]:
                ailie_check = True
            if easter_eggs[eg]:
                if eg != "ailie":
                    useless_check = True
                    break

        # Fail summons but obtained ailie
        if not not_easter_eggs["white_box"] and ailie_check \
                and not_easter_eggs["heroes_check"]:
            reply = [
                f"Think positive, <@{ctx.author.id}>! "
                + "At least you got me :D"
            ]
        # Fail summons without ailie
        elif not not_easter_eggs["white_box"] and not ailie_check:
            reply = [
                f"You just suck at gachas, <@{ctx.author.id}>..",
                f"Try harder, <@{ctx.author.id}>.",
                f"Ermmm.. <@{ctx.author.id}>. Oh well. You've tried."
            ]
        # Lucky summons without useless things in normal banner
        elif not_easter_eggs["white_box"] and not useless_check and \
                not not_easter_eggs["obtainedPickup"] and not target:
            # "Lucky" but only with four star exclusive weapon
            if not_easter_eggs["four_ex"] and not not_easter_eggs["five_ex"]:
                reply = [
                    f"Oh.. Its just a four star {type}. But thats better "
                    + f"than nothing. Right, <@{ctx.author.id}>?"
                ]
            # Replies for the lucky pulls that aren't fake
            else:
                reply = [
                    f"WOW! W-w-waaaiittt a second, <@{ctx.author.id}>.. "
                    + f"Is that a freaking {type}?!",
                    f"{type.capitalize()} comes to you like a magnet, "
                    + f"<@{ctx.author.id}>. "
                    + "Yeah I said it.",
                    f"Yeah. You got {type}, <@{ctx.author.id}>. "
                    + "I can see that. But how many gems has it been?"
                ]
        # Lucky summons with pick up banners
        elif not_easter_eggs["white_box"] and not_easter_eggs["obtainedPickup"]:
            reply = [
                f"WOHOOOOOOOOOOOOOOOOOO, <@{ctx.author.id}>! You got the "
                + f"pick up {type_short}!",
                f"This calls for a treat, <@{ctx.author.id}>! Easy-peasy.",
                f"<@{ctx.author.id}>, what kind of luck do you have? Are you "
                + "somekind of luck beast or something?!"
            ]
        # Lucky summons but you get useless things in normal banner.
        elif not_easter_eggs["white_box"] and useless_check and \
                not not_easter_eggs["obtainedPickup"]:
            if easter_eggs["alef"]:
                reply = [
                    f"LOL. You've got Alef instead, <@{ctx.author.id}>. "
                    + "Congratulations?"
                ]
            if easter_eggs["plitvice"]:
                reply = [
                    "3 STAR WOW! Wait.. Oh. Its Plitvice. "
                    + f"Good for you, <@{ctx.author.id}>."
                ]
            if easter_eggs["lapice"]:
                reply = [
                    f"Huh? Lapice? Whats that, <@{ctx.author.id}>?"
                ]
            if easter_eggs["nari"]:
                reply = [
                    f"YES, <@{ctx.author.id}>! NARI! But shhhhhh! Keep it "
                    + "quiet. Some YouTuber doesn't seem too fond of Nari. "
                    + "*smirks*"
                ]
            if easter_eggs["lupina"]:
                reply = [
                    "I don't know if you should be happy with "
                    + f"this, <@{ctx.author.id}>.."
                ]
            if easter_eggs["idol"]:
                reply = [
                    "Okay fine, Idol Eva is used more now in colosseum. "
                    + f"Maybe she's good after all. Right, <@{ctx.author.id}>"
                ]
        # Lucky summons but you get useless things in pick up banner
        elif not_easter_eggs["white_box"] and \
                not not_easter_eggs["obtainedPickup"] and target:
            reply = [
                f"I see {type}. But no {target}.. "
                + f"Sad life, <@{ctx.author.id}>.",
                "Well.. Not too shabby I guess. Right, "
                + f"<@{ctx.author.id}>? Although there's no {target}. "
                + "Hahaha.",
                f"At least there's {type}. It could've been worse, "
                + f"<@{ctx.author.id}>."
            ]
        # If this reply is chosen, then there's a check that is
        # not taken into account and should be taken care of
        # quickly. But the checks should cover all pulls.
        else:
            reply = [
                f"I don't know anymore, <@{ctx.author.id}>.."
            ]

        reply = random.choice(reply)

        return reply

    # Check if pick up chosen is available at the current time
    def checkPickUpAvailability(self, target, w):
        # Initialize variable to check invalid input
        invalid = False
        present = False
        target_banner = ""
        heroes_check = False

        # Check if the parameter send is lesser than 4 characters
        # If its lesser, then return error message
        if len(target) < 4:
            invalid = True

        # Check if the summon is for heroes or equipments
        if w == self.heroes_pick_up_weights:
            heroes_check = True

        # Check if selected pick up is available
        if heroes_check:
            for target_banner in self.pick_up_heroes:
                if target_banner.lower().__contains__(target.lower()):
                    present = True
                    break
        else:
            for target_banner in self.pick_up_equipments:
                if target_banner.lower().__contains__(target.lower()):
                    present = True
                    break

        return present, invalid, target_banner

    # Create new list with pick up included in a separate list in main list
    def pickUpPresent(self, target_banner, pool):
        # Initialize counters
        pick_up_pool = pool[:]
        heroes_check = False

        # Check which summon is running
        if pool == self.heroes:
            heroes_check = True

        if heroes_check:
            index = 2
        else:
            index = 4

        for heroes_list in pool:
            if target_banner in heroes_list:
                for hero_list in heroes_list:
                    if target_banner == hero_list:
                        buffer = pool[index][:]
                        buffer.remove(target_banner)
                        pick_up_pool.pop(index)
                        pick_up_pool.append(buffer)
                        pick_up_pool.append([target_banner, ])

                        break
                break

        return pick_up_pool, pick_up_pool[index+1][0]

    # Calculate the chances in summons
    def calcResults(
            self, ctx, one_or_ten, t, w, last_slot_weights, target=None):
        # Initialize value to return later
        reply = ""
        boxes = []

        # Check for summon values be it 10, 1 or invalid
        if one_or_ten == 10:
            results = random.choices(t, w, k=9)
        elif one_or_ten == 1:
            results = random.choices(t, w, k=1)
        else:
            results = [
                f"Hey, <@{ctx.author.id}>. "
                + "I don't think thats a valid summon value. LOL!",
                "Ermm.. its either 10 or 1! Get yourself corrected, "
                + f"<@{ctx.author.id}>!",
                f"You sure there's a {one_or_ten} summon, <@{ctx.author.id}>? "
                + "There's only 1 and 10 summon!"
            ]

            reply = random.choice(results)

        # Reduce 2700 gems or 300 gems depending on the count
        if one_or_ten == 10:
            gems = 2700
        else:
            gems = 300

        # Reduce gems in database after checking if balance is enough
        db_ailie = Database()
        enough_balance = db_ailie.spend_gems(ctx.author.id, gems)

        if not enough_balance:
            reply = f"You don't have enough gems, <@{ctx.author.id}>."

        # If the value is valid, then the statements here is executed
        if (one_or_ten == 10 or one_or_ten == 1) and enough_balance:
            db_ailie.update_user_exp(ctx.author.id, one_or_ten * 10)
            db_ailie.store_spent_gems(ctx.author.id, gems)
            db_ailie.store_summon_count(ctx.author.id, one_or_ten)
            # Variables used as a counter to check what is being summoned
            pity_check = False
            pity = False
            not_easter_eggs = {
                "heroes_check": False,
                "white_box": False,
                "obtainedPickup": False,
                "five_ex": False,
                "four_ex": False
            }
            easter_eggs = {
                "ailie": False,
                "alef": False,
                "plitvice": False,
                "lapice": False,
                "nari": False,
                "lupina": False,
                "idol": False
            }

            if w == self.heroes_weights or w == self.heroes_pick_up_weights:
                not_easter_eggs["heroes_check"] = True

            # Iterate through results
            for result in results:
                result = random.choices(result, k=1)
                for r in result:
                    if one_or_ten == 10:
                        # To determine if pity is deserved for last slot summon
                        if not_easter_eggs["heroes_check"]:
                            if r in ["★★ ", "★★★ "] and not pity_check:
                                pity = False
                                pity_check = True
                            else:
                                pity = True
                        else:
                            if r in ["★★★★ ", "★★★★★ "] and not pity_check:
                                pity = False
                                pity_check = True
                            else:
                                pity = True

                    # Check what is being summoned for specific replies
                    not_easter_eggs, easter_eggs = self.checkWhatIsSummoned(
                        r, target, not_easter_eggs, easter_eggs)

                    # Append the summons to boxes to be returned
                    boxes.append(r)

            # If the summon is with a value 10 and the summons from 1 until 9
            # is bad (No 2 star and above for heroes and no 4 star and above
            # for equipments), then, the user deserves higher rates
            if pity and one_or_ten == 10:
                if last_slot_weights == self.heroes_last_slot_weights:
                    target_pity = self.heroes[:]
                else:
                    target_pity = self.equipments[:]

                if not_easter_eggs["heroes_check"]:
                    target_pity.pop(0)
                else:
                    target_pity.pop(0)
                    target_pity.pop(0)

                results = random.choices(
                    target_pity, last_slot_weights, k=1)
                for pity_result in results:
                    p_r = random.choices(pity_result, k=1)
                    for pr in p_r:
                        # Check what is being summoned for specific replies
                        not_easter_eggs, easter_eggs = \
                                self.checkWhatIsSummoned(
                                        pr, target,
                                        not_easter_eggs, easter_eggs)

                        # Append the summons to boxes to be returned
                        boxes.append(pr)

            # If the user doesn't deserve pity, then continue with normal rates
            if not pity and one_or_ten == 10:
                results = random.choices(t, w, k=1)
                for not_pity_result in results:
                    n_p_r = random.choices(not_pity_result, k=1)
                    for npr in n_p_r:
                        # Check what is being summoned for specific replies
                        not_easter_eggs, easter_eggs = \
                                self.checkWhatIsSummoned(
                                        npr, target,
                                        not_easter_eggs, easter_eggs)

                        # Append the summons to boxes to be returned
                        boxes.append(npr)

            # Get specific replies corresponding to the summons
            reply = self.getRepliesForSpecificSummons(
                ctx, target, not_easter_eggs, easter_eggs)

        # Check if summon is for heroes or equipments
        its_heroes = False
        if w == self.heroes_weights or w == self.heroes_pick_up_weights:
            its_heroes = True

        # Record obtained units
        db_ailie = Database()
        if its_heroes:
            db_ailie.store_heroes(ctx.author.id, boxes)
        else:
            db_ailie.store_equipments(ctx.author.id, boxes)
        db_ailie.disconnect()

        return boxes, reply

    # Summon is displayed accordingly
    async def summonDisplay(self, ctx, one_or_ten, boxes, reply):
        msg = await ctx.send(
                f"Wait up, <@{ctx.author.id}>. Summoning {one_or_ten} now..")
        await asyncio.sleep(3)

        # Declare counter
        counter = 1
        # Iterate through box and edit messages to update the results
        boxes = iter(boxes)
        for box in boxes:
            if one_or_ten == 10:
                # Add five entry per request to lower occurance of rate limits
                await msg.edit(
                    content=msg.content
                    + f"\n{counter}. {box}"
                    + f"\n{counter + 1}. {next(boxes)}"
                    + f"\n{counter + 2}. {next(boxes)}"
                    + f"\n{counter + 3}. {next(boxes)}"
                    + f"\n{counter + 4}. {next(boxes)}"
                )
                await asyncio.sleep(2)
                counter += 5
            else:
                await msg.edit(content=msg.content + f"\n{counter}. {box}")
                await asyncio.sleep(2)
                counter += 1

        # Send the reply to fellow guardian
        await asyncio.sleep(1)
        msg = await msg.reply(reply)
        await msg.add_reaction("💎")

    # Lists the current pickup banner
    @commands.command(
        name="banner",
        brief="List current pickup banner.",
        description=(
            "Check the current pickup heroes and equipments. "
            + "This changes every two weeks or so."
            ),
        aliases=["ba"]
    )
    async def banner(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                    "Do `ailie;initialize` or `a;initialize` first "
                    + "before anything!"
                )
            db_ailie.disconnect()
            return

        db_ailie.disconnect()

        embed = discord.Embed(
                description="Current Pick Up Banners.",
                color=discord.Color.purple())

        # Store heroes pick up banner
        i = 1
        message = ""
        for pick_up_info in self.pick_up_heroes:
            message = message + f"\n{i}. {pick_up_info}"
            i += 1

        embed.add_field(name="Heroes", value=message, inline=False)

        # Store equipments pick up banner
        i = 1
        message = ""
        for pick_up_info in self.pick_up_equipments:
            message = message + f"\n{i}. {pick_up_info}"
            i += 1

        embed.add_field(name="Equipments", value=message, inline=False)
        embed.set_author(name="Ailie", icon_url=ctx.me.avatar_url)
        embed.set_footer(
                text="Pick Up Banners will change according to the "
                + "current banners in Guardian Tales.")
        await ctx.send(embed=embed)

    # Summon heroes or equipments either on the normal or pick up banne.
    @commands.command(
        name="summon",
        brief="Summon heroes or equipments.",
        description=(
            "Summon heroes or equipments on a pickup banner or "
            + "non-pickup banner."
            + "\n\n`type` can be either `hero` or `equip`."
            + "\n`count` can be `10` or `1`."
            + "\n`target` should be any heroes or equipments "
            + "that are currently in the pickup banner. "
            + "If target is not specified, then the summon will be done "
            + "on a non-pickup banner."
        ),
        aliases=["s"]
    )
    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    async def summon(self, ctx, type, count: int, *target):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                    "Do `ailie;initialize` or `a;initialize` first before "
                    + "anything!"
                )
            db_ailie.disconnect()
            return

        db_ailie.disconnect()

        # Initialize variables to return for display
        boxes = []
        weightage = []
        pick_up_weightage = []
        reply = ""
        present = False
        target = " ".join(target)

        # Determine what banner is chosen
        if not target:
            if type in ["h", "hero", "heroes"]:
                pool = self.heroes
                weightage = self.heroes_weights
                last_slot_weightage = self.heroes_last_slot_weights
            elif type in ["e", "eq", "equip", "equipment", "equipments"]:
                pool = self.equipments
                weightage = self.equipments_weights
                last_slot_weightage = self.equipments_last_slot_weights
            else:
                await ctx.send(
                        f"Use the command properly please, <@{ctx.author.id}>?")
                return
        else:
            if type in ["h", "hero", "heroes"]:
                pool = self.heroes
                pick_up_weightage = self.heroes_pick_up_weights
                last_slot_weightage = self.heroes_last_slot_weights
            elif type in ["e", "eq", "equip", "equipment", "equipments"]:
                pool = self.equipments
                pick_up_weightage = self.equipments_pick_up_weights
                last_slot_weightage = self.equipments_last_slot_weights
            else:
                await ctx.send(
                        f"Use the command properly please, <@{ctx.author.id}>?")
                return

        if target:
            # Check if pick up is available
            present, invalid, target_banner = self.checkPickUpAvailability(
                target, pick_up_weightage)

            # If the parameter entered is too short
            if invalid:
                await ctx.send(
                        f"Yo, <@{ctx.author.id}>. "
                        + "At least put 4 characters please?")
                return

            # If hero is indeed present in current pick up banner
            if present:
                pick_up_pool, target = self.pickUpPresent(target_banner, pool)

                # Once the pick up is determined, then calculate the summons
                boxes, reply = self.calcResults(
                        ctx, count, pick_up_pool, pick_up_weightage,
                        last_slot_weightage, target)
        else:
            boxes, reply = self.calcResults(
                ctx, count, pool, weightage, last_slot_weightage)

        # If target hero or equipment entered is
        # not present in the current banner
        if not present and target:
            await ctx.send(
                f"Ermmm, <@{ctx.author.id}>. The hero you mentioned "
                + "is not in the current pick up banner."
            )
            return

        self.grantExpOnDupe(ctx.author.id, boxes, type)
        await self.summonDisplay(ctx, count, boxes, reply)


def setup(bot):
    bot.add_cog(Summon(bot))
