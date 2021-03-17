#!/usr/bin/env python

import asyncio
import random
import csv
from discord.ext import commands


class Summon(commands.Cog):
    def __init__(self, bot):
        # Bot assigned to class
        self.bot = bot

        # Get all the data for heroes and pick up heroes
        self.heroes = self.getRecords("csv/heroes.csv", [[], [], []])
        self.pick_up_heroes = self.getRecords("csv/pick-up-heroes.csv", [])

        # Weights declaration for probability upon hero summons
        self.heroes_weights = [78.250, 19.000, 2.750]
        self.heroes_pick_up_weights = [78.250, 19.000, 1.375, 1.375]
        self.heroes_last_slot_weights = [97.25, 2.75]

        # Get all the data for heroes and pick up heroes
        self.equipments = self.getRecords(
            "csv/equipments.csv", [[], [], [], [], []])
        self.pick_up_equipments = self.getRecords(
            "csv/pick-up-equipments.csv", [])

        # Weights declaration for probability upon hero summons
        self.equipments_weights = [58.000, 27.000, 9.000, 3.000, 3.000]
        self.equipments_pick_up_weights = [
            58.000, 27.000, 9.000, 3.000, 1.000, 2.000
        ]
        self.equipments_last_slot_weights = [94, 3, 3]

    # Get the records of all Guardian Tales heroes from csv files
    def getRecords(self, csv_file, records):
        buffer = records[:]

        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                for r in row:
                    # Check if the list has a list inside declared
                    if len(records) != 0:
                        if r:
                            buffer[row.index(r)].append(r)
                    else:
                        buffer.append(r)

        return buffer

    # Summons are determined to check for certain requirements
    def checkWhatIsSummoned(self, r, target, heroes_check, white_box, obtainedPickup, ailie=None):
        if heroes_check:
            if "★★★" in r:
                white_box = True
            if r == target:
                obtainedPickup = True
            if "Ailie" in r:
                ailie = True
        else:
            if "★★★★★ [Ex]" in r:
                white_box = True
            if r == target:
                obtainedPickup = True

        return white_box, obtainedPickup, ailie

    # Replies are sent back according to the summons obtained
    def getRepliesForSpecificSummons(self, ctx, target, heroes_check, white_box, obtainedPickup, ailie):
        # Initialize reply variable
        reply = ""

        # Get funky replies
        if heroes_check:
            if white_box and not obtainedPickup and target:
                reply = f"I see 3 star hero. But no {target}.. Sad life, <@{ctx.author.id}>."
            if white_box and obtainedPickup and target:
                reply = f"WOHOOOOOOOOOOOOOOOOOO, <@{ctx.author.id}>! You got the pick up hero!"
            if white_box and not target:
                reply = f"WOW! W-w-waaaiittt a second, <@{ctx.author.id}>..  Is that a freaking 3 star hero?!"

            if not white_box and ailie:
                reply = f"Think positive, <@{ctx.author.id}>! At least you got me :D"
            elif not white_box and not ailie:
                reply = f"You just suck at gachas, <@{ctx.author.id}>.."
        else:
            if white_box and not obtainedPickup and target:
                reply = f"I see 5 star exclusive weapon. But no {target}.. Sad life, <@{ctx.author.id}>."
            if white_box and obtainedPickup and target:
                reply = f"WOHOOOOOOOOOOOOOOOOOO, <@{ctx.author.id}>! You got the pick up equipment!"
            if white_box and not target:
                reply = f"WOW! W-w-waaaiittt a second, <@{ctx.author.id}>..  Is that a freaking exclusive weapon?!"

            if not white_box:
                reply = f"You just suck at gachas, <@{ctx.author.id}>.."

        return reply

    # Check if pick up chosen is available at the current time
    def checkPickUpAvailability(self, ctx, target, w):
        # Initialize variable to check invalid input
        invalid = False
        present = False
        target_banner = ""
        heroes_check = False

        # Check if the parameter send is lesser than 5 characters
        # If its lesser, then return error message
        if len(target) < 5:
            return f"Yo, <@{ctx.author.id}>. At least put 4 characters please?"

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
    def pickUpPresent(self, ctx, one_or_ten, target_banner, pool, weights, last_slot_weights):
        # Initialize counters
        pick_up_pool = pool[:]
        boxes = []
        reply = ""
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

                        boxes, reply = self.calcResults(
                            ctx,
                            one_or_ten,
                            pick_up_pool,
                            weights,
                            last_slot_weights,
                            pick_up_pool[index + 1][0],
                        )

                        break
                break

        return boxes, reply

    # Calculate the chances in summons
    def calcResults(self, ctx, one_or_ten, t, w, last_slot_weights, target=None):
        # Initialize value to return later
        reply = ""
        boxes = []

        # Check for summon values be it 10, 1 or invalid
        if one_or_ten == "10" or one_or_ten == "ten":
            results = random.choices(t, w, k=9)
        elif one_or_ten == "1" or one_or_ten == "one":
            results = random.choices(t, w, k=1)
        else:
            results = [
                f"Hey, <@{ctx.author.id}>. I don't think thats a valid summon value. LOL!",
                f"Ermm.. its either 10 or 1! Get yourself corrected, <@{ctx.author.id}>!",
                f"You sure there's a {one_or_ten} summon, <@{ctx.author.id}>? There's only 1 and 10 summon!"
            ]

            reply = random.choice(results)

        # If the value is valid, then the statements here is executed
        if one_or_ten == "10" or one_or_ten == "ten" or one_or_ten == "1" or one_or_ten == "one":
            # Variables used as a counter to check what is being summoned
            heroes_check = False
            white_box = False
            obtainedPickup = False
            pity = False
            ailie = False
            pity_check = False

            if w == self.heroes_weights or w == self.heroes_pick_up_weights:
                heroes_check = True

            # Iterate through results
            for result in results:
                result = random.choices(result, k=1)
                for r in result:
                    if one_or_ten == "10" or one_or_ten == "ten":
                        # To determine if pity is deserved for last slot summon
                        if heroes_check:
                            if not "★★★ " in r and not pity_check:
                                pity = True
                            if not "★★ " in r and not pity_check:
                                pity = True
                            else:
                                pity = False
                                pity_check = True
                        else:
                            if not "★★★★★ " in r and not pity_check:
                                pity = True
                            if not "★★★★ " in r and not pity_check:
                                pity = True
                            else:
                                pity = False
                                pity_check = True

                    # Check what is being summoned for specific replies
                    if heroes_check:
                        white_box, obtainedPickup, ailie = self.checkWhatIsSummoned(
                            r, target, heroes_check, white_box, obtainedPickup, ailie)
                    else:
                        white_box, obtainedPickup, ailie = self.checkWhatIsSummoned(
                            r, target, heroes_check, white_box, obtainedPickup)

                    # Append the summons to boxes to be returned
                    boxes.append(r)

            # If the summon is with a value 10 and the summons from 1 until 9 is bad
            # (No 2 star and above for heroes and no 4 star and above for equipments),
            # then, the user deserves higher rates
            if pity:
                target_pity = t[:]
                target_pity.pop(0)
                results = random.choices(
                    target_pity, last_slot_weights, k=1)
                for pity_result in results:
                    p_r = random.choices(pity_result, k=1)
                    for pr in p_r:
                        # Check what is being summoned for specific replies
                        if heroes_check:
                            white_box, obtainedPickup, ailie = self.checkWhatIsSummoned(
                                pr, target, heroes_check, white_box, obtainedPickup, ailie)
                        else:
                            white_box, obtainedPickup, ailie = self.checkWhatIsSummoned(
                                pr, target, heroes_check, white_box, obtainedPickup)

                        # Append the summons to boxes to be returned
                        boxes.append(pr)

            # If the user doesn't deserve pity, then continue with normal rates
            if not pity:
                results = random.choices(t, w, k=1)
                for not_pity_result in results:
                    n_p_r = random.choices(not_pity_result, k=1)
                    for npr in n_p_r:
                        # Check what is being summoned for specific replies
                        if heroes_check:
                            white_box, obtainedPickup, ailie = self.checkWhatIsSummoned(
                                npr, target, heroes_check, white_box, obtainedPickup, ailie)
                        else:
                            white_box, obtainedPickup, ailie = self.checkWhatIsSummoned(
                                npr, target, heroes_check, white_box, obtainedPickup)

                        # Append the summons to boxes to be returned
                        boxes.append(npr)

            # Get specific replies corresponding to the summons
            if heroes_check:
                reply = self.getRepliesForSpecificSummons(
                    ctx, target, heroes_check, white_box, obtainedPickup, ailie)
            else:
                reply = self.getRepliesForSpecificSummons(
                    ctx, target, heroes_check, white_box, obtainedPickup, ailie)

        return boxes, reply

    # Summon is displayed accordingly
    async def summonDisplay(self, ctx, one_or_ten, boxes, reply):
        msg = await ctx.send(f"Wait up, <@{ctx.author.id}>. Summoning {one_or_ten} now..")
        await asyncio.sleep(3)

        # Declare counter
        counter = 1
        # Iterate through box and edit messages to update the results
        boxes = iter(boxes)
        for box in boxes:
            # Add two entry per request to lower occurance of rate limits
            await msg.edit(content=msg.content + f"\n{counter}. {box}\n{counter + 1}. {next(boxes)}")
            await asyncio.sleep(1.5)
            counter += 2

        await ctx.send(reply)

    # Lists the current pickup banner
    @commands.command(
        name="pickup.info",
        help="Lists the current pickup banner.",
        aliases=["pickupinfo", "p.i", "pi"]
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def pickUpInfo(self, ctx):
        message = "\n\n**Pick Up Heroes**"
        i = 1

        # Store heroes pick up banner
        for pick_up_info in self.pick_up_heroes:
            message = message + f"\n{i}. {pick_up_info}"
            i += 1

        message = message + "\n\n**Pick Up Equipments**"
        i = 1
        # Store equipments pick up banner
        for pick_up_info in self.pick_up_equipments:
            message = message + f"\n{i}. {pick_up_info}"
            i += 1

        # Send the string in one take so rate limit doesn't occur
        await ctx.send(f"Hello, <@{ctx.author.id}>. These are the Pick Up Banner ongoing. {message}")

    # Summon heroes on the normal banner
    @commands.command(
        name="summon.hero",
        help="Summons single or ten heroes on the normal banner.",
        aliases=["summonhero", "s.h", "sh"]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def summonHero(self, ctx, one_or_ten):
        boxes, reply = self.calcResults(
            ctx, one_or_ten, self.heroes, self.heroes_weights, self.heroes_last_slot_weights)
        await self.summonDisplay(ctx, one_or_ten, boxes, reply)

    # Summon heroes on the pick up banner
    @commands.command(
        name="summon.hero.pickup",
        help="Summons single or ten heroes on the pick up banner.",
        aliases=["summonheropickup", "s.h.p", "shp"]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def summonHeroPickUp(self, ctx, hero, one_or_ten):
        # Check if pick up is available
        present, invalid, hero_banner = self.checkPickUpAvailability(
            ctx, hero, self.heroes_pick_up_weights)

        # If the parameter entered is too short
        if invalid:
            await ctx.send(invalid)
            return

        # If hero is indeed present in current pick up banner
        if present:
            boxes, reply = self.pickUpPresent(
                ctx,
                one_or_ten,
                hero_banner,
                self.heroes,
                self.heroes_pick_up_weights,
                self.heroes_last_slot_weights
            )
            await self.summonDisplay(ctx, one_or_ten, boxes, reply)
        # If not, then send error message
        else:
            await ctx.send(
                f"Ermmm, <@{ctx.author.id}>. The hero you mentioned is not in the current pick up banner."
            )

    # Summon heroes on the normal banner
    @commands.command(
        name="summon.equipment",
        help="Summons single or ten equipments on the normal banner.",
        aliases=["summon.equip", "summonequipment", "summonequip", "s.e", "se"]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def summonEquipment(self, ctx, one_or_ten):
        boxes, reply = self.calcResults(
            ctx, one_or_ten, self.equipments, self.equipments_weights, self.equipments_last_slot_weights)
        await self.summonDisplay(ctx, one_or_ten, boxes, reply)

    # Summon heroes on the pick up banner
    @commands.command(
        name="summon.equipment.pickup",
        help="Summons single or ten equipments on the pick up banner.",
        aliases=["summon.equip.pickup", "summonequipmentpickup",
                 "summonequippickup", "s.e.p", "sep"]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def summonEquipmentPickUp(self, ctx, equipment, one_or_ten):
        # Check if pick up is available
        present, invalid, equipment_banner = self.checkPickUpAvailability(
            ctx, equipment, self.equipments_pick_up_weights)

        # If the parameter entered is too short
        if invalid:
            await ctx.send(invalid)
            return

        # If equipment is indeed present in current pick up banner
        if present:
            boxes, reply = self.pickUpPresent(
                ctx,
                one_or_ten,
                equipment_banner,
                self.equipments,
                self.equipments_pick_up_weights,
                self.equipments_last_slot_weights
            )
            await self.summonDisplay(ctx, one_or_ten, boxes, reply)
        # If not, then send error message
        else:
            await ctx.send(
                f"Ermmm, <@{ctx.author.id}>. The equipment you mentioned is not in the current pick up banner."
            )


def setup(bot):
    bot.add_cog(Summon(bot))
