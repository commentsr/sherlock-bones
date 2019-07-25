import discord
from discord.ext import commands

import datetime
import itertools

from utils import get_member, log, error, success, EmbedColor, read_logs, is_admin

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="commands")
    async def _commands(self, ctx):
        description = "A list of available commands. Some may be admin only.\nUse `help <command>` for more info about a command"
        embed = discord.Embed(title="Commands", description=description, color=EmbedColor.dark_green)
        for category, category_data in self.bot.data.command_metadata.items():
            title = category
            value = []
            for command, command_info in category_data.items():
                args = []
                for argument, argument_info in command_info["arguments"].items():
                    if argument_info["required"]:
                        args.append(f"<{argument}>")
                    else:
                        args.append(f"[{argument}]")
                value.append(command + " " + " ".join(args))
            embed.add_field(name=title, value="\n".join(value), inline=False)
        await ctx.send(embed=embed)


    @commands.command()
    async def help(self, ctx, command_name=None):
        if command_name == None:
            description = "Usage:\n```help <command>```"
            description += "\nYou can also use the `commands` command to view the commands list"
            embed = discord.Embed(title="Help", description=description, color=EmbedColor.dark_green)
            await ctx.send(embed=embed)
        else:
            command_info = None
            for category, category_data in self.bot.data.command_metadata.items():
                for command, _command_info in category_data.items():
                    if command_name == command:
                        command_info = _command_info

            if not command_info:
                await ctx.send(embed=await error(f"Unknwn command '{command_name}'"))
                return

            description = command_info["description"]

            if command_info["requires_admin"]:
                description += "\nThis command is admin only"
            args = []
            for argument, argument_info in command_info["arguments"].items():
                if argument_info["required"]:
                    args.append(f"<{argument}>")
                else:
                    args.append(f"[{argument}]")
            description += "\nUsage:"
            description += "```" + command_name + " " + " ".join(args) + "```"

            embed = discord.Embed(title=command_name, description=description, color=EmbedColor.dark_green)

            for argument, argument_info in command_info["arguments"].items():
                description = argument_info["description"]
                if argument_info["required"]:
                    description += "\nThis argument is requred"
                else:
                    description += "\nThis argument is optional"
                    if argument_info["default"]:
                        description += f". The default value is {argument_info['default']}"

                embed.add_field(name=argument, value=description, inline=False)

            await ctx.send(embed=embed)


    @commands.command()
    async def online(self, ctx):
        guild = self.bot.get_guild(self.bot.data.guilds["main"])
        member_count = guild.member_count
        status_count = [0, 0, 0, 0, 0]  # online, offline, idle, dnd, invisible
        status_list = list(discord.Status)
        for member in guild.members:
            status_count[status_list.index(member.status)] += 1

        stats = discord.Embed(color=EmbedColor.dark_green)
        stats.add_field(name=f"Total: {member_count}", value="\n".join([
            f"<:online:572884944813031434>{status_count[0]}",
            f"<:idle:572884943898673174>{status_count[2]}",
            f"<:do_not_disturb:572884944016113666>{status_count[3]}",
            f"<:offline:572884944343269378>{status_count[1] + status_count[4]}"]))
        await ctx.send(embed=stats)


    @commands.command()
    async def ping(self, ctx):
        await ctx.send(embed=await success(f"Pong! ({round(self.bot.latency, 3) * 1000}ms)"))


    @commands.command()
    async def rule(self, ctx, number=None):
        async def _error():
            await ctx.send(embed=await error(f"Invalid rule number '{number}', must be 1-{len(self.bot.data.rules.keys())}"))

        if number == None:
            await _error()
            return
        try:
            number = int(number)
        except (ValueError, TypeError):
            await _error()
            return
        if not 0 < number < len(self.bot.data.rules.keys())+1: 
            await _error()
            return

        rule = self.bot.data.rules[str(number)]
        title = f"Rule {number} - {rule['title']}"
        description = "\n".join(rule['description']) or u"\u200b"
        embed = discord.Embed(title=title, description=description, color=EmbedColor.dark_green)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(User(bot))