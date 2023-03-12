#!/usr/local/bin/python
import discord
from discord.ext import commands
import json
import time
import asyncpraw
import sqlite3
import re

description = '''eppi\'s bot for random stuff'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='.', description=description, intents=intents)

onetoten = ('1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟')
ranking = []
flairbot_on = False

def get_reddit_ids(link: str):
    if 'reddit.com' in link:
        return link.split('/')[6]
    elif 'redd.it' in link:
        return link.split('/')[3]
    else:
        return link

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.load_extension('coperoom')
    await bot.load_extension('super_flair')


@bot.command()
@commands.is_owner()
async def reload(ctx):
    async with ctx.typing():
        await bot.reload_extension("coperoom")
        await bot.reload_extension("super_flair")
        await ctx.send('modules loaded')
#
# @bot.command()
# async def his(ctx, amount:int):
#     global ranking
#     async with ctx.typing():
#         messages = ctx.channel.history(limit=amount)
#         ranking = [m async for m in messages if m.content.startswith('.| ')]

# @bot.command(name='|')
# async def entry(ctx):
#     ranking.append(ctx.message)
#     for e in onetoten:
#         await ctx.message.add_reaction(e)

# @bot.command()
# async def show(ctx):
#     global ranking
#     ra = []
#     start = time.time()
#     async with ctx.typing():
#         for msg in ranking:
#             await retrieve_reactions(ra, msg)
#         ra.sort(key=lambda x: x['mean'], reverse=True)
#         for a in ra:
#             await a['msg'].channel.send(f'{a["msg"].content}: {a["mean"]}')
#     end = time.time()
#     print(end-start)

# @bot.command()
# async def list(_):
#     global ranking
#     print(ranking)

# async def retrieve_reactions(ra, msg):
#     mean = 0
#     total = 0
#     for r in msg.reactions:
#         score = onetoten.index(r.emoji) + 1
#         total += r.count-1
#         mean += score*(r.count - 1)
#     if total:
#         mean = mean/total
#         ra.append({'msg':msg, 'mean':mean})

@bot.command(aliases=['t'])
async def top250(ctx, post:str=commands.parameter(description=': Wholesome Animemes post link or id')):
    '''checks if post is in the top 250 posts of wholesomeanimemes'''
    async with ctx.typing():
        post = get_reddit_ids(post)
        sub = 'wholesomeanimemes'
        reddit = asyncpraw.Reddit('iiep')
        subreddit = await reddit.subreddit(sub)
        async for p in subreddit.top(limit=250):
            if p.id == post:
                post = p.title
                n = ''
                break
        else:
            n = 'not '
        await ctx.send(f'post "{post}" is {n}in top 250, {ctx.message.author.name}-san')
        await reddit.close()

with open('../credentials.json', 'r') as f:
    token = json.load(f)['discord_token']


bot.run(token)
