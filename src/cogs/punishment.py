import discord
from discord.ext import commands

import asyncio
import datetime
from pytimeparse import parse as parse_time

from utils import get_member, log, error, success, EmbedColor

class Punishment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.mute_check())
        self.mutes = []


    async def cog_check(self, ctx):
        roles = ctx.author.roles
        admin_main = ctx.guild.get_role(self.bot.data.roles["admin_main"])
        admin_management = ctx.guild.get_role(self.bot.data.roles["admin_management"])
        return admin_main in roles or admin_management in roles


    async def mute_check(self):
        mute_role = self.bot.get_guild(self.bot.data.guilds["main"]).get_role(self.bot.data.roles["muted"])

        while True:
            finished_mutes = []
            for index, (member, start_time, time_period, reason) in enumerate(self.mutes):
                if (datetime.datetime.now() - start_time).seconds > time_period:
                    finished_mutes.append(index)
                else:
                    await member.add_roles(mute_role)

            for index in finished_mutes:
                member, _, _, _ = self.mutes.pop(index)
                await member.remove_roles(mute_role)
                log_data = {
                    "unmuted": str(member),
                    "unmuted by": "SherlockBones",
                    "reason": "automatic unmute",
                    "timestamp": datetime.datetime.now().isoformat()
                }

                await log(self.bot, log_data, "mute_log", EmbedColor.green)

                desc = f"You have been **unmuted** in the Speedrunners discord server"
                embed = discord.Embed(description=desc, color=EmbedColor.dark_green)
                await member.send(embed=embed)

            await asyncio.sleep(5)


    async def moderate(self, ctx, member_descriptor, reason, word, logname, color, callback, check=None):
        member = await get_member(self.bot, member_descriptor)
        if not member:
            await ctx.send(embed=await error(f"No member found by descriptor '{member_descriptor}'"))
            return
        reason = " ".join(reason)

        if check:
            if not await check(member):
                return

        await callback(member)

        log_data = {
            f"{word}": str(member),
            f"{word} by": ctx.author.name,
            "reason": reason,
            "timestamp": datetime.datetime.now().isoformat()
        }

        await log(ctx.bot, log_data, logname, color)

        if reason:
            desc = f"You have been **{word}** in the Speedrunners discord server for the following reason:\n```{reason}```"
        else:
            desc = f"You have been **{word}** in the Speedrunners discord server"
        embed = discord.Embed(description=desc, color=EmbedColor.dark_green)
        await member.send(embed=embed)

        await ctx.send(embed=await success(f"Successfully {word} {str(member)}"))


    @commands.command()
    async def warn(self, ctx, member, *reason):
        async def callback(member):
            pass
        await self.moderate(ctx, member, reason, "warned", "warn_log", EmbedColor.orange, callback)


    @commands.command()
    async def mute(self, ctx, member_descriptor, time_descriptor, *reason):
        member = await get_member(self.bot, member_descriptor)
        if not member:
            await ctx.send(embed=await error(f"No member found by descriptor '{member_descriptor}'"))
            return

        n_seconds = parse_time(time_descriptor)
        if not n_seconds:
            await ctx.send(embed=await error(f"Unknown time period '{time_descriptor}'"))
            return

        reason = " ".join(reason)

        log_data = {
            "muted": str(member),
            "muted by": str(ctx.author),
            "muted for": str(datetime.timedelta(seconds=n_seconds)),
            "reason": reason,
            "timestamp": datetime.datetime.now().isoformat()
        }
        await log(self.bot, log_data, "mute_log", EmbedColor.orange)

        self.mutes.append((member, datetime.datetime.now(), n_seconds, reason))

        if reason:
            desc = f"You have been **muted** in the Speedrunners discord server for the following reason:\n```{reason}```"
        else:
            desc = f"You have been **muted** in the Speedrunners discord server"
        embed = discord.Embed(description=desc, color=EmbedColor.dark_green)
        await member.send(embed=embed)

        await ctx.send(embed=await success(f"Successfully muted {str(member)} for {str(datetime.timedelta(seconds=n_seconds))}"))


    @commands.command()
    async def unmute(self, ctx, member, *reason):
        async def callback(member):
            mute_role = self.bot.get_guild(self.bot.data.guilds["main"]).get_role(self.bot.data.roles["muted"])
            remove_indices = []
            for index, (muted_member, start_time, time_period, reason) in enumerate(self.mutes):
                if member == muted_member:
                    remove_indices.append(index)
                    await member.remove_roles(mute_role)

            for index in remove_indices:
                self.mutes.pop(index)

        async def check(member):
            for index, (muted_member, start_time, time_period, reason) in enumerate(self.mutes):
                if member == muted_member:
                    return True
            await ctx.send(embed=await error(f"{str(member)} is not currently muted"))
            return False

        await self.moderate(ctx, member, reason, "unmuted", "mute_log", EmbedColor.green, callback, check)


    @commands.command()
    async def kick(self, ctx, member, *reason):
        async def callback(member):
            await ctx.guild.kick(member)
        await self.moderate(ctx, member, reason, "kicked", "kick_log", EmbedColor.orange, callback)


    @commands.command()
    async def ban(self, ctx, member, *reason):
        async def callback(member):
            await ctx.guild.ban(member)
        await self.moderate(ctx, member, reason, "banned", "ban_log", EmbedColor.red, callback)


    @commands.command()
    async def unban(self, ctx, member, *reason):
        async def callback(member):
            await ctx.guild.unban(member)
        async def check(member):
            bans = await ctx.guild.bans()
            if member in [be[0] for be in bans]:
                return True
            else:
                ctx.send(embed=await error(f"{str(member)} is not currently banned"))
                return False

        await self.moderate(ctx, member, reason, "unbanned", "ban_log", EmbedColor.green, callback, check)


    @commands.command()
    async def purge(self, ctx, n_messages):
        try:
            n_messages = int(n_messages)
        except ValueError:
            await ctx.send(embed=await error(f"Invalid number of messages '{n_messages}'"))
            return
        if not (0 < n_messages <= 100):
            await ctx.send(embed=await error(f"Number of messages must be 0-100"))
            return
        await ctx.channel.purge(limit=n_messages+1)

        log_data = {
            "channel": ctx.channel.name,
            "purged by": str(ctx.author),
            "number": str(n_messages),
            "timestamp": datetime.datetime.now().isoformat()
        }
        await log(self.bot, log_data, "delete_log", EmbedColor.red)

        await ctx.send(embed=await success(f"Successfully purged {n_messages} messages"))


def setup(bot):
    bot.add_cog(Punishment(bot))
