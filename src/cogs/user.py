import discord
from discord.ext import commands

import datetime
import itertools

from utils import get_member, log, error, success, EmbedColor, read_logs, is_admin

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


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