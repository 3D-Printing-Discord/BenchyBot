
import discord
from discord.ext import commands
import json
import bot_utils 
import re
from urllib.parse import urlparse

class LinkScanner(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/LinkScanner/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 339978089411117076:
            return

        if self.get_links(message.content) is not None:
            with open('modules/LinkScanner/lists/porn.txt') as porn:
                if any([i.strip() in message.content.lower() for i in porn.readlines()]):
                    await message.delete()
                    await bot_utils.log(self.bot, title="Banned Site Removed", color=bot_utils.red, From=f"{message.author.mention} [{message.author}]", Message=f"```{message.content[:1000]}```")

    def get_domain(self, url):
        return urlparse(url).netloc

    def get_links(self, message):
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)

def setup(bot):
    bot.add_cog(LinkScanner(bot))