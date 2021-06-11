#!/usr/bin/env python

import asyncio
import math
import random
import discord
from discord.ext import commands
from helpers.database import Database


class Growth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sprint_event = []

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
                self, ctx, one_or_ten, t, w, last_slot_weights,
                mass_summon, target=None
            ):
        # Initialize value to return later
        reply = ""
        boxes = []

        if mass_summon:
            one_or_ten = 10

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
    async def summonDisplay(
            self, ctx, one_or_ten, boxes, reply, mass_summon, type):
        msg = await ctx.send(
                f"Wait up, <@{ctx.author.id}>. Summoning {one_or_ten} now..")
        await asyncio.sleep(1)

        # Declare counter
        counter = 1
        units = {}

        if mass_summon:
            one_or_ten = 10

        # Iterate through box and edit messages to update the results
        boxes = iter(boxes)
        for box in boxes:
            if one_or_ten == 10 and not mass_summon:
                # Add five entry per request to lower occurance of rate limits
                await asyncio.sleep(2)
                await msg.edit(
                    content=msg.content
                    + f"\n{counter}. {box}"
                    + f"\n{counter + 1}. {next(boxes)}"
                    + f"\n{counter + 2}. {next(boxes)}"
                    + f"\n{counter + 3}. {next(boxes)}"
                    + f"\n{counter + 4}. {next(boxes)}"
                )
                counter += 5
            elif one_or_ten == 10 and mass_summon:
                if box not in units:
                    units[box] = 1
                else:
                    units[box] += 1
            else:
                await asyncio.sleep(2)
                await msg.edit(content=msg.content + f"\n{counter}. {box}")
                counter += 1

        # Send the reply to fellow guardian
        await asyncio.sleep(2)
        if not mass_summon:
            msg = await msg.reply(reply)
        else:
            emoji_right = "➡️"
            emoji_left = "⬅️"
            emoji_stop = "🛑"
            count = 1
            output = []
            tmp_units = sorted(units, reverse=True)

            for buffer in tmp_units:
                value = units[buffer]
                output.append(f"{count}. **{buffer}** - `{value}`")
                count += 1

            units = output[:]
            buffer_second = []
            buffer_main = []

            total = len(units)
            count = 1
            counter = 0

            for inv in units:
                if len(buffer_second) != 10:
                    buffer_second.append(inv)
                else:
                    buffer_main.append(buffer_second)
                    buffer_second = []
                    buffer_second.append(inv)

                if count == total:
                    buffer_main.append(buffer_second)

                count += 1

            data = "\n".join(buffer_main[counter])

            embed = discord.Embed(
                color=discord.Color.purple(),
                description=data
            )
            embed.set_author(name=ctx.me.name, icon_url=ctx.me.avatar_url)
            embed.set_footer(
                text=(
                    "Press stop sign before you can summon "
                    + "again or wait for timeout."
                    f"\n\n{counter + 1}/{len(buffer_main)}"
                )
            )

            msg = await msg.reply(embed=embed)

            await asyncio.sleep(2)

            await msg.reply(
                f"Mass summon done I guess, <@{ctx.author.id}>?")

            await msg.add_reaction(emoji_left)
            await msg.add_reaction(emoji_right)
            await msg.add_reaction(emoji_stop)

            def check(reaction, user):
                return user == ctx.author \
                    and str(reaction.emoji) in \
                    [emoji_right, emoji_left, emoji_stop]

            while True:
                try:
                    reaction, user = await self.bot.wait_for(
                        'reaction_add', check=check, timeout=10)

                    if reaction.emoji == str(emoji_right):
                        if (len(buffer_main) - 1) != counter:
                            counter += 1

                        data = "\n".join(buffer_main[counter])

                        embed = discord.Embed(
                            color=discord.Color.purple(),
                            description=data
                        )
                        embed.set_author(
                            name=ctx.me.name, icon_url=ctx.me.avatar_url)

                        embed.set_footer(
                            text=(
                                "Press stop sign before you can summon "
                                + "again or wait for timeout."
                                f"\n\n{counter + 1}/{len(buffer_main)}"
                            )
                        )
                        await msg.remove_reaction(str(emoji_right), user)
                        await msg.edit(embed=embed)

                    if reaction.emoji == str(emoji_left):
                        if counter != 0:
                            counter -= 1

                        data = "\n".join(buffer_main[counter])

                        embed = discord.Embed(
                            color=discord.Color.purple(),
                            description=data
                        )
                        embed.set_author(
                            name=ctx.me.name, icon_url=ctx.me.avatar_url)

                        embed.set_footer(
                            text=(
                                "Press stop sign before you can summon "
                                + "again or wait for timeout."
                                f"\n\n{counter + 1}/{len(buffer_main)}"
                            )
                        )
                        await msg.remove_reaction(str(emoji_left), user)
                        await msg.edit(embed=embed)

                    if reaction.emoji == str(emoji_stop):
                        await msg.remove_reaction(str(emoji_stop), user)
                        break
                except discord.Forbidden:
                    await ctx.send(
                        "Please check that I have the permission, "
                        + "`View Channels`, `Send Messages`, `Embed Links` "
                        + "`Add Reactions`, `Read Message History`, "
                        + "and `Manage Messages`."
                        )
                    break
                except Exception:
                    break

    @commands.command(
        name="race",
        brief="Race against Lana.",
        description=(
            "Participate in racing Lana where a random amount "
            + "of gems from roughly 10 to 500 can be obtained."
        ),
        aliases=["rac"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def race(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        # Variables initialized
        gems_to_obtain = []
        counter = 200
        gems = 0

        # Fill gems to obtain list with many random increasing numbers
        while counter < 700:
            gems_to_obtain.append(random.randint(counter + 10, counter + 100))
            counter += 100

        # Choose gems from list with weights
        gems_obtained = random.choices(
            gems_to_obtain, [65, 20, 10, 3.5, 1.5], k=1
        )

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        reply = [
            f"You raced against Lana and obtained `{gems:,d}` gems, "
            + f"<@{ctx.author.id}>!",
            f"You got `{gems:,d}` gems! Lana can't win with that wheelchair "
            + f"on. Right, <@{ctx.author.id}>?",
            f"YES! `{gems:,d}` gems obtained! Good job, <@{ctx.author.id}>!",
            f"Don't you get tired of racing Lana, <@{ctx.author.id}>? Oh well, "
            + f"you've gotten `{gems:,d}` gems though.",
        ]

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.update_user_exp(ctx.author.id, 2)

        await ctx.send(random.choice(reply))

        if ctx.guild.id in self.sprint_event:
            return

        do_sprint_event = random.choices([True, False], [15, 85], k=1)[0]

        if do_sprint_event:
            self.sprint_event.append(ctx.guild.id)
            await ctx.send(
                "Time to race! Call everyone! Its.. sprinting event! "
                + "Whoever typed `sprint` seven times first, wins!"
            )

            sprinters = {}

            def check(message):
                if message.channel == ctx.channel and \
                        message.content.lower() == "sprint":
                    if message.author.id not in sprinters:
                        sprinters[message.author.id] = 1
                    else:
                        sprinters[message.author.id] += 1

                    if sprinters[message.author.id] == 7:
                        return True
                return False

            try:
                await self.bot.wait_for("message", check=check, timeout=45)

                sprint_win_gems = 5000
                user_exp = 100
                for sprinter in sprinters:
                    if sprinters[sprinter] == 7:
                        db_ailie.store_gems(sprinter, sprint_win_gems)
                        db_ailie.update_user_exp(sprinter, user_exp)

                        await ctx.send(
                            f"The winner is <@{sprinter}>! "
                            + f"<@{sprinter}> gained `{sprint_win_gems:,d}` "
                            + f"gems and `{user_exp:,d}` Guardian EXP."
                        )

                        self.sprint_event.remove(ctx.guild.id)
            except Exception as error:
                if isinstance(error, asyncio.TimeoutError):
                    await ctx.send(
                        "Timed out! No one reached the finish line.. "
                        + "*sad noises*"
                    )
                    self.sprint_event.remove(ctx.guild.id)

        db_ailie.disconnect()

    @commands.command(
        name="pat",
        brief="Pats Little Princess's head.",
        description=(
            "Obtain roughly 10 to 1500 gems depending on "
            + "how much Little Princess likes you."
        ),
        aliases=["pa"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def pat(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Variables initialized
        gems_to_obtain = []
        counter = 1000
        gems = 0

        # Fill gems to obtain list with many random increasing numbers
        while counter < 2500:
            gems_to_obtain.append(random.randint(counter + 10, counter + 500))
            counter += 500

        # Choose gems from list with weights
        gems_obtained = random.choices(gems_to_obtain, [50, 30, 20], k=1)

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        reply = [
            f"Little Princess found you `{gems:,d}` gems, <@{ctx.author.id}>!",
            "Little Princess did all the hard work for you and got you, "
            + f"`{gems:,d}` gems. Good one, <@{ctx.author.id}>?",
            f"`{gems:,d}` gems obtained! You get that by being nice to "
            + f"Little Princess, <@{ctx.author.id}>!",
            f"Don't you ever get tired of Little Princess, <@{ctx.author.id}>? "
            + f"Oh well, she gave you `{gems:,d}` gems though.",
        ]

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.update_user_exp(ctx.author.id, 3)
        db_ailie.disconnect()

        await ctx.send(random.choice(reply))

    @commands.command(
        name="gamble",
        brief="Gamble gems.",
        description=(
            "Gamble any amount of gems (of course you can't gamble 0 gems "
            + "or less) to gain the exact amount back in return. That. "
            + "Or you lose the gems gambled."
        ),
        aliases=["ga"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gamble(self, ctx, gems: int):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Disallow negative numbers as input
        if gems <= 0:
            await ctx.send(f"Are you okay, <@{ctx.author.id}>?")
            db_ailie.disconnect()
            return

        max_gamble_amount = 500000
        if gems > max_gamble_amount:
            await ctx.send(
                f"Max gambling amount is `{max_gamble_amount:,d}` gems. "
                + f"Fix your gambling addiction, <@{ctx.author.id}>."
            )
            db_ailie.disconnect()
            return

        # Check if gems is available to gamble
        db_ailie = Database()
        current_gems = db_ailie.get_gems(ctx.author.id)
        balance = current_gems - gems
        if balance < 0:
            await ctx.send(
                "You don't have enough gems to gamble, "
                + f"<@{ctx.author.id}>.."
            )
            db_ailie.disconnect()
            return

        # 50% chance of gambled gems being negative or positive
        win_percentage = 50
        if db_ailie.has_item_amount(ctx.author.id, "Miya's Lucky Card"):
            win_percentage = win_percentage + 10

            dissolves = random.choices([True, False], [90, 10], k=1)
            dissolve = ""

            for dissolve in dissolves:
                dissolve = dissolve

            if dissolve:
                await ctx.send(
                    "You can see `Miya's Lucky Card` "
                    + "flew away as the wind pass by."
                )
                db_ailie.item_break(ctx.author.id, "Miya's Lucky Card")
        gems_obtained = random.choices(
            [-gems, gems], [100 - win_percentage, win_percentage], k=1)

        # Only increase User EXP on 500 or more gamble
        legit_gamble = False
        if gems >= 500:
            legit_gamble = True

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        if gems < 0:
            lost_gems = -gems
            reply = [
                f"<@{ctx.author.id}>, you lost `{lost_gems:,d}` gems. HAHA.",
                f"Condolences to <@{ctx.author.id}> for losing "
                + f"`{lost_gems:,d}` gems.",
                f"Welp. Lost `{lost_gems:,d}` gems. "
                + f"Too bad, <@{ctx.author.id}>.",
            ]
            db_ailie.store_lose_gambled_count(ctx.author.id)
            db_ailie.store_lose_gambled_gems(ctx.author.id, lost_gems)
            db_ailie.store_gambled_gems(ctx.author.id, lost_gems)
            db_ailie.store_spent_gems(ctx.author.id, lost_gems)
        else:
            reply = [
                f"<@{ctx.author.id}>, your luck is omnipotent! Gained "
                + f"`{gems:,d}` gems.",
                f"Congratulations for winning `{gems:,d}` gems, "
                + f"<@{ctx.author.id}>!",
                f"Keep the gems rolling, <@{ctx.author.id}>. `{gems:,d}` gems "
                + "obtained!",
            ]
            db_ailie.store_won_gambled_count(ctx.author.id)
            db_ailie.store_won_gambled_gems(ctx.author.id, gems)
            db_ailie.store_gambled_gems(ctx.author.id, gems)
            db_ailie.store_spent_gems(ctx.author.id, gems)

        db_ailie.store_gems(ctx.author.id, gems)
        db_ailie.store_gamble_count(ctx.author.id)

        if legit_gamble:
            db_ailie.update_user_exp(ctx.author.id, 10)

        db_ailie.disconnect()

        await ctx.send(random.choice(reply))

    @commands.command(
        name="share",
        brief="Share gems.",
        description=(
            "Give a certain amount of gems that you obtain to someone else."
        ),
        aliases=["sha"],
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def share(self, ctx, gems: int, mention: discord.Member):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        # Check if receiver is initialized
        if not db_ailie.is_initialized(mention.id):
            await ctx.send(
                f"Poor thing.. {mention.mention} haven't initialized yet. "
                + f"Tell {mention.mention} to initialize so you can share "
                + "your precious gems!"
            )
            db_ailie.disconnect()
            return

        # Disallow negative numbers as input
        if gems < 0:
            await ctx.send(f"Are you high, <@{ctx.author.id}>?")
            db_ailie.disconnect()
            return

        # Check if gems is available to gamble
        db_ailie = Database()
        current_gems = db_ailie.get_gems(ctx.author.id)
        balance = current_gems - gems
        if balance < 0:
            await ctx.send(
                "To share gems, you need gems yourself first, "
                + f"<@{ctx.author.id}>.."
            )
            db_ailie.disconnect()
            return

        # Check if same sender and receiver
        if mention.id == ctx.author.id:
            await ctx.send(
                "Haha! You really assumed I'd let you share to yourself?")
            db_ailie.disconnect()
            return

        # Transfer gems from sender to receiver
        db_ailie.spend_gems(ctx.author.id, gems)
        db_ailie.store_gems(mention.id, gems)
        db_ailie.update_user_exp(ctx.author.id, 5)
        await ctx.send(
            f"<@{ctx.author.id}> shared `{gems:,d}` gem(s) to {mention.mention}. "
            + "SWEET!"
        )

    @commands.command(
        name="rich",
        brief="Show whales.",
        description=(
            "Rank users based on the server you're in or globally. "
            + "To rank based on the server you're in, put `server` as "
            + "the scope (default). To rank based on global, "
            + "put `global` as the scope."
        ),
        aliases=["ri"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rich(self, ctx, scope="server"):
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
        guardian_with_gems = []
        logical_whereabouts = ""
        output = ""

        if scope.lower() in ["server"]:
            logical_whereabouts = ctx.guild.name
            for member in ctx.guild.members:
                if db_ailie.is_initialized(member.id):
                    gems = db_ailie.get_gems(member.id)
                    level = db_ailie.get_user_level(member.id)
                    if gems != 0:
                        buffer = [gems, member.id, str(member), level]
                        guardian_with_gems.append(buffer)
        elif scope.lower() in ["global", "all"]:
            await ctx.send(
                "Global rank will take a while to produce.. "
                + f"Please wait, <@{ctx.author.id}>."
            )
            logical_whereabouts = "Global"
            for guild in self.bot.guilds:
                for member in guild.members:
                    if db_ailie.is_initialized(member.id):
                        gems = db_ailie.get_gems(member.id)
                        level = db_ailie.get_user_level(member.id)
                        if gems != 0:
                            buffer = [gems, member.id, str(member), level]
                            if buffer not in guardian_with_gems:
                                guardian_with_gems.append(buffer)
        else:
            await ctx.send(
                f"Dear, <@{ctx.author.id}>. You can only specify `server` "
                + "or `global`."
            )

        # If no one has gems
        if not guardian_with_gems:
            await ctx.send("No one has gems.")
            db_ailie.disconnect()
            return

        # Display richest user in discord server
        guardian_with_gems_sorted = sorted(guardian_with_gems, reverse=True)
        guardian_with_gems = guardian_with_gems_sorted[:10]
        counter = 1
        for whales in guardian_with_gems:
            if counter == 1:
                output = output + \
                    f"{counter}. {whales[0]:,d} 💎 - " \
                    + f"Lvl {whales[3]} `{whales[2]}`"
            else:
                output = output \
                        + f"\n{counter}. {whales[0]:,d} 💎 - " \
                        + f"Lvl {whales[3]} `{whales[2]}`"

            # Get username if any
            username = db_ailie.get_username(whales[1])
            if username is not None:
                output = output + f" a.k.a. `{username}`"

            counter += 1

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name=ctx.me.name, icon_url=ctx.me.avatar_url)
        embed.add_field(name=f"Whales in {logical_whereabouts}!", value=output)

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="gems",
        brief="Check gems.",
        description="Check the amount of your current gems statistics.",
        aliases=["ge"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gems(self, ctx, mention: discord.Member = None):
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

        # Display gems balance
        gems = db_ailie.get_gems(guardian_id)
        gems_gambled = db_ailie.get_gambled_gems(guardian_id)
        gems_spent = db_ailie.get_spent_gems(guardian_id)
        win_gamble_gems = db_ailie.get_won_gambled_gems(guardian_id)
        lose_gamble_gems = db_ailie.get_lose_gambled_gems(guardian_id)
        db_ailie.disconnect()
        embed = discord.Embed(
            description=(
                f"**Current Gems**: `{gems:,d}`"
                + f"\n**Gems Spent**: `{gems_spent:,d}`"
                + f"\n**Gems Gambled**: `{gems_gambled:,d}`"
                + f"\n**Gems Gambled Won**: `{win_gamble_gems:,d}`"
                + f"\n**Gems Gambled Lost**: `{lose_gamble_gems:,d}`"
            ),
            color=discord.Color.purple()
        )
        embed.set_author(
            name=f"{guardian_name}'s Gems", icon_url=guardian_avatar)
        await ctx.send(embed=embed)

    @commands.command(
        name="hourly",
        brief="Hourly gems.",
        description="Claim hourly gems.",
        aliases=["ho"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hourly(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        qualified_hourly = db_ailie.get_hourly_qualification(ctx.author.id)

        if qualified_hourly:
            gems = 1000
            db_ailie.store_gems(ctx.author.id, gems)
            db_ailie.update_user_exp(ctx.author.id, 5)
            await ctx.send(
                f"Hourly gems claimed. You obtained `{gems:,d}` gems, "
                + f"<@{ctx.author.id}>!"
            )
        else:
            cd = db_ailie.get_hourly_cooldown(ctx.author.id)
            await ctx.send(
                f"One can be so greedy, <@{ctx.author.id}>. "
                + f"`{cd}` left before reset."
            )

    @commands.command(
        name="daily",
        brief="Daily gems.",
        description="Claim daily gems.",
        aliases=["da"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def daily(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        qualified_daily = db_ailie.get_daily_qualification(ctx.author.id)

        if qualified_daily:
            count = db_ailie.get_daily_count(ctx.author.id)
            gems = 2500 + (200 * count)
            db_ailie.store_gems(ctx.author.id, gems)
            db_ailie.update_user_exp(ctx.author.id, 5)
            await ctx.send(
                f"Daily gems claimed for `{count:,d}` time(s) already. "
                + f"You obtained `{gems:,d}` gems, <@{ctx.author.id}>!"
            )
        else:
            cd = db_ailie.get_daily_cooldown(ctx.author.id)
            await ctx.send(
                f"One can be so greedy, <@{ctx.author.id}>. "
                + f"`{cd}` left before reset."
            )

    @commands.command(
        name="shop",
        brief="Look through shop.",
        description="View items sold in shop.",
        aliases=["sho"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx, *item):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        blacklist = ["Miya's Lucky Card"]

        if item:
            item = " ".join(item)

            if len(item) < 4:
                await ctx.send(
                    f"Yo, <@{ctx.author.id}>. "
                    + "At least put 4 characters please?"
                )
                db_ailie.disconnect()
                return

            item_details = db_ailie.get_shop_item_detailed(item)

            if item_details is None:
                await ctx.send(
                    f"Are you sure that item exist, <@{ctx.author.id}>?")
                db_ailie.disconnect()
                return

            if item_details[0] in blacklist:
                await ctx.send("The item you mentioned is not available now.")
                db_ailie.disconnect()
                return

            embed = discord.Embed(
                description=(
                    f"**Name**: `{item_details[0]}`"
                    + f"\n**Price**: `{item_details[1]:,d}` 💎"
                    + f"\n\n**Description**:\n`{item_details[2]}`"
                ),
                color=discord.Color.purple()
            )
            embed.set_author(
                name=f"{ctx.me.name}'s Shop",
                icon_url=ctx.me.avatar_url
            )
            await ctx.send(embed=embed)
        else:
            shop_items = db_ailie.get_shop_items()

            counter = 1
            buffer_total = []
            for shop_item in shop_items:
                if not shop_item[0] in blacklist:
                    buffer = \
                        f"{counter}. **{shop_item[0]}** - `{shop_item[1]:,d}` 💎"
                    buffer_total.append(buffer)
                    counter += 1

            embed = discord.Embed(
                description=("\n".join(buffer_total)),
                color=discord.Color.purple()
            )
            embed.set_author(
                name=f"{ctx.me.name}'s Shop",
                icon_url=ctx.me.avatar_url
            )
            await ctx.send(embed=embed)

        db_ailie.disconnect()

    @commands.command(
        name="buy",
        brief="Buy items in shop.",
        description="Buy items from shop to use in your adventure.",
        aliases=["bu"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def buy(self, ctx, amount: int, *item):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        blacklist = ["Miya's Lucky Card"]

        if amount <= 0:
            await ctx.send(
                "Are you testing me?"
            )
            db_ailie.disconnect()
            return

        if not item:
            await ctx.send(
                "Forgot to specify the item, I assume? "
                + "Do something correctly for once. *sigh*"
            )
            db_ailie.disconnect()
            return

        item = " ".join(item)
        item_details = db_ailie.get_shop_item_detailed(item)

        if item_details is None:
            await ctx.send(
                f"Item does not exists. You okay, <@{ctx.author.id}>?")
            return

        if item_details[0] in blacklist:
            await ctx.send("The item you mentioned is not available now.")
            db_ailie.disconnect()
            return

        if not item_details:
            await ctx.send(
                f"Are you sure that item exist, <@{ctx.author.id}>? "
                + "Please, please, please, do better!"
            )
            db_ailie.disconnect()
            return

        item_name = item_details[0]
        item_price = item_details[1]
        gems_required = item_price * amount

        current_gems = db_ailie.get_gems(ctx.author.id)

        if gems_required > current_gems:
            await ctx.send(
                f"Go collect more gems, you need `{gems_required:,d}` gems."
            )
            db_ailie.disconnect()
            return

        db_ailie.spend_gems(ctx.author.id, gems_required)
        db_ailie.buy_items(ctx.author.id, item_name, amount)

        await ctx.send(f"<@{ctx.author.id}>, you bought {amount} {item_name}!")
        db_ailie.disconnect()

    @commands.command(
        name="wish",
        brief="Wishes for gems.",
        description=(
            "You wished so hard using `Princess Amulet` that you get gems."
        ),
        aliases=["wi"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def wish(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` "
                + "first before anything!"
            )
            db_ailie.disconnect()
            return

        amount_amulet = \
            db_ailie.has_item_amount(ctx.author.id, "Princess Amulet")

        if not amount_amulet:
            await ctx.send(
                f"Sorry, <@{ctx.author.id}>. You need `Princess Amulet` "
                + "to `wish`. Buy one from `a;shop`. "
                + "If you have gems that is. HAHA!"
            )
            db_ailie.disconnect()
            return

        # Variables initialized
        gems_to_obtain = []
        weight = [70, 15, 10, 2.5, 1.75, 0.50, 0.25]
        counter = 1
        min_gems_to_gain = 1000
        gems = 0

        # Fill gems to obtain list with many random increasing numbers
        while counter < 8:
            gems_to_obtain.append(
                random.randint(min_gems_to_gain, min_gems_to_gain + 500))
            min_gems_to_gain = min_gems_to_gain * 2
            counter += 1

        # Choose gems from list with weights
        gems_obtained = random.choices(gems_to_obtain, weight, k=1)

        # Assign gem amount from array to single variable
        for gems in gems_obtained:
            gems = gems

        # Store and display gems obtained
        reply = [
            "You wished to get the maximum amount of gems "
            + "this command can you. "
            + f"You get.. nothing, <@{ctx.author.id}>.",
            "Oops! `Princess Amulet` broke. "
            + f"No gems for you, <@{ctx.author.id}>.",
            f"You wished hard and got `{gems:,d}` gems, <@{ctx.author.id}>.",
            "You wish and wished and wished Little Princess "
            + f"never had to suffer and got `{gems:,d}` gems while "
            + f"doing so, <@{ctx.author.id}>.",
            f"While wishing you saw `{gems:,d}` gems infront of you, "
            f"<@{ctx.author.id}>. Miracle?",
            "You wished to be the richest Guardian and got "
            + f"yourself `{gems:,d}` gems, <@{ctx.author.id}>."
        ]

        buffer = [reply[0], reply[1]]
        broke = False
        chosen_reply = random.choice(reply)

        if chosen_reply in buffer:
            msg = await ctx.send(chosen_reply)
            await asyncio.sleep(3)

            # Calculate chance to break
            broke = random.choices([True, False], [20, 80], k=1)

            # Assign list to variable
            for b in broke:
                broke = b

            if broke:
                db_ailie.item_break(ctx.author.id, "Princess Amulet")
                await msg.reply(
                    "Yeah, I'm serious. Your `Princess Amulet` broke, "
                    + f"<@{ctx.author.id}>. Sad."
                )
            else:
                await msg.reply(
                    f"Just kidding. You've gotten `{gems:,d}` gems, "
                    + f"<@{ctx.author.id}>. Scared?"
                )
        else:
            await ctx.send(chosen_reply)
            broke = False

        if not broke:
            db_ailie.store_gems(ctx.author.id, gems)
            db_ailie.update_user_exp(ctx.author.id, 10)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        max_lb = 9
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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

        level = math.trunc((current_exp + exp_to_increase) / 100)
        max_level = int((5000 + (5000 * lb)) / 100)

        if level > max_level:
            await ctx.send(
                f"You can't increase that much, <@{ctx.author.id}>. "
                + f"Your max level for that equipment is `{max_level:,d}`."
            )
            db_ailie.disconnect()
            return

        gems_required = level_increase * 2700
        current_gems = db_ailie.get_gems(ctx.author.id)

        if gems_required > current_gems:
            await ctx.send(
                f"Oof, poor guys <@{ctx.author.id}>.. "
                + f"You need `{gems_required:,d}` gems "
                + f"and you only have `{current_gems:,d}` gems. Sad life."
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
                db_ailie.update_equip_exp(
                    ctx.author.id, equip_full_name, exp_to_increase)

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
        name="train",
        brief="Train heroes.",
        description="Train heroes to gain EXP.",
        aliases=["tra"],
    )
    @commands.guild_only()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def train(self, ctx, key="main"):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if key == "main":
            if not db_ailie.is_team_exists(ctx.author.id, "main"):
                await ctx.send(
                    "You need to set a team with `a;team`."
                )
                db_ailie.disconnect()
                return

        if not db_ailie.is_team_exists(ctx.author.id, key):
            await ctx.send(
                f"You dont have a team with that key, <@{ctx.author.id}>! "
                + "Check `team` command."
            )
            db_ailie.disconnect()
            return

        hero_id = db_ailie.get_first_hero_from_team(ctx.author.id, key)
        hero_full_name = db_ailie.get_hero_name_from_id(hero_id)

        highest_exp_gain = 60
        lowest_exp_gain = 40

        hero_current_exp = db_ailie.get_hero_exp(ctx.author.id, hero_full_name)
        hero_lb = db_ailie.get_hero_limit_break(ctx.author.id, hero_full_name)
        max_exp = 5000 + (5000 * hero_lb)
        max_exp_can_gain = max_exp - hero_current_exp

        if max_exp_can_gain == 0:
            await ctx.send(
                f"Stop being greedy, <@{ctx.author.id}>! "
                + "You're already at max level. *sigh*"
            )
            db_ailie.disconnect()
            return

        if max_exp_can_gain < 40:
            highest_exp_gain = lowest_exp_gain = max_exp_can_gain
        elif max_exp_can_gain < 60:
            highest_exp_gain = max_exp_can_gain

        training_typing = [
            "Must protect Little Princess!",
            "I hope Future Princess gets nerfed..",
            "I love it when my Weapon Skill misses.",
            "Push up, push down, push up, push down.",
            "I just want to get this over with.",
            "What should I ask you guys to type?",
            "Does it feel better when you don't need to type "
            + "the hero's name?"
        ]

        # Randomly pick from list
        training_typing_picked = random.choice(training_typing)

        await ctx.send(
            f"Type `{training_typing_picked}` to train your hero. "
            + "Easy enough?"
        )

        # Function to confirm training
        def confirm_training(message):
            return message.author.id == ctx.author.id

        # Wait for training decision
        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_training, timeout=30
            )

            exp = random.randint(lowest_exp_gain, highest_exp_gain)

            if msg.content == training_typing_picked:
                reply = [
                    f"<@{ctx.author.id}>, you can feel `{exp:,d}` Hero EXP "
                    + "coursing through your hero.",
                    "You think you've got the best your hero? "
                    + "However strong your your hero "
                    + f"is, <@{ctx.author.id}>, it still won't surpass me. "
                    + f"You've got `{exp:,d}` Hero EXP though.",
                    f"<@{ctx.author.id}>, you can feel your hero "
                    + f"getting stronger right this moment. Gained `{exp:,d}` "
                    + "Hero EXP!",
                ]
                reply = random.choice(reply)

                db_ailie.update_hero_exp(ctx.author.id, hero_full_name, exp)

                await ctx.send(reply)
            else:
                await ctx.send(
                    f"Oops! You typed wrong, <@{ctx.author.id}>. "
                    + "Make sure everything is the same. "
                    + "Also, its Caps Lock Sensitive."
                )
        except Exception:
            await ctx.send(
                "You're taking too long to type, "
                + f"<@{ctx.author.id}>. Ain't waiting for you!"
            )

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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
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
        mass_summon = False
        summon_loop = 0
        target = " ".join(target)

        if not count <= 0 and count > 10:
            if count > 100:
                await ctx.send(
                    "More than 100 summons? You trying to "
                    + "make me crash or something?"
                )
                return

            if count % 10 == 0:
                db_ailie = Database()
                if not db_ailie.has_item_amount(
                        ctx.author.id, "Oghma's Booster"):
                    await ctx.send("You need `Oghma's Booster` to mass summon.")
                    db_ailie.disconnect()
                    return

                mass_summon = True
                summon_loop = int(count / 10)
                db_ailie.item_break(ctx.author.id, "Oghma's Booster")
                db_ailie.disconnect()
            else:
                await ctx.send(
                    "Mass summon can only be done with "
                    + "numbers that are multiplications of 10."
                )
                return

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
                if not mass_summon:
                    boxes, reply = self.calcResults(
                            ctx, count, pick_up_pool, pick_up_weightage,
                            last_slot_weightage, mass_summon, target)
                else:
                    counter = 0
                    boxes_buffer = []
                    while counter < summon_loop:
                        boxes_buffer, reply = self.calcResults(
                                ctx, count, pick_up_pool, pick_up_weightage,
                                last_slot_weightage, mass_summon, target)
                        counter += 1

                        for b in boxes_buffer:
                            boxes.append(b)
        else:
            if not mass_summon:
                boxes, reply = self.calcResults(
                    ctx, count, pool, weightage,
                    last_slot_weightage, mass_summon
                )
            else:
                counter = 0
                boxes_buffer = []
                while counter < summon_loop:
                    boxes_buffer, reply = self.calcResults(
                        ctx, count, pool, weightage,
                        last_slot_weightage, mass_summon
                    )
                    counter += 1

                    for b in boxes_buffer:
                        boxes.append(b)

        # If target hero or equipment entered is
        # not present in the current banner
        if not present and target:
            await ctx.send(
                f"Ermmm, <@{ctx.author.id}>. The hero you mentioned "
                + "is not in the current pick up banner."
            )
            return

        self.grantExpOnDupe(ctx.author.id, boxes, type)
        await self.summonDisplay(ctx, count, boxes, reply, mass_summon, type)

    @commands.command(
        name="rank",
        brief="Show PvP ranks.",
        description=(
            "Rank users based on the server you're in or globally. "
            + "To rank based on the server you're in, put `server` as "
            + "the scope (default). To rank based on global, "
            + "put `global` as the scope."
        ),
        aliases=["ran"]
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
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
                        buffer = [trophy, member.id, str(member), level]
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
                            buffer = [trophy, member.id, str(member), level]
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
                    + f"Lvl {barbarian[3]} `{barbarian[2]}`"
            else:
                output = output + \
                        f"\n{counter}. {barbarian[0]:,d} 🏆 - " \
                        + f"Lvl {barbarian[3]} `{barbarian[2]}`"

            # Get username if any
            username = db_ailie.get_username(barbarian[1])
            if username is not None:
                output = output + f" a.k.a. `{username}`"

            counter += 1

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name="Ailie", icon_url=ctx.me.avatar_url)
        embed.add_field(
            name=f"Barbarians in {logical_whereabouts}!", value=output)
        embed.set_footer(
            text=(
                "Arena resets weekly on Monday, 00:00 UTC."
                + "\nYou can claim weekly arena rewards with claim command."
            )
        )

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="trophy",
        brief="Check trophies.",
        description="Check the amount of your current trophies.",
        aliases=["tro"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        rank = db_ailie.get_current_guardian_ranking(guardian_id)

        if not rank:
            rank = "`No Rank` - *Participate in arena once to get rank.*"

        db_ailie.disconnect()
        embed = discord.Embed(
            description=(
                f"**Trophies**: `{trophies:,d}`"
                + f"\n**Rank**: {rank}"
                + f"\n**Wins**: `{wins:,d}`"
                + f"\n**Losses**: `{losses:,d}`"
            ),
            color=discord.Color.purple()
        )
        embed.set_author(
            name=f"{guardian_name}'s Trophies", icon_url=guardian_avatar)
        embed.set_footer(
            text=(
                "Arena resets weekly on Monday, 00:00 UTC."
                + "\nYou can claim weekly arena rewards with claim command."
            )
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="roll",
        brief="Roll equipments' multipliers.",
        description=(
            "Roll equipments' multipliers with a certain amount of gems."
        ),
        aliases=["ro"]
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roll(self, ctx, *equipment):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if not equipment:
            await ctx.send(
                "You need to specify an equipment to roll multipliers.")
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

        if not db_ailie.has_item_amount(ctx.author.id, "Option Change Stone"):
            await ctx.send(
                "You need `Option Change Stone` to roll new "
                + "multiplier for your weapon."
            )
            db_ailie.disconnect()
            return

        # Variables initialized
        rolls_to_obtain = []
        weight = [5, 10, 20, 30, 20, 7.5, 3, 2, 1.75, 0.75]
        counter = 0
        min_rolls_to_gain = 0
        rolls = 0
        inventory_id = db_ailie.get_inventory_id(ctx.author.id)
        old_roll = \
            db_ailie.get_multiplier_equip(equip_id, inventory_id)

        # Fill gems to obtain list with many random increasing numbers
        while counter < 10:
            rolls_to_obtain.append(
                random.randint(min_rolls_to_gain, min_rolls_to_gain + 10))
            min_rolls_to_gain += 10
            counter += 1

        # Choose rolls from list with weights
        rolls_obtained = random.choices(rolls_to_obtain, weight, k=1)

        # Assign gem amount from array to single variable
        for rolls in rolls_obtained:
            rolls = rolls

        await ctx.send(
            f"<@{ctx.author.id}>, your old roll is `{old_roll}`% " +
            f"and your new roll is `{rolls}`%. Would you like to confirm "
            + "the new roll or not? `Y` or `N`."
        )

        # Break after use
        db_ailie.item_break(ctx.author.id, "Option Change Stone")

        # Function to confirm roll
        def confirm_roll(message):
            return (
                message.author.id == ctx.author.id
                and message.content.upper() in ["YES", "Y", "NO", "N"]
            )

        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_roll, timeout=30
            )

            if msg.content.upper() in ["YES", "Y"]:
                db_ailie.update_multiplier_equip(inventory_id, equip_id, rolls)
                await ctx.send(
                    f"Updated your equipment multiplier to `{rolls}`%, "
                    + f"<@{ctx.author.id}>!"
                )
            else:
                await ctx.send(
                    f"Alright, <@{ctx.author.id}>. "
                    + "Keeping your old multiplier roll."
                )
        except Exception:
            await ctx.send(
                f"I guess you somehow forgot to reply, <@{ctx.author.id}>."
            )

    @commands.command(
        name="exchange",
        brief="Exchange stats from one to another.",
        description=(
            "Exchange the stats from one hero or equipment "
            + "to another hero or equipment. `type` should "
            + "either be `hero` or `equip`. `targets` should "
            + "be the hero or equipment to swap in "
            + "`target>target` format."
        ),
        aliases=["ex"]
    )
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def exchange(self, ctx, type, *targets):
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

        if not targets:
            await ctx.send(
                "Please specify hero or equipment to swap."
            )
            return

        targets = " ".join(targets)
        targets = targets.split(">")
        counter_buffer = []

        # Remove whitespaces
        for target in targets:
            if target == "":
                counter_buffer.append(targets.index(target))

        for counter in counter_buffer:
            targets.pop(counter)

        if len(targets) != 2:
            await ctx.send(
                "Can only exchange stats when two targets are stated. "
                "`Alef>Vishuvac` or `Liberator>Amarok` for such."
            )
            db_ailie.disconnect()
            return

        buffer = []
        for target in targets:
            if type.lower() in ["h", "hero", "heroes"]:
                full_name = db_ailie.get_hero_full_name(target)
                if not db_ailie.has_item_amount(
                        ctx.author.id, "Hero Exchange Scroll"):
                    await ctx.send(
                        "You need `Hero Exchange Scroll` to swap heroes' "
                        + "stats."
                    )
                    db_ailie.disconnect()
                    return
            else:
                full_name = db_ailie.get_equip_full_name(target)
                if not db_ailie.has_item_amount(
                        ctx.author.id, "Equipment Exchange Scroll"):
                    await ctx.send(
                        "You need `Equipment Exchange Scroll` to swap "
                        + "equipments' stats."
                    )
                    db_ailie.disconnect()
                    return

            if not full_name:
                await ctx.send("The target you stated doesn't exist.")
                db_ailie.disconnect()
                return
            else:
                if type.lower() in ["h", "hero", "heroes"]:
                    target_id = db_ailie.get_hero_id(full_name)
                    obtained = \
                        db_ailie.is_hero_obtained(ctx.author.id, target_id)
                else:
                    target_id = db_ailie.get_equip_id(full_name)
                    obtained = \
                        db_ailie.is_equip_obtained(ctx.author.id, target_id)

                if not obtained:
                    await ctx.send(f"You don't own **{full_name}**.")
                    db_ailie.disconnect()
                    return
                buffer.append(full_name)

        # Check duplicate targets
        if len(set(buffer)) != len(buffer):
            await ctx.send(
                "You're trying to exchange stats of the "
                + "same target? Aren't you a bit crazy?"
            )
            db_ailie.disconnect()
            return

        # Get confirmation
        await ctx.send(
                f"<@{ctx.author.id}>, confirm to exchange stats from "
                + f"**{buffer[0]}** to **{buffer[1]}**. `Y` or `N`?"
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
                if type.lower() in ["h", "hero", "heroes"]:
                    db_ailie.exchange_stats_hero(
                        inventory_id, buffer[0], buffer[1])
                    db_ailie.item_break(
                        ctx.author.id, "Hero Exchange Scroll")
                else:
                    db_ailie.exchange_stats_equip(
                        inventory_id, buffer[0], buffer[1]
                    )
                    db_ailie.item_break(
                        ctx.author.id, "Equipment Exchange Scroll")

                await ctx.send(
                        f"Hey, <@{ctx.author.id}>. "
                        + f"Your **{buffer[0]}**'s stats has been carried "
                        + f"over to **{buffer[1]}**."
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
        name="claim",
        brief="Claim rewards from arena.",
        description=(
            "Claim the accumulated rewards from arena."
        ),
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def claim(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        claim_gems = db_ailie.get_claim_gems(ctx.author.id)
        db_ailie.store_gems(ctx.author.id, claim_gems)

        if claim_gems == 0:
            await ctx.send(
                f"You have nothing to claim, <@{ctx.author.id}>."
            )
        else:
            await ctx.send(
                f"You claimed `{claim_gems:,d}` gems, <@{ctx.author.id}>."
            )

        db_ailie.disconnect()


def setup(bot):
    bot.add_cog(Growth(bot))
