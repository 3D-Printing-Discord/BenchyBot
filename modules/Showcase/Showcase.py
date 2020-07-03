
import discord
from discord.ext import commands
import json
import bot_utils
import random

class Showcase(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.whitelist = [
            'youtube.com',
            'thingiverse.com',
            'imgur.com'
        ]

        self.reacts = ['👍', '❤️', '🆒', '💯', '🔥']

        self.config_data = []
        with open('modules/Showcase/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.config_data['showcase_channels']:
            if message.author.top_role.id in bot_utils.admin_roles:
                return
            if message.attachments or any(True for term in self.whitelist if term in message.content):
                await message.add_reaction(random.choice(self.reacts))

            else:
                await message.author.send(self.config_data['showcase_message'])
                await message.delete()

def setup(bot):
    bot.add_cog(Showcase(bot))