
import discord
from discord.ext import commands
import json
import random
import bot_utils
import asyncio
import d20

class Dice(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        # self.config_data = []
        # with open('modules/Dice/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def d20(self, ctx, *, d='1d6'):
        '''
        Rolls a dice using d20 syntax. Defaults to a single d6
        '''
        try:
            result = d20.roll(d)
            result = int(result)
        except d20.errors.RollSyntaxError:
            await ctx.send("Sorry, I dont recognise that dice!")
            return

        embed = discord.Embed(title=f"Dice ({d})", description="Shaking the dice!", color=bot_utils.red)
        message = await ctx.send(embed=embed)

        await asyncio.sleep(3)

        embed = discord.Embed(title=f"Dice ({d})", description=f"Result: {result}", color=bot_utils.green)
        await message.edit(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def roll(self, ctx, d='6'):
        '''
        Rolls a dice. Defaults to 1 d6
        '''

        try:
            d = int(d)
        except ValueError:
            await ctx.send("I dont recognise that die!")
            return

        embed = discord.Embed(title=f"Dice d{d}", description="Shaking the dice!", color=bot_utils.red)
        message = await ctx.send(embed=embed)

        await asyncio.sleep(3)

        embed = discord.Embed(title=f"Dice d{d}", description=f"It's a {random.randint(1,d)}", color=bot_utils.green)
        await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(Dice(bot))