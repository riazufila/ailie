#!/usr/bin/env python

import time
import random
from discord.ext import commands


class Summon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.heroes = [
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
            "★★★ Chosen One's Archpriestess Veronica", "★★ Fe/Male Knight",
            "★★ Knight Captain Eva", "★★ Red Hood Elvira", "★★ White Beast",
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
            "★★ Battleball Girl Rie", "★★ Dragon Seeking Girl Neva",
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
        ]
        self.weights = [
            2.750, 2.750, 2.750, 2.750, 2.750, 2.750, 2.750, 2.750, 2.750,
            2.750, 2.750, 2.750, 2.750, 2.750, 2.750, 2.750, 2.750, 2.750,
            2.750, 2.750, 2.750, 2.750, 2.750, 2.750,
            19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000,
            19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000,
            19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000,
            19.000, 19.000, 19.000, 19.000, 19.000,
            78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250,
            78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250,
            78.250, 78.250, 78.250, 78.250, 78.250, 78.250
        ]
        self.heroes_banner = [
            "★★★ Chosen One's Archpriestess Veronica",
            "★★★ Nine-tailed Fox Garam",
            "★★★ Noble Succubus Bianca",
            "★★★ Grand Admiral Marina"
        ]
        self.weights_banner = [
            1.375, 1.375, 1.375, 1.375, 1.375, 1.375, 1.375, 1.375, 1.375,
            1.375, 1.375, 1.375, 1.375, 1.375, 1.375, 1.375, 1.375, 1.375,
            1.375, 1.375, 1.375, 1.375, 1.375, 1.375,
            19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000,
            19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000,
            19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000, 19.000,
            19.000, 19.000, 19.000, 19.000, 19.000,
            78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250,
            78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250, 78.250,
            78.250, 78.250, 78.250, 78.250, 78.250, 78.250
        ]

    # Calculate the chances for those 3 stars
    async def calcResults(self, ctx, one_or_ten, w, hero=None):
        if one_or_ten == "10" or one_or_ten == "ten":
            results = random.choices(self.heroes, w, k=10)
        elif one_or_ten == "1" or one_or_ten == "one":
            results = random.choices(self.heroes, w, k=1)
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

            time.sleep(3)

            i = 1
            for result in results:
                if "★★★" in result:
                    three_star = True
                if result in self.heroes_banner:
                    obtainedPickup = True
                if "Ailie" in result:
                    ailie = True

                await msg.edit(content=msg.content + f"\n{i}. {result}")
                i += 1

            if three_star and not obtainedPickup and hero:
                await ctx.send(f"I see 3 star hero. But no {hero}.. Sad life, <@{ctx.author.id}>")
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

    # Lists the current pickup banner
    @commands.command(name="banner.info", help="Lists the current pickup banner.")
    async def bannerInfo(self, ctx):
        msg = await ctx.send(f"One sec, <@{ctx.author.id}>. Getting those Pick Up Banner info.")
        time.sleep(1.5)

        i = 1
        for hero_banner in self.heroes_banner:
            await msg.edit(content=msg.content + f"\n{i}. {hero_banner}")
            i += 1

    # Summons on the normal banner
    @commands.command(name="summon.normal", help="Summons single or ten units on the normal banner.")
    async def summonNormal(self, ctx, one_or_ten):
        await self.calcResults(ctx, one_or_ten, self.weights)

    # Summons on the pick up banner
    @commands.command(name="summon.banner", help="Summons single or ten units on the pick up banner.")
    async def summonBanner(self, ctx, hero, one_or_ten):
        self.weights_banner = self.weights
        present = False

        for hero_banner in self.heroes_banner:
            if hero_banner.lower().__contains__(hero.lower()):
                present = True
                index = self.heroes.index(hero_banner)
                await self.calcResults(ctx, one_or_ten, self.weights_banner, self.heroes[index])

        if not present:
            await ctx.send(f"Ermmm, <@{ctx.author.id}>. The hero you mentioned is not in the current pick up banner. Do ailie;banner.info to check the current pick up banner.")


def setup(bot):
    bot.add_cog(Summon(bot))
