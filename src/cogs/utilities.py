import discord
from discord.ext import commands

import datetime
import itertools

from utils import get_member, log, error, success, EmbedColor, read_logs

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def cog_check(self, ctx):
        roles = ctx.author.roles
        admin_main = ctx.guild.get_role(self.bot.data.roles["admin_main"])
        admin_management = ctx.guild.get_role(self.bot.data.roles["admin_management"])
        return admin_main in roles or admin_management in roles


    @commands.command()
    async def history(self, ctx, member_descriptor, page=None):
        member = await get_member(self.bot, member_descriptor)
        if not member:
            await ctx.send(embed=await error(f"No member found by descriptor '{member_descriptor}'"))
            return

        if page == None: page = 1

        try:
            page = int(page)
        except (ValueError, TypeError):
            await ctx.send(embed=await error(f"Invalid page number '{page}'"))
            return

        logs = read_logs(self.bot)

        events = []

        for event in itertools.chain(
            logs["warn_log"],
            logs["mute_log"],
            logs["kick_log"],
            logs["ban_log"]):
            if int(list(event.keys())[0]) == member.id:
                event_details = event[str(member.id)]
                valid_logs = ("warned", "muted", "kicked", "banned")
                valid_keys = [key for key in event_details.keys() if key in valid_logs]
                if valid_keys:
                    events.append((valid_keys[0], event_details))

        events = [events[i:i+10] for i in range(0, len(events), 10)]

        embed = discord.Embed(color=EmbedColor.dark_green)

        if not events:
            embed.description = "No logged data"
            events = [None]

        else:
            if not 0 < page <= len(events):
                await ctx.send(embed=await error(f"Invalid page number '{page}', must be 1-{len(events)}"))
                return
            for event in events[page-1]:
                name = event[0]
                value = event[1]["reason"]
                if not value:
                    value = u"\u200b"
                embed.add_field(name=name, value=value, inline=False)

        embed.set_author(name=f"{member.name}'s moderation history", icon_url=member.avatar_url)
        embed.set_footer(text=f"Page {page}/{len(events)}")

        await ctx.send(embed=embed)


    @commands.command()
    async def purge(self, ctx, n_messages):
        try:
            n_messages = int(n_messages)
        except ValueError:
            await ctx.send(embed=await error(f"Invalid number of messages '{n_messages}'"))
            return
        if not (0 < n_messages <= 100):
            await ctx.send(embed=await error(f"Invalid number of messages '{n_messages}', must be 1-100"))
            return
        await ctx.channel.purge(limit=n_messages+1)

        log_data = {
            "channel": ctx.channel.name,
            "purged by": str(ctx.author),
            "number": str(n_messages),
            "timestamp": datetime.datetime.now().isoformat()
        }
        await log(self.bot, ctx.author.id, log_data, "delete_log", EmbedColor.red)

        await ctx.send(embed=await success(f"Successfully purged {n_messages} messages"))


def setup(bot):
    bot.add_cog(Utilities(bot))