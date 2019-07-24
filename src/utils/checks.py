import discord

async def is_admin(bot, ctx):
	roles = ctx.author.roles
	admin_main = ctx.guild.get_role(bot.data.roles["admin_main"])
	admin_management = ctx.guild.get_role(bot.data.roles["admin_management"])
	return admin_main in roles or admin_management in roles