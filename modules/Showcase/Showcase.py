
import discord
from discord.ext import commands
import json
import bot_utils
import random
import asyncio

class Showcase(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.whitelist = [
            'youtube.com',
            'thingiverse.com',
            'imgur.com',
            'youtu.be',
            'discordapp.com/attachments'
        ]

        self.reacts = ['👍', '❤️', '🆒', '😍', '📸', '🎉', '🎊']

        self.config_data = []
        with open('modules/Showcase/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.config_data['showcase_channels']:

            if any(role.id in bot_utils.admin_roles for role in message.author.roles):
                return

            if message.attachments or any(True for term in self.whitelist if term in message.content):
                await asyncio.sleep(30)
                await message.add_reaction(random.choice(self.reacts))
            else:
                try:
                    await message.author.send(self.config_data['showcase_message'])
                except discord.errors.Forbidden:
                    print(f"[!] Couldnt Message: {message.author}")
                await message.delete()
                await message.guild.get_channel(self.bot.config['bot_log_channel']).send(f"Showcase message from {message.author} removed.\n\n```{message.content}```")

def setup(bot):
    bot.add_cog(Showcase(bot))