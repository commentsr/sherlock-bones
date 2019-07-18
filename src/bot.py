import discord
import discord.ext.commands as commands

from utils import read_data

import json
import os

bot = commands.Bot("")
setattr(bot, "root_dir", os.path.dirname(os.getcwd()))
setattr(bot, "data", read_data(bot))


@bot.listen()
async def on_ready():
	bot.command_prefix = bot.data.metadata["command_prefix"]

	for cog in bot.data.cogs:
		bot.load_extension(f"cogs.{cog}")

	print(f"Logged in as {str(bot.user)}!")


bot.run(bot.data.metadata["token"])