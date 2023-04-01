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
        
        actions = {'remove': self.flairbot.remove_post_for_no_sauce, 'comment': self.flairbot.comment_no_sauce, 'none': self.__none}

        self.no_sauce_action = actions[self.config['action']]
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

    @commands.command(aliases=['fstatus', 'fs'])
    @can_use_flair()
    async def flairing_status(self, ctx):
        response = ''
        async with ctx.typing():
            for key, task in {'flairing': self.flairing, 'collecting':self.collecting_post, 'no_sauce_hook':self.no_sauce_hook}.items():
                if task:
                    response = f'{response}\n{key}: {"inactive" if task.done() else "active"}'
                else:
                    response = f'{response}\n{key}: inactive'
            response = f'{response}\naction: {self.config["action"]}'
            await ctx.send(response)

    @commands.command()
    @can_use_flair()
    async def initiate_flairing(self, ctx):
        async with ctx.typing():
            self.config['flairing_on'] = True
            self.save_config()
            await self.__stop_flairing()
            await self.__initiate_flairing()
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

    @commands.command()
    @can_use_flair()
    async def activate_commenting(self, ctx):
        async with ctx.typing():
            await self.__stop_flairing()
            self.no_sauce_action = self.flairbot.comment_no_sauce
            self.config['action'] = 'comment'
            self.save_config()
            await self.__initiate_flairing()
            await ctx.send('commenting on posts without sauce is active')

    @commands.command()
    @can_use_flair()
    async def activate_removing(self, ctx):
        async with ctx.typing():
            await self.__stop_flairing()
            self.no_sauce_action = self.flairbot.remove_post_for_no_sauce
            self.config['action'] = 'remove'
            self.save_config()
            await self.__initiate_flairing()
            await ctx.send('removing posts without sauce is active')

    @commands.command()
    @can_use_flair()
    async def no_action(self, ctx):
        async with ctx.typing():
            await self.__stop_flairing()
            self.no_sauce_action = self.__none
            self.config['action'] = 'none'
            self.save_config()
            await self.__initiate_flairing()
            await ctx.send('no action is active')

    async def __stop_flairing(self):
        for task in (self.flairing, self.collecting_post, self.no_sauce_hook):
            if task:
                if not task.done():
                    task.cancel()

    async def __none(self, *_):
        return

    async def __initiate_flairing(self):
        if self.config['flairing_on']:
            self.flairing = asyncio.create_task(self.flairbot.flairer.flairing())
        self.collecting_post = asyncio.create_task(self.flairbot.collect_posts())
        self.no_sauce_hook = asyncio.create_task(self.flairbot.no_sauce_hook(self.no_sauce_action, spoiler=self.no_sauce_spoiler))
        asyncio.create_task(self.restartor(self.flairing))
        asyncio.create_task(self.restartor(self.collecting_post))
        asyncio.create_task(self.restartor(self.no_sauce_hook))
        
    async def restartor(self, task):
        try:
            await task
        finally:
            await self.__stop_flairing()
            await self.__initiate_flairing()


    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

async def setup(bot):
    await bot.add_cog(await get_super_flair(bot))
