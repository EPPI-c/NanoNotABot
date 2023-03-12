import json
import asyncio

import superflair

from discord.ext import commands

CONFIG_FILE = 'superflair.json'

async def get_super_flair(bot:commands.Bot):
    super_flair = Super_Flair(bot)
    await super_flair.init_async()
    return super_flair

def can_use_flair():
    with open(CONFIG_FILE) as f: config = json.load(f)
    async def predicate(ctx):
        return ctx.guild.id in config['allowed_guilds']
    return commands.check(predicate)

class Super_Flair(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.flairbot = superflair.FlairBot()
        with open(CONFIG_FILE) as f:
            self.config = json.load(f)

        self.no_sauce_action = self.flairbot.comment_no_sauce
        self.no_sauce_spoiler = self.config['no_sauce_spoiler']

        self.flairing = None
        self.collecting_post = None
        self.no_sauce_hook = None

    async def init_async(self):
        if self.config['flairing_on']:
            await self.__initiate_flairing()
    
    @commands.command()
    @commands.is_owner()
    async def allow_guild(self, ctx):
        async with ctx.typing():
            self.config['allowed_guilds'].append(ctx.guild.id)
            self.save_config()
            await ctx.send(f'allowed {ctx.guild.name} to use superflair reload required')

    @commands.command()
    @commands.is_owner()
    async def disallow_guild(self, ctx):
        async with ctx.typing():
            self.config['allowed_guilds'].remove(ctx.guild.id)
            self.save_config()
            await ctx.send(f'disallowed {ctx.guild.name} to use superflair reload required')

    @commands.command()
    @can_use_flair()
    async def initiate_flairing(self, ctx):
        async with ctx.typing():
            await self.__stop_flairing()
            await self.__initiate_flairing()
            self.config['flairing_on'] = True
            self.save_config()
            await ctx.send("I activated flairing")

    @commands.command()
    @can_use_flair()
    async def stop_flairing(self, ctx):
        async with ctx.typing():
            await self.__stop_flairing()
            self.config['flairing_on'] = False
            self.save_config()
            await ctx.send("I stopped flairing")

    @commands.command()
    @can_use_flair()
    async def switch_no_sauce_spoiler(self, ctx):
        'if True removes unsauced spoilered posts using flairbot'
        async with ctx.typing():
            self.config['no_sauce_spoiler'] = not self.config['no_sauce_spoiler'] 
            self.save_config()
            await self.__stop_flairing()
            await self.__initiate_flairing()
            await ctx.send(f'spoiler mode is now {self.config["no_sauce_spoiler"]}')

    async def __stop_flairing(self):
        for task in (self.flairing, self.collecting_post, self.no_sauce_hook):
            if task:
                if not task.done():
                    task.cancel()

    async def __initiate_flairing(self):
        self.flairing = asyncio.create_task(self.flairbot.flairer.flairing())
        self.collecting_post = asyncio.create_task(self.flairbot.collect_posts())
        self.no_sauce_hook = asyncio.create_task(self.flairbot.no_sauce_hook(self.no_sauce_action, spoiler=self.no_sauce_spoiler))

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

async def setup(bot):
    await bot.add_cog(await get_super_flair(bot))
