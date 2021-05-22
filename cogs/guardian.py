#!/usr/bin/env python

import discord
from discord.ext import commands
from helpers.database import Database


class Guardian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def statsLevel(self, stats, hero_level, user_level):
        # Increase overall stats
        for stat in stats:
            if stat in ["attack"]:
                increase = 10
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
                increase = 2
                stats[stat] = round(
                    stats[stat]
                    + ((increase/100) * stats[stat] * hero_level)
                    + ((increase/100) * stats[stat] * user_level)
                )
            else:
                pass

        return stats

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

    @commands.command(
        name="profile",
        brief="View profile.",
        description="View profile of yourself or someone else's.",
        aliases=["pr", "prof"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, mention: discord.Member = None):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
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

        # Get all information needed for a profile show off
        username, guild_name, position, gems = db_ailie.get_guardian_info(
            guardian_id
        )
        trophies = db_ailie.get_trophy(guardian_id)
        guild_id = db_ailie.get_guild_id_of_member(guardian_id)
        heroes_obtained = db_ailie.hero_inventory(guardian_id)
        equips_obtained = db_ailie.equip_inventory(guardian_id)
        user_exp = db_ailie.get_user_exp(guardian_id)
        user_level = db_ailie.get_user_level(guardian_id)
        summon_count = db_ailie.get_summon_count(guardian_id)

        # Set embed baseline
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(
            name=f"Lvl {user_level}/500 {guardian_name}'s Profile",
            icon_url=guardian_avatar
        )

        # Username, gems, and trophies
        embed.add_field(name="Username 📝", value=f"`{username}`", inline=False)
        embed.add_field(
            name="User EXP 💪", value=f"`{user_exp:,d}`", inline=False)
        embed.add_field(name="Gems 💎", value=f"`{gems:,d}`")
        embed.add_field(name="Trophies 🏆", value=f"`{trophies:,d}`")

        # Total unique and epic exclusive
        heroes_equips_count = (
            "**Summon Count**: "
            + f"`{summon_count:,d}`"
            + "\n**Unique Heroes**: "
            + f"`{len(heroes_obtained[len(heroes_obtained) - 1])}`"
            + "\n**Epic Exclusive Equipments**: "
            + f"`{len(equips_obtained[len(equips_obtained) - 1])}`"
        )
        embed.add_field(
            name="Summons⚔️",
            value=heroes_equips_count,
            inline=False
        )

        # Guild details
        guild_detail = (
            f"**Guild Name**: `{guild_name}`"
            + f"\n**Guild ID**: `{guild_id}`"
            + f"\n**Position**: `{position}`"
        )
        embed.add_field(
            name="Guild Details 🏠",
            value=guild_detail,
            inline=False,
        )

        db_ailie.disconnect()

        await ctx.send(embed=embed)

    @commands.command(
        name="inventory",
        brief="View inventory.",
        description=(
            "Open inventory to check what you have collected so far."
            + "`type` can be either `hero`, `equip`, or `item`. "
            + "`target` is optional as it can be used to view "
            + "your specific hero statistics."
        ),
        aliases=["inv"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def inventory(
            self, ctx, type, *target):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        guardian_id = ctx.author.id
        guardian_name = ctx.author.name
        guardian_avatar = ctx.author.avatar_url
        inventory = []
        header = ""
        exists = False
        in_bag = False
        ind = ""
        full_name = ""
        acquired = {}
        stats = buffs = skill = on_hit = on_normal \
            = on_normal_instant = on_hit_instant = {}

        if target:
            target = " ".join(target)
            if len(target) < 4:
                await ctx.send(
                    f"Yo, <@{ctx.author.id}>. "
                    + "At least put 4 characters please?"
                )
                db_ailie.disconnect()
                return

        # Determine inventory to check
        if type.lower() in ["heroes", "hero", "h"] and not target:
            inventory = db_ailie.hero_inventory(guardian_id)
            if len(inventory[len(inventory) - 1]) > 1:
                header = "Unique Heroes"
            else:
                header = "Unique Hero"
        elif (
            type.lower()
            in [
                "equipments",
                "equipment",
                "equips",
                "equip",
                "e",
            ]
            and not target
        ):
            inventory = db_ailie.equip_inventory(guardian_id)
            if len(inventory[len(inventory) - 1]) > 1:
                header = "Epic Exclusive Equipments"
            else:
                header = "Epic Exclusive Equipment"
        elif type.lower() in ["items", "item", "i"] and not target:
            inventory = db_ailie.item_inventory(guardian_id)
            if len(inventory[len(inventory) - 1]) > 1:
                header = "Items"
            else:
                header = "Item"
        elif type in ["heroes", "hero", "h"] and target:
            type = "Hero"
            exists = True
            full_name = db_ailie.get_hero_full_name(target)

            if not full_name:
                exists = False
            else:
                hero_id = db_ailie.get_hero_id(full_name)
                (
                    stats,
                    buffs,
                    skill,
                    triggers,
                ) = db_ailie.get_hero_stats(hero_id)

                for trigger in triggers:
                    if trigger == "on_hit":
                        on_hit = triggers[trigger]
                    else:
                        on_normal = triggers[trigger]

                inventory_id = db_ailie.get_inventory_id(guardian_id)
                if db_ailie.is_hero_obtained(guardian_id, hero_id):
                    user_level = db_ailie.get_user_level(guardian_id)
                    acquired = db_ailie.get_hero_acquired_details(
                        inventory_id, hero_id
                    )
                    stats = self.statsLevel(
                        stats, acquired["level"], user_level
                    )
                    ewp_id = db_ailie.get_exclusive_weapon_id(hero_id)
                    hero_ewp_set = db_ailie.is_equip_obtained(
                        ctx.author.id, ewp_id)
                    if hero_ewp_set:
                        ind = " 🗡️"
                    else:
                        ind = ""

                    in_bag = True
                else:
                    in_bag = False
        elif type in ["equipments", "equips", "equip", "eq", "e"] and target:
            type = "Equip"
            exists = True
            full_name = db_ailie.get_equip_full_name(target)

            if not full_name:
                exists = False
            else:
                equip_id = db_ailie.get_equip_id(full_name)
                (
                    stats,
                    buffs,
                    skill,
                    triggers,
                    instant_triggers
                ) = db_ailie.get_equip_stats(equip_id)

                for trigger in triggers:
                    if trigger == "on_hit":
                        on_hit = triggers[trigger]
                    else:
                        on_normal = triggers[trigger]

                for instant_trigger in instant_triggers:
                    if instant_trigger == "on_hit":
                        on_hit_instant = instant_triggers[instant_trigger]
                    else:
                        on_normal_instant = instant_triggers[instant_trigger]

                inventory_id = db_ailie.get_inventory_id(guardian_id)
                if db_ailie.is_equip_obtained(guardian_id, equip_id):
                    acquired = db_ailie.get_equip_acquired_details(
                        inventory_id, equip_id
                    )
                    stats = self.statsLevel(
                        stats, acquired["level"], 0
                    )
                    hero_id = db_ailie.get_hero_id_for_exclusive_weapon(
                        equip_id)
                    hero_ewp_set = db_ailie.is_hero_obtained(
                        ctx.author.id, hero_id)
                    if hero_ewp_set:
                        ind = " 👊"
                    else:
                        ind = ""

                    in_bag = True
                else:
                    in_bag = False
        elif type in ["items", "item", "i"] and target:
            await ctx.send(
                "Please use `a;shop` to check the items in detail.")
            db_ailie.disconnect()
            return
        else:
            await ctx.send(
                "There's only inventories for heroes, equipments, and items "
                + f"<@{ctx.author.id}>."
            )
            db_ailie.disconnect()
            return

        if not target:
            buffer_main = []
            emoji_right = "➡️"
            emoji_left = "⬅️"
            emoji_stop = "🛑"
            counter = 0

            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                name=guardian_name + "'s Inventory",
                icon_url=guardian_avatar,
            )
            if len(inventory[len(inventory) - 1]) == 0:
                buffer_main.append(["None"])
            else:
                buffer_second = []
                total = len(inventory[len(inventory) - 1])
                count = 1
                for inv in inventory[len(inventory) - 1]:
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

            embed.add_field(
                name=header,
                value=data,
                inline=False,
            )
            embed_sent = await ctx.send(embed=embed)
            await embed_sent.add_reaction(emoji_left)
            await embed_sent.add_reaction(emoji_right)
            await embed_sent.add_reaction(emoji_stop)

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

                        embed = discord.Embed(color=discord.Color.purple())
                        embed.set_author(
                            name=guardian_name + "'s Inventory",
                            icon_url=guardian_avatar,
                        )

                        data = "\n".join(buffer_main[counter])

                        embed.add_field(
                            name=header,
                            value=data,
                            inline=False,
                        )

                        await embed_sent.remove_reaction(str(emoji_right), user)
                        await embed_sent.edit(embed=embed)

                    if reaction.emoji == str(emoji_left):
                        if counter != 0:
                            counter -= 1

                        embed = discord.Embed(color=discord.Color.purple())
                        embed.set_author(
                            name=guardian_name + "'s Inventory",
                            icon_url=guardian_avatar,
                        )

                        data = "\n".join(buffer_main[counter])

                        embed.add_field(
                            name=header,
                            value=data,
                            inline=False,
                        )

                        await embed_sent.remove_reaction(str(emoji_left), user)
                        await embed_sent.edit(embed=embed)

                    if reaction.emoji == str(emoji_stop):
                        await embed_sent.remove_reaction(str(emoji_stop), user)
                        break
                except discord.Forbidden:
                    await ctx.send(
                        "Please check that I have the permission, "
                        + "`View Channels`, `Send Messages`, `Embed Links` "
                        + "`Add Reactions`, `Read Message History`, "
                        + "and Manage Messages."
                        )
                    break
                except Exception:
                    break

        elif target and in_bag:
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                icon_url=self.bot.user.avatar_url,
                name=(
                    f"Lvl {acquired['level']}/{acquired['max_level']} "
                    + f"{full_name}{ind}"),
            )
            embed.add_field(
                name=f"{type} EXP 💪",
                value=f"`{acquired['exp']:,d}`",
                inline=False
            )
            embed.add_field(
                name="Limit Break 🛩️",
                value=f"`{acquired['limit_break']:,d}`/`9`",
                inline=False
            )

            # Set output
            for info in [
                stats,
                buffs,
                skill,
                on_hit,
                on_normal,
                on_hit_instant,
                on_normal_instant
            ]:
                information = ""
                info_title = ""
                for i in info:
                    all = False
                    party = ""

                    if info == stats:
                        info_title = "Stats 📋"
                    elif info == buffs:
                        info_title = "Buffs ✨"
                    elif info == skill:
                        if type == "Hero":
                            info_title = "Chain Skill 🔗"
                        else:
                            info_title = "Weapon Skill 🔥"
                    elif info == on_hit:
                        info_title = "On Hit 🛡️"
                    elif info == on_normal:
                        info_title = "On Attack ⚔️"
                    elif info == on_hit_instant:
                        info_title = "On Hit Instant 🛡️⚡"
                    else:
                        info_title = "On Attack Instant ⚔️⚡"

                    if i.startswith("all"):
                        buffer = i[4:]
                        all = True
                    else:
                        buffer = i

                    info_proper = self.translateToReadableFormat(buffer)

                    if all:
                        party = " (Party)"

                    if information == "":
                        information = f"\n**{info_proper}**: `{info[i]}`{party}"
                    else:
                        information = (
                            information
                            + f"\n**{info_proper}**: `{info[i]}`{party}"
                        )

                if information:
                    embed.add_field(
                        name=info_title, value=information, inline=False
                    )

            await ctx.send(embed=embed)
        elif not exists:
            await ctx.send("The target you stated doesn't exist.")
        else:
            await ctx.send("You don't own the target you stated.")

        db_ailie.disconnect()

    @commands.command(
        name="book",
        brief="Open book of everything.",
        description=(
            "Use the book to check information of heroes and equipments. "
            + "`type` can be either `hero` or `equip`. "
            + "Target can be any heroes or equipments."
        ),
        aliases=["bo"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def book(self, ctx, type, *target):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if target:
            target = " ".join(target)

            if len(target) < 4:
                await ctx.send(
                    f"Yo, <@{ctx.author.id}>. "
                    + "At least put 4 characters please?"
                )
                db_ailie.disconnect()
                return

            exists = False
            full_name = ""
            stats = (
                buffs
            ) = (
                skill
            ) = on_hit = on_normal = on_normal_instant = on_hit_instant = {}
        else:
            await ctx.send("No hero or equipment mentioned.")
            db_ailie.disconnect()
            return

        if type in ["heroes", "hero", "h"]:
            exists = True
            full_name = db_ailie.get_hero_full_name(target)

            if not full_name:
                exists = False
            else:
                hero_id = db_ailie.get_hero_id(full_name)
                (
                    stats,
                    buffs,
                    skill,
                    triggers,
                ) = db_ailie.get_hero_stats(hero_id)

                for trigger in triggers:
                    if trigger == "on_hit":
                        on_hit = triggers[trigger]
                    else:
                        on_normal = triggers[trigger]
        elif type in ["equipments", "equips", "equip", "eq", "e"]:
            exists = True
            full_name = db_ailie.get_equip_full_name(target)

            if not full_name:
                exists = False
            else:
                equip_id = db_ailie.get_equip_id(full_name)
                (
                    stats,
                    buffs,
                    skill,
                    triggers,
                    instant_triggers,
                ) = db_ailie.get_equip_stats(equip_id)

                for trigger in triggers:
                    if trigger == "on_hit":
                        on_hit = triggers[trigger]
                    else:
                        on_normal = triggers[trigger]

                for instant_trigger in instant_triggers:
                    if instant_trigger == "on_hit":
                        on_hit_instant = instant_triggers[instant_trigger]
                    else:
                        on_normal_instant = instant_triggers[instant_trigger]
        else:
            await ctx.send("Please specify the type as hero or equipment.")
            return

        if exists:
            embed = discord.Embed(color=discord.Color.purple())
            embed.set_author(
                icon_url=self.bot.user.avatar_url, name=f"Lvl 1 {full_name}"
            )

            # Set output
            for info in [
                stats,
                buffs,
                skill,
                on_hit,
                on_normal,
                on_hit_instant,
                on_normal_instant,
            ]:
                information = ""
                info_title = ""
                for i in info:
                    all = False
                    party = ""

                    if info == stats:
                        info_title = "Stats 📋"
                    elif info == buffs:
                        info_title = "Buffs ✨"
                    elif info == skill:
                        info_title = "Chain Skill 🔗"
                    elif info == on_hit:
                        info_title = "On Hit 🛡️"
                    elif info == on_normal:
                        info_title = "On Attack ⚔️"
                    elif info == on_hit_instant:
                        info_title = "On Hit Instant 🛡️⚡"
                    else:
                        info_title = "On Attack Instant ⚔️⚡"

                    if i.startswith("all"):
                        buffer = i[4:]
                        all = True
                    else:
                        buffer = i

                    info_proper = self.translateToReadableFormat(buffer)

                    if all:
                        party = " (Party)"

                    if information == "":
                        information = f"\n**{info_proper}**: `{info[i]}`{party}"
                    else:
                        information = (
                            information
                            + f"\n**{info_proper}**: `{info[i]}`{party}"
                        )

                if information:
                    embed.add_field(
                        name=info_title, value=information, inline=False
                    )

            await ctx.send(embed=embed)
        else:
            await ctx.send("The target you asked for does not exist.")

    @commands.command(
        name="username",
        brief="Set username.",
        description=(
            "Set username that you use in-game or not. "
            + "This is optional. If you set it, you'll see the "
            + "username you set in some commands."
        ),
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def username(self, ctx, username):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        db_ailie.set_username(ctx.author.id, username)
        await ctx.send(
            f"Your username is now, {username}. Enjoy, <@{ctx.author.id}>."
        )

        db_ailie.disconnect()

    @commands.command(
        name="initialize",
        brief="Initialize user.",
        description=(
            "This command needs to be issued before most of the other commands "
            + "can be used. Think of it as a registration process."
        ),
        aliases=["ini"],
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def initialize(self, ctx):
        db_ailie = Database()

        if db_ailie.initialize_user(ctx.author.id):
            await ctx.send(
                "You can now use the other commands, "
                + f"<@{ctx.author.id}>. Have fun!"
            )
        else:
            await ctx.send(
                f"You are already initialized, <@{ctx.author.id}>. "
                + "No need to initialize for the second time. Have fun!"
            )

    @commands.group(
        name="team",
        brief="Manage team here.",
        description="Set, delete, and view your teams.",
        invoke_without_command=True
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return
        db_ailie.disconnect()

        able_send = True
        if isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.send("Time to explain..")
        else:
            try:
                await ctx.send(
                    "Sent you a Private Message to get started with "
                    + f"team, <@{ctx.author.id}>."
                )
            except Exception:
                await ctx.send(
                    "Can't send a Private Message to your for "
                    + "`team` management. Do you have it diabled?"
                )
                able_send = False

        if able_send:
            await ctx.author.send(
                f"Hello, <@{ctx.author.id}>! "
                + "Make a team with `a;team set <key> <hero>` and "
                + "show your current team with `a;team show`. "
                + "Your max team slots for now is 3. Remember. "
                + "Making a team with 'main' as the name will allow "
                + "you to use the `a;train` just as is. If your team's "
                + "key is not 'main', then, you'll have to specify your "
                + "team when using `a;train`. For example, if your "
                + "team's key is `main`. Then, the full command for "
                + "`train` is `a;train`. However if your team's key "
                + "is other than main for example, 'one', then your "
                + "full command would be `a;train one`. The same "
                + "concept applies to `arena`. You can also `a;help team`.")

    @team.command(
        name="set",
        brief="Set team.",
        description=(
            "Configure team that you can pre-made before battle or any "
            + "commands that requires a hero to use, such as, `arena`. "
            + "With this, enemy would not be able to know your used hero "
            + "until the match begins. Use `a;team` without any arguments "
            + "first, to bring Ailie into your Private Messages. "
            + "You can set a team with `main` key "
            + "to allow automatic use of that hero for commands like `train`. "
            + "`key` should be any words, letters, or numbers. You will have "
            + "to specify your `key` instead of your hero when in commands, "
            + "like `arena`. Using `main` key will allow you to use the team "
            + "without specifying any `key`. `heroes` is the hero you want "
            + "in you team. For now, only one hero can be in a team."
        ),
    )
    @commands.dm_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team_set(self, ctx, key: str, *heroes):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if not key:
            await ctx.send(
                "You forgot to specify the key. Put `main` as the key "
                + "if you want to be able to use commands like `arena` "
                + "without having to specify `key`."
            )
            db_ailie.disconnect()
            return

        if not heroes:
            await ctx.send(
                "Specify the heroes you want in the team. "
                + "One team consists of one to four heroes. "
                + "Make sure to separate the heroes with `;` "
                + "For example, "
                + "`Alef;Idol Captain Eva;Gabriel;Princess`."
            )
            db_ailie.disconnect()
            return

        exist = db_ailie.is_team_exists(ctx.author.id, key)
        team_count = db_ailie.get_team_count(ctx.author.id)

        if not exist:
            if team_count >= 3:
                await ctx.send(
                    "The max amount of team you can make is 3."
                )
                db_ailie.disconnect()
                return

        heroes = " ".join(heroes)
        heroes = heroes.split(";")
        counter_buffer = []

        # Remove whitespaces
        for hero in heroes:
            if hero == "":
                counter_buffer.append(heroes.index(hero))

        for counter in counter_buffer:
            heroes.pop(counter)

        if len(heroes) > 1:
            await ctx.send(
                "The max amount of heroes in a team now is 1. "
                + "Yeah I know, weird. How can it be a team with "
                + "only 1 hero. You're gonna need to wait "
                + "for an update for that."
            )
            db_ailie.disconnect()
            return

        buffer = []
        for hero in heroes:
            full_name = db_ailie.get_hero_full_name(hero)
            if not full_name:
                await ctx.send("The hero you stated doesn't exist.")
                db_ailie.disconnect()
                return
            else:
                hero_id = db_ailie.get_hero_id(full_name)
                obtained = db_ailie.is_hero_obtained(ctx.author.id, hero_id)
                if not obtained:
                    await ctx.send(f"You don't own **{full_name}**.")
                    db_ailie.disconnect()
                    return
                buffer.append(hero_id)

        # Check duplicate heroes
        if len(set(buffer)) != len(buffer):
            await ctx.send(
                "Two of the same hero in a team? That's absurd!")
            db_ailie.disconnect()
            return

        # Fill the extra spaces with zeros
        if len(buffer) != 4:
            while len(buffer) != 4:
                buffer.append(0)

        db_ailie.set_team(ctx.author.id, key, buffer)
        await ctx.send("Updated your team!")

    @team.command(
        name="show",
        brief="Show team.",
        description=(
            "View all the teams you made."
        ),
    )
    @commands.dm_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team_show(self, ctx):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        teams = db_ailie.get_all_teams(ctx.author.id)

        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(
            icon_url=ctx.author.avatar_url, name=ctx.author.name
        )

        output = ""
        for team in teams:
            for t in team[1]:
                hero_name = db_ailie.get_hero_name_from_id(t)
                if hero_name is not None:
                    if team[1].index(t) == 0:
                        output = f"`{hero_name}`"
                    else:
                        output = output + "\n" + f"`{hero_name}`"

            embed.add_field(name=team[0], value=output, inline=False)

        if len(teams) == 0:
            embed.add_field(name="Teams", value="None", inline=False)

        await ctx.send(embed=embed)

    @team.command(
        name="delete",
        brief="Delete team.",
        description=(
            "Delete the teams you made."
        ),
    )
    @commands.dm_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team_delete(self, ctx, key: str):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        exist = db_ailie.is_team_exists(ctx.author.id, key)

        if not exist:
            await ctx.send(
                "Are you sure they key is correct?"
            )
            db_ailie.disconnect()
            return

        db_ailie.delete_team(ctx.author.id, key)
        await ctx.send(f"Deleted your team with `{key}` key.")


def setup(bot):
    bot.add_cog(Guardian(bot))
