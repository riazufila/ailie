#!/usr/bin/env python

import asyncio
import random
from discord.ext import commands


class Hero(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.heroes = [
            [
                "★ Linda the Senior Guardian", "★ Guardian Member Bob",
                "★ Byrule's Hero Hyper", "★ Peddler Maria", "★ Caravan Lisa",
                "★ Elf Archer Leah", "★ Teaten Ninja Jay",
                "★ Ultra Rationale Dragon", "★ Super Teaten 2 Blade",
                "★ Homecoming Queen Mina", "★ Dragon Talon Clan Hoshida",
                "★ Succubus Researcher Peggy", "★ Relic Collector Ailie",
                "★ Ghost Guard Oralie", "★ Baby White Tiger Kang",
                "★ Merchant Agatha", "★ Doctor DaVinci", "★ Class President Kate",
                "★ Town Guide Zoe", "★ Monk Disciple Rio", "★ Private Nyan",
                "★ Junior Engineer Marty Junior"
            ],
            [
                "★★ Fe/Male Knight", "★★ Knight Captain Eva",
                "★★ Red Hood Elvira", "★★ White Beast",
                "★★ Vampire Girl Karina", "★★ Innkeeper Loraine",
                "★★ Twin Fighter Lavi", "★★ Twin Healer Favi",
                "★★ Leaf Fairy Aoba", "★★ Mad Scientist Gremory",
                "★★ Pirate Rachel", "★★ Sniper Hekate", "★★ Innuit Girl Coco",
                "★★ Engineer Marianne", "★★ Scientist Sohee",
                "★★ Kung Fu Master Mei/Fei", "★★ Desert Mercenary Marvin",
                "★★ Aspiring Warrior Craig", "★★ Swordsman Akayuki",
                "★★ Dragon Talon Clan Ranpang", "★★ Succubus Adventurer Yuze",
                "★★ Princess Aisha", "★★ Dragon Knight Shapira",
                "★★ Swindler Magician Dolf", "★★ Dual-personality Maid Amy",
                "★★ Fire Dragon Girgas", "★★ Dimension Traveler Catherine",
                "★★ Battleball Girl Rie", "★★ Dragon Seeking Girl Neva"
            ],
            [
                "★★★ Goddess of War Plitvice", "★★★ Knight Lady Lapice",
                "★★★ Grand Admiral Marina", "★★★ Executive Red Hood Arabelle",
                "★★★ Idol Captain Eva", "★★★ Flower Girl Bari",
                "★★★ Ice Witch Lupina", "★★★ Scrivener Lahn",
                "★★★ Movie Star Eugene", "★★★ Dancing Archer Tinia",
                "★★★ Dragon Avatar Vishuvac", "★★★ Eight-tailed Fox Nari",
                "★★★ Noble Succubus Bianca", "★★★ Mecha Warrior Oghma",
                "★★★ Golem Rider Alef", "★★★ Exorcist Miya", "★★★ Future Princess",
                "★★★ Nine-tailed Fox Garam", "★★★ Dark Magician Beth",
                "★★★ Santa's Little Helper Rue", "★★★ Archangel Gabriel",
                "★★★ Drunken Swordmaster Lynn", "★★★ Future Knight",
                "★★★ Chosen One's Archpriestess Veronica"
            ]
        ]
        self.heroes_banner = [
            "★★★ Chosen One's Archpriestess Veronica",
            "★★★ Nine-tailed Fox Garam",
            "★★★ Noble Succubus Bianca",
            "★★★ Grand Admiral Marina"
        ]
        self.heroes_with_banner = []
        self.weights = [78.250, 19.000, 2.750]
        self.weights_banner = [78.250, 19.000, 1.375, 1.375]
        self.weights_last = [97.25, 2.75]

    # Calculate the chances for those 3 stars
    async def calcResults(self, ctx, one_or_ten, h, w, hero=None):
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

            await ctx.send(random.choice(results))

        if one_or_ten == "10" or one_or_ten == "ten" or one_or_ten == "1" or one_or_ten == "one":
            three_star = False
            obtainedPickup = False
            ailie = False

            msg = await ctx.send(
                f"Wait up, <@{ctx.author.id}>. Summoning {one_or_ten} now..")

            await asyncio.sleep(3)

            pity = False
            check = False
            i = 1

            for result in results:
                result = random.choices(result, k=1)
                for r in result:
                    if one_or_ten == "10" or one_or_ten == "ten":
                        if not "★★★ " in r and not check:
                            pity = True
                        if not "★★ " in r and not check:
                            pity = True
                        else:
                            pity = False
                            check = True

                    if "★★★" in r:
                        three_star = True
                    if r == hero:
                        obtainedPickup = True
                    if "Ailie" in r:
                        ailie = True

                    await msg.edit(content=msg.content + f"\n{i}. {r}")
                    await asyncio.sleep(1.5)
                    i += 1

            if pity:
                heroes_pity = self.heroes[:]
                heroes_pity.pop(0)
                results = random.choices(heroes_pity, self.weights_last, k=1)
                for pity_result in results:
                    p_r = random.choices(pity_result, k=1)
                    for pr in p_r:
                        if "★★★" in pr:
                            three_star = True
                        if pr == hero:
                            obtainedPickup = True
                        if "Ailie" in pr:
                            ailie = True

                        await msg.edit(content=msg.content + f"\n10. {pr}")
                        await asyncio.sleep(1.5)

            if not pity:
                results = random.choices(h, w, k=1)
                for not_pity_result in results:
                    n_p_r = random.choices(not_pity_result, k=1)
                    for npr in n_p_r:
                        if "★★★" in npr:
                            three_star = True
                        if npr == hero:
                            obtainedPickup = True
                        if "Ailie" in npr:
                            ailie = True

                        await msg.edit(content=msg.content + f"\n10. {npr}")
                        await asyncio.sleep(1.5)

            if three_star and not obtainedPickup and hero:
                await ctx.send(f"I see 3 star hero. But no {hero}.. Sad life, <@{ctx.author.id}>.")
            if three_star and obtainedPickup and hero:
                await ctx.send(f"WOHOOOOOOOOOOOOOOOOOO, <@{ctx.author.id}>! You got the pick up hero!")
            if three_star and not hero:
                await ctx.send(
                    f"WOW! W-w-waaaiittt a second, <@{ctx.author.id}>..  Is that a freaking 3 star hero?!"
                )

            if not three_star and ailie:
                await ctx.send(
                    f"Think positive, <@{ctx.author.id}>! At least you got me :D"
                )
            elif not three_star and not ailie:
                await ctx.send(
                    f"You just suck at gachas, <@{ctx.author.id}>..")

    # On cooldown
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Hey, <@{ctx.author.id}>.. {error}!")

    # Lists the current pickup banner
    @commands.command(name="hero.pickup.info", help="Lists the current pickup banner.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def bannerInfo(self, ctx):
        msg = await ctx.send(f"One sec, <@{ctx.author.id}>. Getting those Pick Up Banner info.")
        await asyncio.sleep(1.5)

        i = 1
        for hero_banner in self.heroes_banner:
            await msg.edit(content=msg.content + f"\n{i}. {hero_banner}")
            i += 1

    # Summons on the normal banner
    @commands.command(name="summon.hero", help="Summons single or ten units on the normal banner.")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def summonHero(self, ctx, one_or_ten):
        await self.calcResults(ctx, one_or_ten, self.heroes, self.weights)

    # Summons on the pick up banner
    @commands.command(name="summon.hero.pickup", help="Summons single or ten units on the pick up banner.")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def summonHeroPickUp(self, ctx, hero, one_or_ten):
        self.heroes_with_banner = self.heroes[:]
        present = False
        hero_banner = ""

        for hero_banner in self.heroes_banner:
            if hero_banner.lower().__contains__(hero.lower()):
                present = True
                break

        if present:
            for heroes_list in self.heroes:
                if hero_banner in heroes_list:
                    for hero_list in heroes_list:
                        if hero_banner == hero_list:
                            buffer = self.heroes[2][:]
                            buffer.remove(hero_banner)
                            self.heroes_with_banner.pop(2)
                            self.heroes_with_banner.append(buffer)
                            self.heroes_with_banner.append([hero_banner, ])

                            await self.calcResults(ctx, one_or_ten, self.heroes_with_banner, self.weights_banner, self.heroes_with_banner[3][0])
                            break
                    break

        if not present:
            await ctx.send(f"Ermmm, <@{ctx.author.id}>. The hero you mentioned is not in the current pick up banner.")


def setup(bot):
    bot.add_cog(Hero(bot))
