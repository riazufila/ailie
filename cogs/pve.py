#!/usr/bin/env python

import random
from discord.ext import commands
from helpers.database import Database


class PvE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="train",
        brief="Train heroes.",
        description="Train heroes to gain EXP.",
        aliases=["tra"],
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def train(self, ctx, *hero):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if not hero:
            await ctx.send("You need to specify a hero to train.")
            db_ailie.disconnect()
            return

        hero = " ".join(hero)

        if len(hero) < 4:
            await ctx.send(
                f"Yo, <@{ctx.author.id}>. "
                + "At least put 4 characters please?"
            )
            db_ailie.disconnect()
            return

        hero_full_name = db_ailie.get_hero_full_name(hero)

        if not hero_full_name:
            await ctx.send("No such hero exists.")
            db_ailie.disconnect()
            return

        hero_id = db_ailie.get_hero_id(hero_full_name)

        if not db_ailie.is_hero_obtained(ctx.author.id, hero_id):
            await ctx.send(f"You dont have that hero, <@{ctx.author.id}>!")
            db_ailie.disconnect()
            return

        training_typing = [
            "Must protect Little Princess!",
            "I hope Future Princess gets nerfed..",
            "I love it when my Weapon Skill misses.",
            "Push up, push down, push up, push down.",
            "I just want to get this over with.",
            "What should I ask you guys to type?",
        ]

        # Randomly pick from list
        training_typing_picked = random.choice(training_typing)

        await ctx.send(
            f"Type `{training_typing_picked}` to train **{hero_full_name}**. "
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

            exp = random.randint(1, 10)

            if msg.content == training_typing_picked:
                reply = [
                    f"<@{ctx.author.id}>, you can feel `{exp:,d}` Hero EXP "
                    + f"coursing through **{hero_full_name}**.",
                    f"You think you've got the best **{hero_full_name}**? "
                    + f"However strong your **{hero_full_name}** "
                    + f"is, <@{ctx.author.id}>, it still won't surpass me. "
                    + f"You've got `{exp:,d}` Hero EXP though.",
                    f"<@{ctx.author.id}>, you can feel **{hero_full_name}** "
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

    @commands.command(
        name="enhance",
        brief="Enhance equipments.",
        description="Enhance equipments for EXP.",
        aliases=["en"],
    )
    async def enhance(self, ctx, *equipment):
        # Check if user is initialized first
        db_ailie = Database()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
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

        if not db_ailie.is_hero_obtained(ctx.author.id, equip_id):
            await ctx.send(f"You dont have that hero, <@{ctx.author.id}>!")
            db_ailie.disconnect()
            return


def setup(bot):
    bot.add_cog(PvE(bot))
