import discord
import re

async def get_member(bot, argument):

    # Modified from the version found in the discord.py source

    def _get_from_guilds(bot, getter, argument):
        result = None
        for guild in bot.guilds:
            result = getattr(guild, getter)(argument)
            if result:
                return result
        return result

    guild = bot.get_guild(bot.data.guilds["main"])

    match = re.match(r'([0-9]{15,21})$', argument) or re.match(r'<@!?([0-9]+)>$', argument)
    
    if match is None:
        if guild:
            return guild.get_member_named(argument)
        else:
            return _get_from_guilds(bot, 'get_member_named', argument)
    else:
        user_id = int(match.group(1))
        if guild:
            return  guild.get_member(user_id)
        else:
            return _get_from_guilds(bot, 'get_member', user_id)