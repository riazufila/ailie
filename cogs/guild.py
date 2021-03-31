#!/usr/bin/env python

import random
import discord
from discord.ext import commands
from helpers.db_ailie import DatabaseAilie


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create guild
    @commands.command(name="create", help="Create guild.")
    async def create(self, ctx, guild_name):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Create a random Guild ID until there is no duplicate
        guild_check = True
        guild_id = 0

        while guild_check:
            guild_id = random.randint(pow(10, 14), (pow(10, 15) - 1))
            guild_check = db_ailie.guild_exists(guild_id)

        # Guild creation if and only if the user is guildless
        if not db_ailie.is_guildless(ctx.author.id):
            await ctx.send(
                "I don't think you should be creating a guild when you "
                + f"already have one. No, <@{ctx.author.id}>?"
            )
            db_ailie.disconnect()
            return

        # Finally, create guild after all checks is done
        db_ailie.create_guild(
            ctx.author.id, "Guild Master", guild_id, guild_name
        )
        await ctx.send(
            f"Congratulations, <@{ctx.author.id}>! You have created "
            + f"a Guild named, `{guild_name}` with the ID, `{guild_id}`."
        )

        db_ailie.disconnect()

    @commands.command(name="join", help="Join guild.")
    async def join(self, ctx, guild_id: int):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Get Guild Master
        guild_master = db_ailie.get_guild_master(guild_id)

        if db_ailie.is_guildless(ctx.author.id):
            if db_ailie.guild_exists(guild_id):
                # Check if guild is full
                if db_ailie.total_members(guild_id) >= 30:
                    await ctx.send(
                        f"The guild is full. Sorry, <@{ctx.author.id}>."
                    )
                    db_ailie.disconnect()
                    return

                # Check if Guild Master is in the Discord Server
                discord_server = self.bot.get_guild(ctx.message.guild.id)
                if not discord_server.get_member(guild_master):
                    await ctx.send(
                        "You must be in the same Discord Server "
                        + "as the Guild Master."
                    )
                    db_ailie.disconnect()
                    return

                # Get Guild details
                guild_name = db_ailie.get_guild_name(guild_id)

                # Get Guild Master's confirmation
                await ctx.send(
                    f"<@{guild_master}>, please choose to accept or decline "
                    + f"<@{ctx.author.id}>'s application to "
                    + f"`{guild_name}`#`{guild_id}` with `Y` or `N`."
                )

                # Function to confirm application
                def confirm_application(message):
                    return (
                        message.author.id == guild_master
                        and message.content.upper() in ["YES", "Y", "NO", "N"]
                    )

                # Wait for Guild Master's confirmation
                try:
                    msg = await self.bot.wait_for(
                        "message", check=confirm_application, timeout=30
                    )

                    # Application accepted
                    if msg.content.upper() in ["YES", "Y"]:
                        db_ailie.join_guild(ctx.author.id, "Member", guild_id)
                        await ctx.send(
                            f"Welcome to `{guild_name}`#`{guild_id}`, "
                            + f"<@{ctx.author.id}>!"
                        )
                    else:
                        # Application rejected else:
                        await ctx.send(
                            f"Application denied! Sorry, <@{ctx.author.id}>.."
                        )
                except Exception:
                    await ctx.send(
                        "Looks like your application got ignored, "
                        + f"<@{ctx.author.id}>. Ouch!"
                    )
            else:
                await ctx.send("The guild you mentioned does not exist.")
        else:
            guild_name = db_ailie.get_guild_name(guild_id)
            await ctx.send(
                "Aren't you a very loyal person? You are already "
                + f"in `{guild_name}`#`{guild_id}`! No, <@{ctx.author.id}>?"
            )

        db_ailie.disconnect()

    @commands.command(name="quit", help="Quit current Guild.")
    async def quit(self, ctx):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Condition checks
        if not db_ailie.is_guildless(ctx.author.id):
            guild_id = db_ailie.get_guild_id_of_member(ctx.author.id)
            guild_master = db_ailie.get_guild_master(guild_id)
            total_members = db_ailie.total_members(guild_id)
            if total_members != 1:
                if ctx.author.id == guild_master:
                    await ctx.send(
                        "You're the Guild Master and you want to run away from "
                        + f"your responsibilities, <@{ctx.author.id}>? "
                        + "Sorry, but NO!"
                    )
                    db_ailie.disconnect()
                    return
                else:
                    db_ailie.quit_guild(ctx.author.id)
                    await ctx.send(f"You're solo now, <@{ctx.author.id}>.")
            else:
                db_ailie.quit_guild(ctx.author.id)
                db_ailie.disband_guild(guild_id)
                await ctx.send(f"You're solo now, <@{ctx.author.id}>.")

        else:
            await ctx.send(
                "Can't quit a Guild when you don't even have one, "
                + f"<@{ctx.author.id}>."
            )

        db_ailie.disconnect()

    @commands.command(name="promote", help="Change members' position.")
    async def promote(self, ctx, member: discord.Member, *position):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        # Initialize variables
        position = " ".join(position)
        position = position.title()

        # Check if author has a guild
        if db_ailie.is_guildless(ctx.author.id):
            await ctx.send(f"You're not even in a Guild, <@{ctx.author.id}>!")
            db_ailie.disconnect()
            return

        # Check if author is Guild Master
        guild_id = db_ailie.get_guild_id_of_member(ctx.author.id)
        guild_master = db_ailie.get_guild_master(guild_id)
        if ctx.author.id != guild_master:
            await ctx.send(
                "You're not privileged to change positions of "
                + f"other members, <@{ctx.author.id}>."
            )
            db_ailie.disconnect()
            return

        # Abort command upon changing own position
        if guild_master == member.id:
            await ctx.send(
                f"Can't change your own position, <@{ctx.author.id}>!"
            )
            db_ailie.disconnect()
            return

        # Check position
        if position.lower() not in ["guild master", "elder", "member"]:
            await ctx.send(
                "The position you entered is invalid. For now, only "
                + "Guild Master, Elder, and Member is available."
            )
            db_ailie.disconnect()
            return
        else:
            # Check if in the same guild
            guardian_one = db_ailie.get_guild_id_of_member(member.id)
            guardian_two = db_ailie.get_guild_id_of_member(ctx.author.id)
            if guardian_one == guardian_two:
                if position.lower() == "guild master":
                    # Ask for confirmation to change Guild Master
                    await ctx.send(
                        "Are you sure you want to transfer "
                        + f"Guild Master to {member}? Reply with "
                        + "`Y` or `N` to confirm."
                    )

                    # Function to confirm promotion to Guild Master
                    def confirm_application(message):
                        return (
                            message.author.id == ctx.author.id
                            and message.content.upper()
                            in ["YES", "Y", "NO", "N"]
                        )

                    try:
                        msg = await self.bot.wait_for(
                            "message", check=confirm_application, timeout=30
                        )
                        if msg.content.upper() in ["YES", "Y"]:
                            await ctx.send(
                                "Transferring Guild Master position now.."
                            )
                            db_ailie.change_position(guild_master, "Member")
                            db_ailie.change_position(member.id, position)
                            await ctx.send(
                                f"Changed position of {member} to {position}."
                            )
                        else:
                            await ctx.send("Aborting Guild Master transfer!")
                    except Exception:
                        await ctx.send("Timeout!")
                        db_ailie.disconnect()
                        return
                else:
                    db_ailie.change_position(member.id, position)
                    await ctx.send(
                        f"Changed position of {member} to {position}."
                    )
            else:
                await ctx.send(
                    "Do it again. But mention someone in your Guild!"
                )

        db_ailie.disconnect()

    @commands.command(
        name="members", help="List Guild members.", aliases=["member"]
    )
    async def members(self, ctx):
        # Check if user is initialized first
        db_ailie = DatabaseAilie()
        if not db_ailie.is_initialized(ctx.author.id):
            await ctx.send(
                "Do `ailie;initialize` or `a;initialize` first before anything!"
            )
            db_ailie.disconnect()
            return

        if not db_ailie.is_guildless(ctx.author.id):
            # Get guild name to present in output
            guild_name = db_ailie.get_guild_name_of_member(ctx.author.id)
            members_output = []

            # Get all the members
            members = db_ailie.get_members_list(ctx.author.id)
            structured_member = ""
            counter = 1
            for member in members:
                structured_member = structured_member + f"{counter}. "
                structured_member = (
                    structured_member + f"`{self.bot.get_user(member[0])}` "
                )
                if member[1] is not None:
                    structured_member = (
                        structured_member + f" a.k.a. `{member[1]}` "
                    )
                structured_member = structured_member + f"({member[2]})"
                members_output.append(structured_member)
                structured_member = ""
                counter += 1

            # Finally send the list
            embed = discord.Embed(
                color=discord.Color.purple(),
            )
            embed.set_author(icon_url=self.bot.user.avatar_url, name="Ailie")
            embed.add_field(
                name=f"**{guild_name}'s Members**",
                value="\n".join(members_output),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                "You can't list your Guild members if you're "
                + f"not in a Guild, <@{ctx.author.id}>."
            )

        db_ailie.disconnect()


def setup(bot):
    bot.add_cog(Guild(bot))
