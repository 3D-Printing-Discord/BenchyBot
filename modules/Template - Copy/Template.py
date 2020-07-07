
import discord
from discord.ext import commands
import json

class Template(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Template/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def event(self, reaction, user):

    @commands.command()
    async def Command(self, ctx):

def setup(bot):
    bot.add_cog(Template(bot))