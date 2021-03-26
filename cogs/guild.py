#!/usr/bin/env python

import random
from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create guild
    @commands.command(name="create", help="Create guild.")
    async def create(self, ctx, guild_name):
        db_ailie = DatabaseAilie(ctx.author.id)
        guild_check = True
        guild_id = 0

        # Create a random Guild ID until there is no duplicate
        while guild_check:
            guild_id = random.randint(pow(10, 14), (pow(10, 15) - 1))
            guild_check = db_ailie.guild_exists(guild_id)

        # Guild creation if and only if the user is guildless
        if db_ailie.is_guildless(ctx.author.id):
            db_ailie.create_guild(
                ctx.author.id, "Guild Master", guild_id, guild_name
            )
            await ctx.send(
                f"Congratulations, <@{ctx.author.id}>! You have created "
                + f"a Guild named, `{guild_name}` with the ID, `{guild_id}`."
            )
        else:
            await ctx.send(
                "I don't think you should be creating a guild when you "
                + f"already have one. No, <@{ctx.author.id}>?"
            )

        db_ailie.disconnect()

    @commands.command(name="join", help="Join guild.")
    async def join(self, ctx, guild_id):
        # Initialize database
        db_ailie = DatabaseAilie(ctx.author.id)

        # Get Guild Master
        guild_master = db_ailie.get_guild_master(guild_id)

        if db_ailie.is_guildless(ctx.author.id):
            if db_ailie.guild_exists(guild_id):
                # Check if Guild Master is in the Discord Server
                discord_server = self.bot.get_guild(ctx.message.guild.id)
                if not discord_server.get_member(guild_master):
                    await ctx.send(
                        "You must be in the same Discord Server "
                        + "as the Guild Master."
                    )
                    return

                # Get Guild details
                guild_id, guild_name = db_ailie.get_guild_id_name(guild_id)

                # Get Guild Master's confirmation
                await ctx.send(
                    f"<@{guild_master}>, please choose to accept or decline "
                    + f"<@{ctx.author.id}> application to "
                    + f"`{guild_name}#{guild_id}` with `Y` or `N`."
                )

                # Function to confirm application
                def confirm_application(message):
                    return (
                        message.author.id == ctx.author.id
                        and message.content.upper() in ["YES", "Y", "NO", "N"]
                    )

                # Wait for Guild Master's confirmation
                msg = await self.bot.wait_for(
                    "message", check=confirm_application, timeout=30
                )

                # Application accepted
                if msg.content.upper() in ["YES", "Y"]:
                    db_ailie.join_guild(ctx.author.id, "Member", guild_id)
                    await ctx.send(
                        f"Welcome to `{guild_name}#{guild_id}`, "
                        + f"<@{ctx.author.id}>!"
                    )
                # Application rejected
                else:
                    await ctx.send(
                        f"Application denied! Sorry, <@{ctx.author.id}>.."
                    )
            else:
                await ctx.send("The guild you mentioned does not exist.")
        else:
            if db_ailie.guild_exists(guild_id):
                guild_id, guild_name = db_ailie.get_guild_id_name(guild_id)
                await ctx.send(
                    "Aren't you a very loyal person? You are already "
                    + f"in `{guild_name}#{guild_id}`! No, <@{ctx.author.id}>?"
                )
            else:
                await ctx.send("The guild you mentioned does not exist.")

        db_ailie.disconnect()


def setup(bot):
    bot.add_cog(Guild(bot))
