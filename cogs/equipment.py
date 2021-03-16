#!/usr/bin/env python

import asyncio
import random
from discord.ext import commands


class Equipment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.equipments = [
            [
                "★★ Tutorial Sword", "★★ Storm Sword", "★★ Crude Sword",
                "★★ Molten Sword", "★★ Bronze Sword", "★★ Knight Sword",
                "★★ Saber", "★★ Curved Sword", "★★ Executioner Sword",
                "★★ Assassin's Dagger", "★★ Tutorial Two-Handed Sword", "★★ Trident Two-Handed Sword",
                "★★ C&C Two-Handed Sword", "★★ Charge Blade", "★★ Zweihander",
                "★★ Lightning Rock Two-Handed Sword", "★★ Flame Thorn Two-Handed Sword",
                "★★ Meteor Core Two-Handed Sword", "★★ Gaia Blade", "★★ Rifle",
                "★★ Blunderbuss Gun", "★★ Strengthened Blunderbuss Gun", "★★ Double Barrel Shotgun",
                "★★ Energy Rifle", "★★ Atomic Rifle", "★★ Medic Bio Rifle",
                "★★ lon Cannon", "★★ MM20 Assault Rifle", "★★ Basic Bow",
                "★★ Devil Wing Bow", "★★ Molten Bow", "★★ Sniper Bow",
                "★★ Magic Bow", "★★ Chasers Bow", "★★ Icicle Bow",
                "★★ Archery Bow", "★★ Solar Eclipse Bow", "★★ Basic Basket",
                "★★ Bomb Basket", "★★ Easter Basket", "★★ Waterbomb Basket",
                "★★ Flower Basket", "★★ Cake Basket", "★★ Witch's Cauldron Basket",
                "★★ Drug Basket", "★★ Health Food Basket", "★★ Training Staff",
                "★★ Ice Staff", "★★ Frigid Crystal Staff", "★★ Amethyst Staff",
                "★★ Black Quartz Staff", "★★ Devil Snake Staff", "★★ Firefly Staff",
                "★★ Flame Staff", "★★ Ankh Staff", "★★ Rugged Gauntlet",
                "★★ Bull's Gauntlet", "★★ Iron Fist Gauntlet", "★★ Black Spider Gauntlet",
                "★★ Gold Chaser Gauntlet", "★★ Carpenter's Gauntlet", "★★ Sun Cultist Gauntlet",
                "★★ Steam Gear Fist Gauntlet", "★★ Training Claw", "★★ Bronze Claw",
                "★★ Yeti Claw", "★★ Hematite Claw", "★★ Snowy Wolf Claw",
                "★★ Blade Claw", "★★ Automatic Claw", "★★ Earth's Fang Claw",
                "★★ Sphinx Claw", "★★ Shape of Darkness Claw", "★★ Thunder Claw",
                "★★ Tutorial Shield", "★★ Circular Wood Shield", "★★ Iron Shield",
                "★★ Molten Shield", "★★ Skeleton Shield", "★★ War Shield",
                "★★ Copper Shield", "★★ Mate's Shield", "★★ Rose Shield",
                "★★ Pearl Ring", "★★ Gold Ring", "★★ Emerald Ring",
                "★★ Pearl Necklace", "★★ Obsidian Necklace", "★★ Magic Fruit Necklace",
                "★★ Ancient God Ring", "★★ Bell Necklace", "★★ Mercenaries Brooch",
                "★★ Necklace of Desire", "★★ Earring of the Cultists", "★★ Goblin Tribe Totem"
            ],
            [
                "★★★ Scale Sword", "★★★ Demon Sword", "★★★ Fire Sword",
                "★★★ Golden Sword", "★★★ Copper Sword", "★★★ Earth's Tooth",
                "★★★ Fantasy Sword", "★★★ Booster Sword", "★★★ Blue Two-Handed Sword",
                "★★★ Golem’s Two-Handed Sword", "★★★ Cloud Two-Handed Sword", "★★★ Hero's Two-Handed Sword",
                "★★★ Paimon's Two-Handed Sword", "★★★ Contracted Two-handed Sword",
                "★★★ Dark Knight Two-Handed Sword", "★★★ Blue Spider Two-Handed Sword",
                "★★★ Earth Song Two-Handed Sword", "★★★ Imperial Two-handed Sword",
                "★★★ Black Thorn Two-Handed Sword", "★★★ Crystal Shotgun", "★★★ AK",
                "★★★ Antique Rifle", "★★★ Musket Rifle", "★★★ Alien Rifle",
                "★★★ Desert Hunter Rifle", "★★★ Flame Cobra Rifle", "★★★ Ghost Energy Buster",
                "★★★ Gatling Gun", "★★★ Forest Hunter Bow", "★★★ Brilliance Bow",
                "★★★ Charger Bow", "★★★ Banshee's Scream", "★★★ Volcano Bow",
                "★★★ Demon Bow", "★★★ Flower Bow", "★★★ Flame Festival Bow",
                "★★★ Rail Bow", "★★★ Wolfs Howl Bow", "★★★ Frost Drop Bow",
                "★★★ Santa's Gift Basket", "★★★ Cat Basket", "★★★ Ice Crystal Basket",
                "★★★ Beat Basket", "★★★ Horror Basket", "★★★ Shark Basket",
                "★★★ Fireworks Basket", "★★★ Steel Bag", "★★★ Vine Basket",
                "★★★ Trophy Basket", "★★★ Lotus Basket", "★★★ Frost Comet Staff",
                "★★★ Guide's Frigid Staff", "★★★ Evil Spirit's Call Staff", "★★★ Frost Eye Staff",
                "★★★ Harvest Staff", "★★★ Flame Wing Staff", "★★★ Fire Shape Staff",
                "★★★ Tear of Light Staff", "★★★ Black Spider Staff", "★★★ Staff of Elegance",
                "★★★ Gargoyle Staff", "★★★ Program Staff", "★★★ Black Leather Gauntlet",
                "★★★ Neko Punch Gauntlet", "★★★ Volcano Punch", "★★★ Galaxy Gauntlet",
                "★★★ Gigantic Fist", "★★★ Gauntlet of Belief", "★★★ Marauder Gauntlet",
                "★★★ Venom Gauntlet", "★★★ Blizzard Brawl Gauntlet", "★★★ Gauntlet of Fury",
                "★★★ Tiger Hunter Gauntlet", "★★★ Thorns Gauntlet", "★★★ Volcano’s Fury Claw",
                "★★★ Demon Claw", "★★★ Guardian's Claw", "★★★ Black Rose Claw",
                "★★★ Golden Scorpion Claw", "★★★ Rune Rock Claw", "★★★ Cold Thorn",
                "★★★ Oni Claw", "★★★ Destruction Claw", "★★★ Knight Shield",
                "★★★ Demon Shield", "★★★ Tanker Shield", "★★★ Blade Shied",
                "★★★ Charge Shield", "★★★ Mirror Shield", "★★★ Seth Shield",
                "★★★ Wyvern Shield", "★★★ Wolf Ring", "★★★ Blessing Necklace",
                "★★★ Pearl Earring", "★★★ Amethyst Earring", "★★★ Angel Necklace",
                "★★★ Rabbit Foot", "★★★ Sharp Shooter", "★★★ Wood Fairy Ring",
                "★★★ Ring of Fortress", "★★★ Frost Flower Ring", "★★★ Sacred Rosary",
                "★★★ Ring of Heat", "★★★ Crescent Moon Earring", "★★★ Earring of Dark Desire",
                "★★★ Wedding Ring of Earth", "★★★ Goddess Statue", "★★★ Gold Pocket Watch",
                "★★★ Greed Earring", "★★★ Ring of Greed"
            ],
            [
                "★★★★ Scale Sword", "★★★★ Demon Sword", "★★★★ Fire Sword",
                "★★★★ Golden Sword", "★★★★ Dryad Sword", "★★★★ Moonlight Sword",
                "★★★★ Copper Sword", "★★★★ Blood Sword", "★★★★ Earth's Tooth",
                "★★★★ Fantasy Sword", "★★★★ Gold Hilt Sword", "★★★★ Purifying Sword",
                "★★★★ Booster Sword", "★★★★ Blue Two-Handed Sword", "★★★★ Golem’s Two-Handed Sword",
                "★★★★ Cloud Two-Handed Sword", "★★★★ Hero's Two-Handed Sword",
                "★★★★ Paimon's Two-Handed Sword", "★★★★ Contracted Two-handed Sword",
                "★★★★ Dark Knight Two-Handed Sword", "★★★★ Lunar Eclipse Two-Handed Sword",
                "★★★★ Blood Knight Blade", "★★★★ Blue Spider Two-Handed Sword", "★★★★ Glacier Blade",
                "★★★★ Galaxy Two-Handed Sword", "★★★★ Earth Song Two-Handed Sword",
                "★★★★ Imperial Two-handed Sword", "★★★★ Black Thorn Two-Handed Sword",
                "★★★★ Crystal Shotgun", "★★★★ AK", "★★★★ Antique Rifle",
                "★★★★ Musket Rifle", "★★★★ Turbo Power Rifle", "★★★★ Alien Rifle",
                "★★★★ Desert Hunter Rifle", "★★★★ Flame Cobra Rifle", "★★★★ Ghost Energy Buster",
                "★★★★ Gatling Gun", "★★★★ Railshot Rifle", "★★★★ LNW-2000",
                "★★★★ Graviton Cannon", "★★★★ Geothermal Plasma Rifle", "★★★★ Forest Hunter Bow",
                "★★★★ Brilliance Bow", "★★★★ Charger Bow", "★★★★ Banshee's Scream",
                "★★★★ Volcano Bow", "★★★★ Ancient Elfs bow", "★★★★ Demon Bow",
                "★★★★ Flower Bow", "★★★★ Flame Festival Bow", "★★★★ Rail Bow",
                "★★★★ Wolfs Howl Bow", "★★★★ Shape of Flame Bow", "★★★★ Cold Heart",
                "★★★★ Sun Garden Bow", "★★★★ Guardian's Bow", "★★★★ Wing of Terror",
                "★★★★ Frost Drop Bow", "★★★★ Santa's Gift Basket", "★★★★ Fire Hatchling Basket",
                "★★★★ Cat Basket", "★★★★ Ice Crystal Basket", "★★★★ Beat Basket",
                "★★★★ Horror Basket", "★★★★ Halloween Basket", "★★★★ Shark Basket",
                "★★★★ Fireworks Basket", "★★★★ Steel Bag", "★★★★ Fairy Shelter Basket",
                "★★★★ Shining Jewel Basket", "★★★★ Vine Basket", "★★★★ Trophy Basket",
                "★★★★ Ocean Basket", "★★★★ Random Basket", "★★★★ Lotus Basket",
                "★★★★ Frost Comet Staff", "★★★★ Guide's Frigid Staff", "★★★★ Ice Moon Staff",
                "★★★★ Evil Spirit's Call Staff", "★★★★ Dark Dragon Staff", "★★★★ Grip of Darkness Staff",
                "★★★★ Frost Eye Staff", "★★★★ Harvest Staff", "★★★★ Jewel of Verdure Staff",
                "★★★★ Flame Wing Staff", "★★★★ Fire Shape Staff", "★★★★ Sunshine Staff",
                "★★★★ Arcane Staff", "★★★★ Tear of Light Staff", "★★★★ Wing of Hope Staff",
                "★★★★ Black Spider Staff", "★★★★ Staff of Elegance", "★★★★ Magic Girl Staff",
                "★★★★ Gargoyle Staff", "★★★★ Program Staff", "★★★★ Black Leather Gauntlet",
                "★★★★ Neko Punch Gauntlet", "★★★★ Volcano Punch", "★★★★ Galaxy Gauntlet",
                "★★★★ Gigantic Fist", "★★★★ Gauntlet of Brilliance", "★★★★ Gauntlet of Belief",
                "★★★★ Marauder Gauntlet", "★★★★ Venom Gauntlet", "★★★★ Blizzard Brawl Gauntlet",
                "★★★★ Flame Dragon Claw Gauntlet", "★★★★ Blizzard Shard Gauntlet",
                "★★★★ Assassination Gauntlet", "★★★★ Lucky Punch", "★★★★ Gauntlet of Fury",
                "★★★★ Tiger Hunter Gauntlet", "★★★★ Thorns Gauntlet", "★★★★ Volcano’s Fury Claw",
                "★★★★ Demon Claw", "★★★★ Guardian's Claw", "★★★★ Black Rose Claw",
                "★★★★ Dragon Tooth Claw", "★★★★ Golden Scorpion Claw", "★★★★ Rune Rock Claw",
                "★★★★ Cold Thorn", "★★★★ Oni Claw", "★★★★ Phoenix Wing Claw",
                "★★★★ Justice Claw", "★★★★ Blizzard Fang Claw", "★★★★ Destruction Claw",
                "★★★★ Black Lion Fang Claw", "★★★★ Knight Shield", "★★★★ Demon Shield",
                "★★★★ Tanker Shield", "★★★★ Angel Shield", "★★★★ Vampire Shield",
                "★★★★ Blade Shied", "★★★★ Ice Princess’ Shield", "★★★★ Charge Shield",
                "★★★★ Mirror Shield", "★★★★ Seth Shield", "★★★★ Punishment Shield",
                "★★★★ Wyvern Shield", "★★★★ Wolf Ring", "★★★★ Blessing Necklace",
                "★★★★ Pearl Earring", "★★★★ Amethyst Earring", "★★★★ Ring of Belief",
                "★★★★ Black Crown Ring", "★★★★ Chaste Love Brooch", "★★★★ Angel Necklace",
                "★★★★ Rabbit Foot", "★★★★ Sharp Shooter", "★★★★ Dark Magic Ring",
                "★★★★ Wood Fairy Ring", "★★★★ Ring of Fortress", "★★★★ Frost Flower Ring",
                "★★★★ Sacred Rosary", "★★★★ Ring of Heat", "★★★★ Ocean Earring",
                "★★★★ Crescent Moon Earring", "★★★★ Cursed Necklace", "★★★★ Earring of Dark Desire",
                "★★★★ Wedding Ring of Earth", "★★★★ Goddess Statue", "★★★★ Gold Pocket Watch",
                "★★★★ Greed Earring", "★★★★ Ring of Greed", "★★★★ Honor Ring"
            ],
            [
                "★★★★★ Scale Sword", "★★★★★ Demon Sword", "★★★★★ Fire Sword",
                "★★★★★ Golden Sword", "★★★★★ Dryad Sword", "★★★★★ Moonlight Sword",
                "★★★★★ Copper Sword", "★★★★★ Blood Sword", "★★★★★ Earth's Tooth",
                "★★★★★ Fantasy Sword", "★★★★★ Holy Sword", "★★★★★ Gold Hilt Sword",
                "★★★★★ Phoenix Sword", "★★★★★ Purifying Sword", "★★★★★ Booster Sword",
                "★★★★★ Blue Two-Handed Sword", "★★★★★ Golem's Two-Handed Sword",
                "★★★★★ Cloud Two-Handed Sword", "★★★★★ Hero's Two-Handed Sword",
                "★★★★★ Paimon's Two-Handed Sword", "★★★★★ Contracted Two-handed Sword",
                "★★★★★ Dark Knight Two-Handed Sword", "★★★★★ Lunar Eclipse Two-Handed Sword",
                "★★★★★ Arondight", "★★★★★ Blood Knight Blade", "★★★★★ Blue Spider Two-Handed Sword",
                "★★★★★ Glacier Blade", "★★★★★ Galaxy Two-Handed Sword", "★★★★★ Earth Song Two-Handed Sword",
                "★★★★★ Imperial Two-handed Sword", "★★★★★ Black Thorn Two-Handed Sword",
                "★★★★★ Crystal Shotgun", "★★★★★ AK", "★★★★★ Antique Rifle", "★★★★★ Musket Rifle",
                "★★★★★ Turbo Power Rifle", "★★★★★ Alien Rifle", "★★★★★ Desert Hunter Rifle",
                "★★★★★ Flame Cobra Rifle", "★★★★★ Ghost Energy Buster", "★★★★★ Gatling Gun",
                "★★★★★ Railshot Rifle", "★★★★★ LNW-2000", "★★★★★ Magic Lightning Rifle",
                "★★★★★ Graviton Cannon", "★★★★★ Geothermal Plasma Rifle", "★★★★★ Forest Hunter Bow",
                "★★★★★ Brilliance Bow", "★★★★★ Charger Bow", "★★★★★ Banshee's Scream",
                "★★★★★ Volcano Bow", "★★★★★ Ancient Elfs bow", "★★★★★ Demon Bow",
                "★★★★★ Flower Bow", "★★★★★ Flame Festival Bow", "★★★★★ Rail Bow",
                "★★★★★ Wolfs Howl Bow", "★★★★★ Yellow Dragon's Bow", "★★★★★ Shape of Flame Bow",
                "★★★★★ Cold Heart", "★★★★★ Sun Garden Bow", "★★★★★ Guardian's Bow",
                "★★★★★ Wing of Terror", "★★★★★ Frost Drop Bow", "★★★★★ Santa's Gift Basket",
                "★★★★★ Fire Hatchling Basket", "★★★★★ Nest of White Dragon", "★★★★★ Cat Basket",
                "★★★★★ Ice Crystal Basket", "★★★★★ Beat Basket", "★★★★★ Horror Basket",
                "★★★★★ Halloween Basket", "★★★★★ Shark Basket", "★★★★★ Fireworks Basket",
                "★★★★★ Steel Bag", "★★★★★ Fairy Shelter Basket", "★★★★★ Shining Jewel Basket",
                "★★★★★ Vine Basket", "★★★★★ Trophy Basket", "★★★★★ Ocean Basket",
                "★★★★★ Random Basket", "★★★★★ Lotus Basket", "★★★★★ Frost Comet Staff",
                "★★★★★ Guide's Frigid Staff", "★★★★★ Ice Moon Staff", "★★★★★ Evil Spirit's Call Staff",
                "★★★★★ Dark Dragon Staff", "★★★★★ Grip of Darkness Staff", "★★★★★ Frost Eye Staff",
                "★★★★★ Harvest Staff", "★★★★★ Jewel of Verdure Staff", "★★★★★ Flame Wing Staff",
                "★★★★★ Fire Shape Staff", "★★★★★ Sunshine Staff", "★★★★★ Arcane Staff",
                "★★★★★ Tear of Light Staff", "★★★★★ Wing of Hope Staff", "★★★★★ Authority of Light Staff",
                "★★★★★ Black Spider Staff", "★★★★★ Staff of Elegance", "★★★★★ Magic Girl Staff",
                "★★★★★ Gargoyle Staff", "★★★★★ Program Staff", "★★★★★ Black Leather Gauntlet",
                "★★★★★ Neko Punch Gauntlet", "★★★★★ Volcano Punch", "★★★★★ Galaxy Gauntlet",
                "★★★★★ Gigantic Fist", "★★★★★ Gauntlet of Brilliance", "★★★★★ Gauntlet of Belief",
                "★★★★★ Marauder Gauntlet", "★★★★★ Venom Gauntlet", "★★★★★ Blizzard Brawl Gauntlet",
                "★★★★★ Flame Dragon Claw Gauntlet", "★★★★★ Blizzard Shard Gauntlet",
                "★★★★★ Assassination Gauntlet", "★★★★★ Magic Gauntlet MS-08",
                "★★★★★ Lucky Punch", "★★★★★ Gauntlet of Fury", "★★★★★ Tiger Hunter Gauntlet",
                "★★★★★ Thorns Gauntlet", "★★★★★ Volcano’s Fury Claw",
                "★★★★★ Demon Claw", "★★★★★ Guardian's Claw", "★★★★★ Black Rose Claw",
                "★★★★★ Dragon Tooth Claw", "★★★★★ Golden Scorpion Claw", "★★★★★ Rune Rock Claw",
                "★★★★★ Cold Thorn", "★★★★★ Oni Claw", "★★★★★ Phoenix Wing Claw",
                "★★★★★ Devil Claw", "★★★★★ Justice Claw", "★★★★★ Blizzard Fang Claw",
                "★★★★★ Destruction Claw", "★★★★★ Black Lion Fang Claw", "★★★★★ Knight Shield",
                "★★★★★ Demon Shield", "★★★★★ Tanker Shield", "★★★★★ Advance Shield",
                "★★★★★ Angel Shield", "★★★★★ Vampire Shield", "★★★★★ Blade Shied",
                "★★★★★ Lion Heart Shield", "★★★★★ Ice Princess’ Shield", "★★★★★ Elphaba's Smile Shield",
                "★★★★★ Charge Shield", "★★★★★ Mirror Shield", "★★★★★ Seth Shield",
                "★★★★★ Punishment Shield", "★★★★★ Wyvern Shield", "★★★★★ Wolf Ring",
                "★★★★★ Blessing Necklace", "★★★★★ Pearl Earring", "★★★★★ Amethyst Earring",
                "★★★★★ Ring of Belief", "★★★★★ Black Crown Ring", "★★★★★ Chaste Love Brooch",
                "★★★★★ Angel Necklace", "★★★★★ Rabbit Foot", "★★★★★ Sharp Shooter",
                "★★★★★ Dark Magic Ring", "★★★★★ Wood Fairy Ring", "★★★★★ Ring of Fortress",
                "★★★★★ Frost Flower Ring", "★★★★★ Sacred Rosary", "★★★★★ Earth Necklace",
                "★★★★★ Ring of Heat", "★★★★★ Ocean Earring", "★★★★★ Crescent Moon Earring",
                "★★★★★ Cursed Necklace", "★★★★★ Earring of Dark Desire", "★★★★★ Wedding Ring of Earth",
                "★★★★★ Goddess Statue", "★★★★★ Gold Pocket Watch", "★★★★★ Greed Earring",
                "★★★★★ Ring of Greed", "★★★★★ Honor Ring", "★★★★★ Ice Queen Ring"
            ],
            [
                "★★★★ [Ex] Libera", "★★★★ [Ex] Silence", "★★★★ [Ex] Veritas",
                "★★★★ [Ex] Murasame", "★★★★ [Ex] Tartaros", "★★★★ [Ex] Trouble Maker",
                "★★★★ [Ex] Merciless", "★★★★ [Ex] Blue Rose", "★★★★ [Ex] Magiton Buster",
                "★★★★ [Ex] Marauder", "★★★★ [Ex] Oberon", "★★★★ [Ex] Curiosity Solver",
                "★★★★ [Ex] Witch Heart", "★★★★ [Ex] Crescent Moon", "★★★★ [Ex] Justice",
                "★★★★ [Ex] Helios", "★★★★ [Ex] Vulkan", "★★★★ [Ex] Pride of Fighter",
                "★★★★ [Ex] Firm Determination",
                "★★★★★ [Ex] Innocent", "★★★★★ [Ex] Armada", "★★★★★ [Ex] Eckesachs",
                "★★★★★ [Ex] Red Lotus", "★★★★★ [Ex] Astarte", "★★★★★ [Ex] Prominence",
                "★★★★★ [Ex] Brave Heart", "★★★★★ [Ex] Predator", "★★★★★ [Ex] Genocide",
                "★★★★★ [Ex] Terminator", "★★★★★ [Ex] Cosmic Destroyer", "★★★★★ [Ex] Samga",
                "★★★★★ [Ex] Thousand Thunder", "★★★★★ [Ex] Magnificat", "★★★★★ [Ex] Mayreel",
                "★★★★★ [Ex] Sage Bead", "★★★★★ [Ex] Shangri La", "★★★★★ [Ex] Angel Voice",
                "★★★★★ [Ex] Amarok", "★★★★★ [Ex] Liberator", "★★★★★ [Ex] Messiah",
                "★★★★★ [Ex] Pure Mind", "★★★★★ [Ex] Uros", "★★★★★ [Ex] Volcanic Horn"
            ]
        ]
        self.equipments_banner = [
                "★★★★★ [Ex] Messiah",
                "★★★★★ [Ex] Thousand Thunder",
                "★★★★★ [Ex] Astarte",
                "★★★★★ [Ex] Armada"
            ]
        self.equipments_with_banner = []
        self.weights = [58.000, 27.000, 9.000, 3.000, 3.000]
        self.weights_banner = [58.000, 27.000, 9.000, 3.000, 1.000, 2.000]
        self.weights_last = [94, 3, 3]

    # Calculate the chances for those exclusive weapons
    async def calcResults(self, ctx, one_or_ten, e, w, ex=None):
        if one_or_ten == "10" or one_or_ten == "ten":
            results = random.choices(e, w, k=9)
        elif one_or_ten == "1" or one_or_ten == "one":
            results = random.choices(e, w, k=1)
        else:
            results = [
                f"Hey, <@{ctx.author.id}>. I don't think thats a valid summon value. LOL!",
                f"Ermm.. its either 10 or 1! Get yourself corrected, <@{ctx.author.id}>!",
                f"You sure there's a {one_or_ten} summon, <@{ctx.author.id}>? There's only 1 and 10 summon!"
            ]

            await ctx.send(random.choice(results))

        if one_or_ten == "10" or one_or_ten == "ten" or one_or_ten == "1" or one_or_ten == "one":
            ex_weap = False
            obtainedPickup = False

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
                        if not "★★★★★ " in r and not check:
                            pity = True
                        if not "★★★★ " in r and not check:
                            pity = True
                        else:
                            pity = False
                            check = True

                    if "★★★★★ [Ex]" in r:
                        ex_weap = True
                    if r == ex:
                        obtainedPickup = True

                    await msg.edit(content=msg.content + f"\n{i}. {r}")
                    await asyncio.sleep(1.5)
                    i += 1

            if pity:
                equips_pity = self.equipments[:]
                equips_pity.pop(0)
                results = random.choices(equips_pity, self.weights_last, k=1)
                for pity_result in results:
                    p_r = random.choices(pity_result, k=1)
                    for pr in p_r:
                        if "★★★★★ [Ex]" in pr:
                            ex_weap = True
                        if pr == ex:
                            obtainedPickup = True

                        await msg.edit(content=msg.content + f"\n10. {pr}")
                        await asyncio.sleep(1.5)

            if not pity:
                results = random.choices(e, w, k=1)
                for not_pity_result in results:
                    n_p_r = random.choices(not_pity_result, k=1)
                    for npr in n_p_r:
                        if "★★★★★ [Ex]" in npr:
                            ex_weap = True
                        if npr == ex:
                            obtainedPickup = True

                        await msg.edit(content=msg.content + f"\n10. {npr}")
                        await asyncio.sleep(1.5)

            if ex_weap and not obtainedPickup and ex:
                await ctx.send(f"I see 5 star exclusive weapon. But no {ex}.. Sad life, <@{ctx.author.id}>.")
            if ex_weap and obtainedPickup and ex:
                await ctx.send(f"WOHOOOOOOOOOOOOOOOOOO, <@{ctx.author.id}>! You got the pick up equipment!")
            if ex_weap and not ex:
                await ctx.send(
                    f"WOW! W-w-waaaiittt a second, <@{ctx.author.id}>..  Is that a freaking exclusive weapon?!"
                )

            if not ex_weap:
                await ctx.send(
                    f"You just suck at gachas, <@{ctx.author.id}>..")

    # Lists the current pickup banner
    @commands.command(name="equipment.pickup.info", help="Lists the current pickup banner.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def equipmentPickUpInfo(self, ctx):
        msg = await ctx.send(f"One sec, <@{ctx.author.id}>. Getting those Pick Up Banner info.")
        await asyncio.sleep(1.5)

        i = 1
        for hero_banner in self.equipments_banner:
            await msg.edit(content=msg.content + f"\n{i}. {hero_banner}")
            i += 1

    # Summons on the normal banner
    @commands.command(name="summon.equipment", help="Summons single or ten equipments on the normal banner.")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def summonEquipment(self, ctx, one_or_ten):
        await self.calcResults(ctx, one_or_ten, self.equipments, self.weights)

    # Summons on the pick up banner
    @commands.command(name="summon.equipment.pickup", help="Summons single or ten equipments on the normal banner.")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def summonEquipmentPickUp(self, ctx, ex, one_or_ten):
        self.equipments_with_banner = self.equipments[:]
        present = False
        equipment_banner = ""

        if len(ex) < 5:
            await ctx.send(f"Yo, <@{ctx.author.id}>. At least put 4 characters please?")
            return

        for equipment_banner in self.equipments_banner:
            if equipment_banner.lower().__contains__(ex.lower()):
                present = True
                break

        if present:
            for equips_list in self.equipments:
                if equipment_banner in equips_list:
                    for equip_list in equips_list:
                        if equipment_banner == equip_list:
                            buffer = self.equipments[4][:]
                            buffer.remove(equipment_banner)
                            self.equipments_with_banner.pop(4)
                            self.equipments_with_banner.append(buffer)
                            self.equipments_with_banner.append([equipment_banner, ])

                            await self.calcResults(ctx, one_or_ten, self.equipments_with_banner, self.weights_banner, self.equipments_with_banner[5][0])
                            break
                    break

        if not present:
            await ctx.send(f"Ermmm, <@{ctx.author.id}>. The hero you mentioned is not in the current pick up banner.")


def setup(bot):
    bot.add_cog(Equipment(bot))
