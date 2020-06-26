
import discord
from discord.ext import commands
import json
import random

class GoodBot(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/GoodBot/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if "good bot" in message.content.lower():

            await message.channel.send(self.config_data['good_bot'][random.randint(0, len(self.config_data['good_bot'])-1)])

        if "bad bot" in message.content.lower():

            await message.channel.send(self.config_data['bad_bot'][random.randint(0, len(self.config_data['bad_bot'])-1)])

def setup(bot):
    bot.add_cog(GoodBot(bot))