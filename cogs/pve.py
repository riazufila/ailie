#!/usr/bin/env python

import random
from discord.ext import commands
from helpers.database import Database


class PvE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="train",
        brief="Train heroes for EXP.",
        description="This command allows heroes to gain EXP.",
        aliases=["exercise"],
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
            await ctx.send("No such heroes exists.")
            db_ailie.disconnect()
            return

        hero_id = db_ailie.get_hero_id(hero_full_name)

        if not db_ailie.is_hero_obtained(ctx.author.id, hero_id):
            await ctx.send(f"You dont have that hero, <@{ctx.author.id}>!")
            db_ailie.disconnect()
            return

        training_type = [
            "punch",
            "evasion",
            "block",
            "focus",
            "skill",
            "run",
            "kite",
        ]

        training_type_picked = random.choices(training_type, k=2)
        output = ""
        for training in training_type_picked:
            if output == "":
                output = f"`{training}`"
            else:
                output = f"{output} or `{training}`"

        await ctx.send(
            "Now choose which training would you want "
            + f"for **{hero_full_name}**. {output}?"
        )

        # Function to confirm training
        def confirm_training(message):
            return message.author.id == ctx.author.id

        # Wait for training decision
        try:
            msg = await self.bot.wait_for(
                "message", check=confirm_training, timeout=30
            )
            if msg.content.lower() in training_type_picked:
                reply = [
                    f"Now **{hero_full_name}** should have "
                    + f"better `{msg.content.lower()}`.",
                    f"**{hero_full_name}**'s `{msg.content.lower()}` "
                    + "intensifies!",
                    f"You think you've got the best **{hero_full_name}**? "
                    + f"However polished your **{hero_full_name}**'s "
                    + f"`{msg.content.lower()}` is, it won't surpass mine.",
                    "Lol, goodluck with your training. "
                    + f"`{msg.content.lower()}` increased.",
                    f"I can feel your **{hero_full_name}** getting stronger!",
                    "Now that is a good way to train your hero!",
                ]
                reply = random.choice(reply)

                db_ailie.update_hero_exp(ctx.author.id, hero_full_name, 5)

                await ctx.send(reply)
            else:
                await ctx.send("Better enter your decision properly next time!")
        except Exception:
            await ctx.send(
                "You're taking too long to decide, "
                + f"<@{ctx.author.id}>. Ain't waiting for you!"
            )


def setup(bot):
    bot.add_cog(PvE(bot))
