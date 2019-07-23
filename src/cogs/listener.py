import discord
from discord.ext import commands

import datetime

from utils import log, EmbedColor

class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
    	if after.guild != self.bot.get_guild(self.bot.data.guilds["main"]):
    		return
    	if after.content == before.content:
    		return
    	log_data = {
    		"message ID": after.id,
    		"sent by": str(after.author),
    		"channel": after.channel.name,
    		"before": before.clean_content,
    		"after": after.clean_content,
    		"timestamp": datetime.datetime.now().isoformat()
    	}
    	await log(self.bot, after.author.id, log_data, "edit_log", EmbedColor.orange)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
    	if message.guild != self.bot.get_guild(self.bot.data.guilds["main"]):
    		return
    	log_data = {
    		"message ID": message.id,
    		"sent by": str(message.author),
    		"channel": message.channel.name,
    		"message": message.clean_content,
    		"timestamp": datetime.datetime.now().isoformat()
    	}
    	await log(self.bot, message.author.id, log_data, "delete_log", EmbedColor.red)


def setup(bot):
    bot.add_cog(Listener(bot))
