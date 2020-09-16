
import discord
from discord.ext import commands
import json

class LinkScanner(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/LinkScanner/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, reaction, user):
        

    @commands.command()
    async def Command(self, ctx):

def setup(bot):
    bot.add_cog(LinkScanner(bot))