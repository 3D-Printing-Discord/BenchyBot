
import discord
from discord.ext import commands
import json
import asyncio
import random
import bot_utils

class Yeet(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        # self.config_data = []
        # with open('modules/Yeet/config.json') as f:
        #     self.config_data = json.load(f)

        self.yeets = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 730178093444104272:
            if "yeet" in message.content.lower() and message.author.id != self.bot.user.id:
                await message.add_reaction(":yeet:730210956793086034")
                # await message.channel.send("Thats a yeet!")
                self.yeets = self.yeets + 1

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def yeet(self, ctx):
        '''
        Shows yeet count.
        '''
        
        await ctx.send(f"Thats {self.yeets} yeets!")

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def unyeet(self, ctx):
        '''
        Resets Yeet count.
        '''
        await ctx.send(f"Thats {self.yeets} yeets set back to 0 yeets all thanks to {ctx.author.name}!")
        self.yeets = 0


def setup(bot):
    bot.add_cog(Yeet(bot))