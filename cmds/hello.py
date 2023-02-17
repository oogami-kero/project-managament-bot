import discord
from discord.ext import commands

@commands.hybrid_command(name = 'hello', with_app_command = True, description = "A welcoming message!")
async def hello(message):
    await message.send(f'Hello {message.author.display_name}!')


async def setup(bot):
    bot.add_command(hello)