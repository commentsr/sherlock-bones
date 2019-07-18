import discord
import os
import json


async def log(bot, data, logname, color):
	with open(os.path.join(bot.root_dir, "logs", logname), "a+") as file:
		file.write(json.dumps(data)+"\n")

	desc = []
	for key, value in data.items():
		desc.append(f"**{key}**: {value}")

	embed = discord.Embed(description="\n".join(desc), color=color)

	await bot.get_channel(bot.data.channels[logname]).send(embed=embed)