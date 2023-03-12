import time

from discord.ext import commands

onetoten = ('1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟')

class Rank(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.ranking = []

    @commands.command()
    async def his(self, ctx, amount:int):
        async with ctx.typing():
            messages = ctx.channel.history(limit=amount)
            self.ranking = [m async for m in messages if m.content.startswith('>>')]

    @commands.command(name='>')
    async def entry(self, ctx):
        async with ctx.typing():
            self.ranking.append(ctx.message)
            for e in onetoten:
                await ctx.message.add_reaction(e)

    @commands.command()
    async def show(self, ctx):
        async with ctx.typing():
            global ranking
            ra = []
            start = time.time()
            async with ctx.typing():
                for msg in self.ranking:
                    await self.retrieve_reactions(ra, msg)
                ra.sort(key=lambda x: x['mean'], reverse=True)
                for i, a in enumerate(ra, start=1):
                    await a['msg'].channel.send(f'{i} - {a["msg"].content.removeprefix(">>")}: {a["mean"]}')
            end = time.time()
            print(end-start)

    @commands.command()
    async def clean(self, ctx):
        async with ctx.typing():
            self.ranking = []

    async def retrieve_reactions(self, ra, msg):
        mean = 0
        total = 0
        for r in msg.reactions:
            score = onetoten.index(r.emoji) + 1
            total += r.count-1
            mean += score*(r.count - 1)
        if total:
            mean = mean/total
            ra.append({'msg':msg, 'mean':mean})

async def setup(bot):
    await bot.add_cog(Rank(bot))
