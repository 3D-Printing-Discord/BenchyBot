
import discord
from discord.ext import commands
import json
import random
import asyncio
import bot_utils

class Magic8(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def fortune(self, ctx):

        embed = discord.Embed(title="Fortune Cookie", description="Lets find out your fortune!")
        message = await ctx.send(embed=embed)

        await asyncio.sleep(2)

        embed = discord.Embed(title="Fortune Cookie", description="Unwrapping the cookie...")
        await message.edit(embed=embed)

        await asyncio.sleep(5)

        f = open("modules/8Ball/fortune.txt", "r")
        responses = f.readlines()
        f.close()

        answer = random.choice(responses).strip()

        embed = discord.Embed(title="Fortune Cookie", description=answer)
        await message.edit(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def magic8(self, ctx):
        embed = discord.Embed(title="Lets find out!", description="Shaking proverbial magic eight Ball...")
        message = await ctx.send(embed=embed)

        await asyncio.sleep(5)

        f = open("modules/8Ball/responses.txt", "r")
        responses = f.readlines()
        f.close()

        # print(responses)

        answer = random.choice(responses).strip()

        colour = bot_utils.yellow
        if answer[0] == 'y':
            colour = bot_utils.green
        if answer[0] == 'm':
            colour = bot_utils.yellow
        if answer[0] == 'n':
            colour = bot_utils.red

        output_string = f"{ctx.author.mention}: {answer[1:]}"
        embed = discord.Embed(title="The eight ball says...", description=output_string, color=colour)
        await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(Magic8(bot))