#!/usr/local/bin/python
import os
import discord
from discord.ext import commands

description = '''eppi\'s bot for random stuff'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=os.environ['COMMAND_PREFIX'], description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.load_extension('super_flair')
    await bot.load_extension("rank")


@bot.command()
@commands.is_owner()
async def reload(ctx):
    async with ctx.typing():
        await bot.reload_extension("rank")
        await bot.reload_extension("super_flair")
        await ctx.send('modules loaded')

token = os.environ['DISCORD_TOKEN']

bot.run(token)
