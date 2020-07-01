
import discord
from discord.ext import commands
import json
import bot_utils
import random

class Showcase(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.reacts = ['👍', '❤️', '‼️', '🆒', '💯', '🔥']

        self.config_data = []
        with open('modules/Showcase/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.config_data['showcase_channels']:
            if not message.attachments:
                await message.author.send(self.config_data['showcase_message'])
                await message.delete()
            else:
                message.add_reaction(random.choice(self.reacts))

def setup(bot):
    bot.add_cog(Showcase(bot))