import discord


class EmbedColor:
    red = 0xCC0000
    orange = 0xFFA500
    green = 0x00CC00
    dark_green = 0x506600


async def error(message):
    return discord.Embed(description=f":x: Error: {message}", color=EmbedColor.red)


async def success(message):
    return discord.Embed(description=f":white_check_mark: {message}", color=EmbedColor.green)