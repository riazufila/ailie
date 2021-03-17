#!/usr/bin/env python

import asyncio
import random
import csv
from discord.ext import commands


class Hero(commands.Cog):
    def __init__(self, bot):
        # Bot assigned to class
        self.bot = bot

        # Get all the data for heroes and pick up heroes
        self.heroes = self.getRecords("csv/heroes.csv", [[], [], []])
        self.pick_up_heroes = self.getRecords("csv/pick-up-heroes.csv", [])

        # Weights declaration for probability upon summon
        self.weights = [78.250, 19.000, 2.750]
        self.pick_up_weights = [78.250, 19.000, 1.375, 1.375]
        self.last_slot_weights = [97.25, 2.75]

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
    def checkWhatIsSummoned(self, r, hero):
        # Initialize counters
        three_star = False
        obtainedPickup = False
        ailie = False

        if "★★★" in r:
            three_star = True
        if r == hero:
            obtainedPickup = True
        if "Ailie" in r:
            ailie = True

        return three_star, obtainedPickup, ailie

    # Replies are sent back according to the summons obtained
    def getRepliesForSpecificSummons(self, ctx, hero, three_star, obtainedPickup, ailie):
        # Initialize reply variable
        reply = ""

        # Get funky replies
        if three_star and not obtainedPickup and hero:
            reply = f"I see 3 star hero. But no {hero}.. Sad life, <@{ctx.author.id}>."
        if three_star and obtainedPickup and hero:
            reply = f"WOHOOOOOOOOOOOOOOOOOO, <@{ctx.author.id}>! You got the pick up hero!"
        if three_star and not hero:
            reply = f"WOW! W-w-waaaiittt a second, <@{ctx.author.id}>..  Is that a freaking 3 star hero?!"

        if not three_star and ailie:
            reply = f"Think positive, <@{ctx.author.id}>! At least you got me :D"
        elif not three_star and not ailie:
            reply = f"You just suck at gachas, <@{ctx.author.id}>.."

        return reply

    # Check if pick up chosen is available at the current time
    def checkPickUpAvailability(self, ctx, hero):
        # Initialize variable to check invalid input
        invalid = False
        present = False
        hero_banner = ""

        # Check if the parameter send is lesser than 5 characters
        # If its lesser, then return error message
        if len(hero) < 5:
            return f"Yo, <@{ctx.author.id}>. At least put 4 characters please?"

        # Check if selected pick up is available
        for hero_banner in self.pick_up_heroes:
            if hero_banner.lower().__contains__(hero.lower()):
                present = True
                break

        return present, invalid, hero_banner

    # Create new list with pick up included in a separate list in main list
    def pickUpPresent(self, ctx, one_or_ten, hero_banner):
        # Initialize counters
        pick_up_hero_pool = self.heroes[:]
        boxes = []
        reply = ""

        for heroes_list in self.heroes:
            if hero_banner in heroes_list:
                for hero_list in heroes_list:
                    if hero_banner == hero_list:
                        buffer = self.heroes[2][:]
                        buffer.remove(hero_banner)
                        pick_up_hero_pool.pop(2)
                        pick_up_hero_pool.append(buffer)
                        pick_up_hero_pool.append([hero_banner, ])

                        boxes, reply = self.calcResults(
                            ctx, one_or_ten, pick_up_hero_pool, self.pick_up_weights, pick_up_hero_pool[3][0])

                        break
                break

        return boxes, reply

    # Calculate the chances in summons
    def calcResults(self, ctx, one_or_ten, h, w, hero=None):
        # Initialize value to return later
        reply = ""
        boxes = []

        # Check for summon values be it 10, 1 or invalid
        if one_or_ten == "10" or one_or_ten == "ten":
            results = random.choices(h, w, k=9)
        elif one_or_ten == "1" or one_or_ten == "one":
            results = random.choices(h, w, k=1)
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
            three_star = False
            obtainedPickup = False
            ailie = False
            pity = False
            check = False

            # Iterate through results
            for result in results:
                result = random.choices(result, k=1)
                for r in result:
                    if one_or_ten == "10" or one_or_ten == "ten":
                        # To determine if pity is deserved for last slot summon
                        if not "★★★ " in r and not check:
                            pity = True
                        if not "★★ " in r and not check:
                            pity = True
                        else:
                            pity = False
                            check = True

                    # Check what is being summoned for specific replies
                    three_star, obtainedPickup, ailie = self.checkWhatIsSummoned(
                        r, hero)
                    # Append the summons to boxes to be returned
                    boxes.append(r)

            # If the summon is with a value 10 and the summons from 1 until 9 is bad
            # (No 2 star and above for heroes and no 4 star and above for equipments),
            # then, the user deserves higher rates
            if pity:
                heroes_pity = self.heroes[:]
                heroes_pity.pop(0)
                results = random.choices(
                    heroes_pity, self.last_slot_weights, k=1)
                for pity_result in results:
                    p_r = random.choices(pity_result, k=1)
                    for pr in p_r:
                        # Check what is being summoned for specific replies
                        three_star, obtainedPickup, ailie = self.checkWhatIsSummoned(
                            pr, hero)
                        # Append the summons to boxes to be returned
                        boxes.append(pr)

            # If the user doesn't deserve pity, then continue with normal rates
            if not pity:
                results = random.choices(h, w, k=1)
                for not_pity_result in results:
                    n_p_r = random.choices(not_pity_result, k=1)
                    for npr in n_p_r:
                        # Check what is being summoned for specific replies
                        three_star, obtainedPickup, ailie = self.checkWhatIsSummoned(
                            npr, hero)
                        # Append the summons to boxes to be returned
                        boxes.append(npr)

            # Get specific replies corresponding to the summons
            reply = self.getRepliesForSpecificSummons(
                ctx, hero, three_star, obtainedPickup, ailie)

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
        name="hero.pickup.info",
        help="Lists the current pickup banner.",
        aliases=["heropickupinfo", "h.p.i", "hpi"]
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def heroPickUpInfo(self, ctx):
        message = ""
        i = 1

        # Store all the information inside a string
        for pick_up_info in self.pick_up_heroes:
            message = message + f"\n{i}. {pick_up_info}"
            i += 1

        # Send the string in one take so rate limit doesn't occur
        await ctx.send(f"Hello, <@{ctx.author.id}>. These are the Pick Up Banner ongoing. {message}")

    # Summons on the normal banner
    @commands.command(
        name="summon.hero",
        help="Summons single or ten heroes on the normal banner.",
        aliases=["summonhero", "s.h", "sh"]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def summonHero(self, ctx, one_or_ten):
        boxes, reply = self.calcResults(
            ctx, one_or_ten, self.heroes, self.weights)
        await self.summonDisplay(ctx, one_or_ten, boxes, reply)

    # Summons on the pick up banner
    @commands.command(
        name="summon.hero.pickup",
        help="Summons single or ten heroes on the pick up banner.",
        aliases=["summonheropickup", "s.h.p", "shp"]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def summonHeroPickUp(self, ctx, hero, one_or_ten):
        # Check if pick up is available
        present, invalid, hero_banner = self.checkPickUpAvailability(ctx, hero)

        # If the parameter entered is too short
        if invalid:
            await ctx.send(invalid)
            return

        # If hero is indeed present in current pick up banner
        if present:
            boxes, reply = self.pickUpPresent(ctx, one_or_ten, hero_banner)
            await self.summonDisplay(ctx, one_or_ten, boxes, reply)
        # If not, then send error message
        else:
            await ctx.send(
                f"Ermmm, <@{ctx.author.id}>. The hero you mentioned is not in the current pick up banner."
            )


def setup(bot):
    bot.add_cog(Hero(bot))
