#!/usr/bin/env python

import discord
from discord.ext import commands


# Subclassing MinimalHelpCommand to create custom help command
class Help(commands.MinimalHelpCommand):
    # Send the help pages
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(
                color=discord.Color.purple(), description=page
            )
            embed.set_author(icon_url=self.context.me.avatar_url, name="Ailie")
            await destination.send(embed=embed)

    # Shows the main help page
    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            i = 0
            joined = ""
            for c in commands:
                better_c = "`" + c.name + "`"
                if i != 0:
                    joined = joined + ",\u2002" + better_c
                else:
                    joined = better_c
                i += 1
            self.paginator.add_line("__**%s**__" % heading)
            self.paginator.add_line(joined)

    # Shows the help page for command help pages
    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

        note = self.get_ending_note()
        if note:
            self.paginator.add_line(note)

    # Cog or Category command help page
    def add_subcommand_formatting(self, command):
        fmt = "`{0}{1}` \N{EN DASH} `{2}`" if command.short_doc else "`{0}{1}`"
        self.paginator.add_line(
            fmt.format(
                self.clean_prefix, command.qualified_name, command.short_doc
            )
        )

    # Command signature
    def get_command_signature(self, command):
        return (
            f"`{self.clean_prefix}{command.qualified_name}` "
            + f"`{command.signature}`"
        )

    # Get opening note
    def get_opening_note(self):
        command_name = self.invoked_with
        return (
            "`ailie;` or `a;` for invoking bot."
            + f"\n`{self.clean_prefix}{command_name} [command]` for "
            + "more info on a command."
            + f"\n`{self.clean_prefix}{command_name} [category]` for "
            + "more info on a category."
        )

    # Get ending note
    def get_ending_note(self):
        return (
            "For issues, feedback, or inquiry, "
            + "visit https://github.com/riazufila/ailie."
        )
