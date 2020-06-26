
import discord
from discord.ext import commands
import json
import bot_utils

class Showcase(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Showcase/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.config_data['showcase_channels']:
            if not message.attachments:
                await bot_utils.bot_log(self.bot, f"{message.content} by {message.author} was removed from a showcase channel.")
                await message.author.send(self.config_data['showcase_message'])
                await message.delete()

def setup(bot):
    bot.add_cog(Showcase(bot))