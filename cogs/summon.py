#!/usr/bin/env python

import time
import random
import discord
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
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            2.750,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            19.000,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
            78.250,
        ]

    @commands.command()
    async def summon(self, ctx, one_or_ten):
        if one_or_ten == "10" or one_or_ten == "ten":
            results = random.choices(self.heroes, self.weights, k=10)
        elif one_or_ten == "1" or one_or_ten == "one":
            results = random.choices(self.heroes, self.weights, k=1)
        else:
            results = [
                f"Hey, <@{ctx.author.id}>. I don't think thats a valid summon value. LOL!",
                f"Ermm.. its either 10 or 1! Get yourself corrected, <@{ctx.author.id}>!",
                f"You sure there's a {one_or_ten} summon, <@{ctx.author.id}>? There's only 1 and 10 summon!"
            ]

            await ctx.send(random.choice(results))

        if one_or_ten == "10" or one_or_ten == "ten" or one_or_ten == "1" or one_or_ten == "one":
            three_star = False
            ailie = False

            msg = await ctx.send(
                f"Wait up, <@{ctx.author.id}>. Summoning {one_or_ten} now..")

            time.sleep(3)

            i = 1
            for result in results:
                if "★★★" in result:
                    three_star = True
                if "Ailie" in result:
                    ailie = True

                await msg.edit(content=msg.content + f"\n{i}. {result}")
                i += 1

            if three_star:
                await ctx.send(
                    f"WOW! W-w-waaaiittt a second, <@{ctx.author.id}>.. Is that a freaking 3 star hero?!"
                )
            else:
                if ailie:
                    await ctx.send(
                        f"Think positive, <@{ctx.author.id}>! At least you got me :D"
                    )
                else:
                    await ctx.send(
                        f"You just suck at gachas, <@{ctx.author.id}>..")


def setup(bot):
    bot.add_cog(Summon(bot))