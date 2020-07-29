
import discord
from discord.ext import commands
import json

class Suggestions(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Suggestions/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.config_data['suggestions_channel']:
            emojis = ['👍', '👎', '🤷‍♀️']
            for i in emojis:
                await message.add_reaction(i)

def setup(bot):
    bot.add_cog(Suggestions(bot))