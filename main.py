#!/usr/local/bin/python
import discord
from discord.ext import commands
import json

description = '''eppi\'s bot for random stuff'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='>', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.load_extension('coperoom')
    await bot.load_extension('super_flair')
    await bot.load_extension("rank")


@bot.command()
@commands.is_owner()
async def reload(ctx):
    async with ctx.typing():
        await bot.reload_extension("coperoom")
        await bot.reload_extension("rank")
        await bot.reload_extension("super_flair")
        await ctx.send('modules loaded')

with open('../credentials.json', 'r') as f:
    token = json.load(f)['discord_token']

bot.run(token)
